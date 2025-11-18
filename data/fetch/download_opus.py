#!/usr/bin/env python3
"""
OPUS Corpus Downloader (Optimized)
Downloads parallel corpus files and monolingual text files from OPUS using the API endpoint.
Optimized for high-speed concurrent downloads with progress tracking.
"""

import requests
import json
import os
import gzip
import zipfile
import argparse
from pathlib import Path
from urllib.parse import urlparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import threading
from typing import Optional, Dict, List, Tuple

# Try to import tqdm for progress bars, fallback if not available
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("⚠️  tqdm not installed. Install with: pip install tqdm for better progress bars")


def fetch_all_corpus_files(corpus: str, source_lang: str, target_lang: str) -> List[Dict]:
    """
    Fetch all available files for a corpus from OPUS API.
    
    Args:
        corpus (str): Corpus name
        source_lang (str): Source language code
        target_lang (str): Target language code
        
    Returns:
        List[Dict]: List of all available files
    """
    all_files = []
    
    try:
        # Try both language directions to find available data
        urls = [
            f"https://opus.nlpl.eu/opusapi/?corpus={corpus}&source={source_lang}&target={target_lang}&preprocessing=xml&version=latest",
            f"https://opus.nlpl.eu/opusapi/?corpus={corpus}&source={target_lang}&target={source_lang}&preprocessing=xml&version=latest"
        ]
        
        for i, url in enumerate(urls):
            try:
                print(f"  Checking API: {url}")
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                corpora_data = data.get('corpora', [])
                
                print(f"  Found {len(corpora_data)} entries")
                
                # Collect all entries
                for entry in corpora_data:
                    entry_source = entry.get('source', '')
                    entry_target = entry.get('target', '')
                    download_url = entry.get('url', '')
                    
                    if download_url:  # Only include entries with download URLs
                        file_info = {
                            'source': entry_source,
                            'target': entry_target,
                            'url': download_url,
                            'alignment_pairs': entry.get('alignment_pairs', 0),
                            'source_tokens': entry.get('source_tokens', 0),
                            'target_tokens': entry.get('target_tokens', 0),
                            'size_mb': entry.get('size', 0),
                            'version': entry.get('version', ''),
                            'file_type': 'parallel' if (entry_source and entry_target) else 'monolingual'
                        }
                        
                        # Determine file type more precisely
                        if entry_source and entry_target and entry_source != entry_target:
                            file_info['file_type'] = 'alignment'
                            file_info['description'] = f"Parallel alignment file ({entry_source}-{entry_target})"
                        elif entry_source and not entry_target:
                            file_info['file_type'] = 'monolingual'
                            file_info['description'] = f"Monolingual text file ({entry_source})"
                        elif entry_target and not entry_source:
                            file_info['file_type'] = 'monolingual'
                            file_info['description'] = f"Monolingual text file ({entry_target})"
                        else:
                            file_info['file_type'] = 'unknown'
                            file_info['description'] = "Unknown file type"
                        
                        all_files.append(file_info)
                        print(f"    📄 {file_info['description']}: {download_url}")
                
            except Exception as e:
                print(f"    Warning: Error with direction {i+1}: {e}")
                continue
        
        # Remove duplicates based on URL
        unique_files = []
        seen_urls = set()
        for file_info in all_files:
            if file_info['url'] not in seen_urls:
                unique_files.append(file_info)
                seen_urls.add(file_info['url'])
        
        return unique_files
        
    except Exception as e:
        print(f"❌ Error fetching files for {corpus}: {e}")
        return []


def download_file(url: str, output_path: str, chunk_size: int = 8192, max_retries: int = 3) -> bool:
    """
    Download a file from URL to local path with optimized performance.
    
    Args:
        url (str): Download URL
        output_path (str): Local file path
        chunk_size (int): Download chunk size
        max_retries (int): Maximum retry attempts
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Create session with connection pooling
    session = requests.Session()
    session.mount('http://', requests.adapters.HTTPAdapter(
        pool_connections=10, pool_maxsize=20, max_retries=max_retries
    ))
    session.mount('https://', requests.adapters.HTTPAdapter(
        pool_connections=10, pool_maxsize=20, max_retries=max_retries
    ))
    
    for attempt in range(max_retries + 1):
        try:
            # Create output directory if it doesn't exist
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Use stream=True for memory efficiency
            response = session.get(url, stream=True, timeout=(30, 300))  # Connect timeout, read timeout
            response.raise_for_status()
            
            # Get file size if available
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            # Create progress bar if tqdm is available
            filename = os.path.basename(output_path)
            
            if HAS_TQDM:
                with tqdm(
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    desc=f"Downloading {filename[:30]}...",
                    leave=False
                ) as pbar:
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                pbar.update(len(chunk))
            else:
                # Fallback without progress bar
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Show basic progress for large files
                            if total_size > 0 and downloaded % (chunk_size * 100) == 0:
                                progress = (downloaded / total_size) * 100
                                print(f"\r  Progress: {progress:.1f}%", end='', flush=True)
            
            print(f"  ✅ Downloaded: {filename} ({downloaded:,} bytes)")
            session.close()
            return True
            
        except Exception as e:
            if attempt < max_retries:
                print(f"  ⚠️  Attempt {attempt + 1} failed, retrying: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print(f"  ❌ Download failed after {max_retries + 1} attempts: {e}")
                session.close()
                return False
    
    session.close()
    return False


def download_file_concurrent(file_info: Dict, output_dir: str, progress_lock: Lock) -> Tuple[bool, str]:
    """
    Download a single file (for concurrent execution).
    
    Args:
        file_info (Dict): File information dictionary
        output_dir (str): Output directory
        progress_lock (Lock): Thread lock for progress updates
        
    Returns:
        Tuple[bool, str]: (success, filename)
    """
    try:
        # Generate filename
        parsed_url = urlparse(file_info['url'])
        original_filename = os.path.basename(parsed_url.path)
        
        # Create descriptive filename
        if file_info['file_type'] == 'alignment':
            filename = f"alignment_{file_info['source']}-{file_info['target']}_{original_filename}"
        elif file_info['file_type'] == 'monolingual':
            lang = file_info['source'] or file_info['target']
            filename = f"text_{lang}_{original_filename}"
        else:
            filename = f"{file_info['file_type']}_{original_filename}"
        
        output_path = os.path.join(output_dir, filename)
        
        # Download with optimized chunk size based on file size
        size_mb = file_info.get('size_mb', 0)
        chunk_size = 64*1024 if size_mb > 100 else 32*1024  # Larger chunks for bigger files
        
        success = download_file(file_info['url'], output_path, chunk_size)
        
        if success and output_path.endswith(('.gz', '.zip')):
            # Extract compressed files
            with progress_lock:
                print(f"  🔄 Extracting: {filename}")
            success = extract_compressed_file(output_path, output_dir)
        
        return success, filename
        
    except Exception as e:
        with progress_lock:
            print(f"  ❌ Error downloading {file_info.get('url', 'unknown')}: {e}")
        return False, file_info.get('url', 'unknown')


def download_files_parallel(all_files: List[Dict], output_dir: str, max_workers: int = 4) -> int:
    """
    Download multiple files concurrently.
    
    Args:
        all_files (List[Dict]): List of file information
        output_dir (str): Output directory
        max_workers (int): Maximum concurrent downloads
        
    Returns:
        int: Number of successfully downloaded files
    """
    success_count = 0
    progress_lock = Lock()
    
    print(f"📥 Starting concurrent downloads with {max_workers} workers...")
    
    # Create overall progress bar if tqdm is available
    if HAS_TQDM:
        with tqdm(total=len(all_files), desc="Overall Progress", unit="files") as overall_pbar:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all download tasks
                future_to_file = {
                    executor.submit(download_file_concurrent, file_info, output_dir, progress_lock): file_info
                    for file_info in all_files
                }
                
                # Process completed downloads
                for future in as_completed(future_to_file):
                    file_info = future_to_file[future]
                    try:
                        success, filename = future.result()
                        if success:
                            success_count += 1
                            with progress_lock:
                                print(f"  ✅ Completed: {filename}")
                        else:
                            with progress_lock:
                                print(f"  ❌ Failed: {filename}")
                    except Exception as e:
                        with progress_lock:
                            print(f"  ❌ Exception for {file_info.get('url', 'unknown')}: {e}")
                    
                    overall_pbar.update(1)
    else:
        # Fallback without overall progress bar
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all download tasks
            future_to_file = {
                executor.submit(download_file_concurrent, file_info, output_dir, progress_lock): file_info
                for file_info in all_files
            }
            
            completed = 0
            # Process completed downloads
            for future in as_completed(future_to_file):
                file_info = future_to_file[future]
                completed += 1
                try:
                    success, filename = future.result()
                    if success:
                        success_count += 1
                        with progress_lock:
                            print(f"  ✅ Completed ({completed}/{len(all_files)}): {filename}")
                    else:
                        with progress_lock:
                            print(f"  ❌ Failed ({completed}/{len(all_files)}): {filename}")
                except Exception as e:
                    with progress_lock:
                        print(f"  ❌ Exception ({completed}/{len(all_files)}) for {file_info.get('url', 'unknown')}: {e}")
    
    return success_count


def extract_compressed_file(input_path: str, output_dir: str = None) -> bool:
    """
    Extract a compressed file (gzip or zip) with optimized performance.
    
    Args:
        input_path (str): Path to compressed file
        output_dir (str): Directory for extracted files (optional)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not output_dir:
            output_dir = os.path.dirname(input_path)
        
        if input_path.endswith('.gz'):
            # Handle gzip files with buffered reading
            output_path = os.path.join(output_dir, os.path.basename(input_path).replace('.gz', ''))
            
            with gzip.open(input_path, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    # Use larger buffer for better performance
                    while True:
                        chunk = f_in.read(1024*1024)  # 1MB chunks
                        if not chunk:
                            break
                        f_out.write(chunk)
            
            os.remove(input_path)
            
        elif input_path.endswith('.zip'):
            # Handle zip files with optimization
            with zipfile.ZipFile(input_path, 'r') as zip_ref:
                # Extract all files at once
                zip_ref.extractall(output_dir)
                extracted_files = zip_ref.namelist()
            
            os.remove(input_path)
        
        return True
        
    except Exception as e:
        print(f"  ❌ Extraction failed: {e}")
        return False


def download_opus_corpus_complete(corpus: str, source_lang: str, target_lang: str, output_dir: str, 
                                file_types: List[str] = None, max_workers: int = 4) -> bool:
    """
    Download complete OPUS corpus (alignment + text files) with concurrent downloads.
    
    Args:
        corpus (str): Corpus name
        source_lang (str): Source language code
        target_lang (str): Target language code
        output_dir (str): Output directory
        file_types (List[str]): Types of files to download ('alignment', 'monolingual', 'all')
        max_workers (int): Maximum concurrent downloads
        
    Returns:
        bool: True if successful, False otherwise
    """
    if file_types is None:
        file_types = ['all']
    
    print(f"\n🔍 Searching for {corpus} corpus files ({source_lang}-{target_lang})...")
    
    # Get all available files
    all_files = fetch_all_corpus_files(corpus, source_lang, target_lang)
    
    if not all_files:
        print(f"❌ No files found for {corpus} with {source_lang}-{target_lang}")
        return False
    
    # Filter files by type if specified
    if 'all' not in file_types:
        filtered_files = []
        for file_info in all_files:
            if file_info['file_type'] in file_types:
                filtered_files.append(file_info)
        all_files = filtered_files
    
    if not all_files:
        print(f"❌ No files of specified types found: {file_types}")
        return False
    
    print(f"\n📊 Available Files:")
    total_size_mb = 0
    for i, file_info in enumerate(all_files, 1):
        size_mb = file_info['size_mb']
        total_size_mb += size_mb
        print(f"  {i}. {file_info['description']}")
        print(f"     Size: {size_mb:,} MB")
        if file_info['alignment_pairs']:
            print(f"     Pairs: {file_info['alignment_pairs']:,}")
        if file_info['source_tokens']:
            print(f"     Source tokens: {file_info['source_tokens']:,}")
        if file_info['target_tokens']:
            print(f"     Target tokens: {file_info['target_tokens']:,}")
        print()
    
    print(f"📏 Total download size: {total_size_mb:,} MB")
    
    # Create corpus-specific output directory
    corpus_dir = os.path.join(output_dir, f"{corpus}_{source_lang}-{target_lang}")
    Path(corpus_dir).mkdir(parents=True, exist_ok=True)
    
    # Start optimized concurrent downloads
    start_time = time.time()
    success_count = download_files_parallel(all_files, corpus_dir, max_workers)
    download_time = time.time() - start_time
    
    # Calculate download speed
    if download_time > 0 and total_size_mb > 0:
        speed_mbps = total_size_mb / download_time
        print(f"\n⚡ Download Speed: {speed_mbps:.2f} MB/s")
    
    print(f"\n📈 Download Summary:")
    print(f"  Successfully downloaded: {success_count}/{len(all_files)} files")
    print(f"  Download time: {download_time:.1f} seconds")
    print(f"  Output directory: {corpus_dir}")
    
    # List final files with sizes
    print(f"  Files saved:")
    total_final_size = 0
    for file_path in Path(corpus_dir).iterdir():
        if file_path.is_file():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            total_final_size += size_mb
            print(f"    📄 {file_path.name} ({size_mb:.1f} MB)")
    
    print(f"  Total extracted size: {total_final_size:.1f} MB")
    
    return success_count > 0


def main():
    """Main function for command-line interface."""
    parser = argparse.ArgumentParser(description="Download OPUS parallel corpus files (Optimized)")
    parser.add_argument("corpus", help="Corpus name (e.g., NLLB, CCMatrix, etc.)")
    parser.add_argument("--source", required=True, help="Source language code (e.g., mg)")
    parser.add_argument("--target", required=True, help="Target language code (e.g., en)")
    parser.add_argument("--output", default="./downloads", help="Output directory (default: ./downloads)")
    parser.add_argument("--types", nargs='+', default=['all'], 
                       choices=['alignment', 'monolingual', 'all'],
                       help="Types of files to download (default: all)")
    parser.add_argument("--workers", type=int, default=4, 
                       help="Number of concurrent downloads (default: 4)")
    parser.add_argument("--info-only", action="store_true", help="Only show available files, don't download")
    
    args = parser.parse_args()
    
    # Validate worker count
    if args.workers < 1 or args.workers > 10:
        print("❌ Worker count must be between 1 and 10")
        return
    
    print(f"OPUS Corpus Downloader (Optimized)")
    print(f"Corpus: {args.corpus}")
    print(f"Languages: {args.source} -> {args.target}")
    print(f"File types: {', '.join(args.types)}")
    print(f"Concurrent workers: {args.workers}")
    print(f"Output: {args.output}")
    print("=" * 50)
    
    if args.info_only:
        # Just show available files
        print(f"🔍 Getting available files for {args.corpus}...")
        all_files = fetch_all_corpus_files(args.corpus, args.source, args.target)
        
        if all_files:
            print(f"\n📊 Available Files:")
            total_size = 0
            for i, file_info in enumerate(all_files, 1):
                size_mb = file_info['size_mb']
                total_size += size_mb
                print(f"  {i}. {file_info['description']}")
                print(f"     Type: {file_info['file_type']}")
                print(f"     Size: {size_mb:,} MB")
                print(f"     URL: {file_info['url']}")
                print()
            print(f"📏 Total size: {total_size:,} MB")
        else:
            print(f"❌ No files found for {args.corpus}")
    else:
        # Download the corpus files
        success = download_opus_corpus_complete(
            args.corpus, args.source, args.target, args.output, args.types, args.workers
        )
        
        if success:
            print(f"\n🎉 Successfully downloaded {args.corpus} files!")
        else:
            print(f"\n❌ Failed to download {args.corpus} files")
            exit(1)


if __name__ == "__main__":
    main()