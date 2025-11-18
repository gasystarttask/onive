#!/usr/bin/env python3
"""
OPUS Corpus Post-Processor
Compresses extracted XML files to match alignment file references.
"""

import os
import gzip
import argparse
from pathlib import Path
from tqdm import tqdm
import shutil


def compress_xml_files(corpus_dir: str, dry_run: bool = False) -> int:
    """
    Compress XML files to .gz format to match alignment file references.
    
    Args:
        corpus_dir (str): Corpus directory containing extracted files
        dry_run (bool): If True, only show what would be compressed
        
    Returns:
        int: Number of files compressed
    """
    corpus_path = Path(corpus_dir)
    
    if not corpus_path.exists():
        print(f"❌ Directory not found: {corpus_dir}")
        return 0
    
    # Find all XML files (excluding alignment files)
    xml_files = []
    for xml_file in corpus_path.rglob("*.xml"):
        # Skip alignment files (they contain alignment data, not text)
        if "alignment" not in xml_file.name.lower():
            xml_files.append(xml_file)
    
    if not xml_files:
        print(f"❌ No XML text files found in {corpus_dir}")
        return 0
    
    print(f"📁 Found {len(xml_files)} XML files to compress")
    
    if dry_run:
        print("\n🔍 Dry run - files that would be compressed:")
        for xml_file in xml_files:
            rel_path = xml_file.relative_to(corpus_path)
            gz_path = xml_file.with_suffix('.xml.gz')
            print(f"  {rel_path} -> {gz_path.relative_to(corpus_path)}")
        return len(xml_files)
    
    compressed_count = 0
    
    print("\n📦 Compressing XML files...")
    for xml_file in tqdm(xml_files, desc="Compressing"):
        try:
            gz_file = xml_file.with_suffix('.xml.gz')
            
            # Compress the XML file
            with open(xml_file, 'rb') as f_in:
                with gzip.open(gz_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Verify compression was successful
            if gz_file.exists() and gz_file.stat().st_size > 0:
                # Remove original XML file
                xml_file.unlink()
                compressed_count += 1
            else:
                print(f"  ⚠️  Failed to compress: {xml_file}")
                
        except Exception as e:
            print(f"  ❌ Error compressing {xml_file}: {e}")
    
    return compressed_count


def verify_alignment_match(corpus_dir: str, alignment_file: str = None) -> bool:
    """
    Verify that compressed files match alignment file references.
    
    Args:
        corpus_dir (str): Corpus directory
        alignment_file (str): Path to alignment file (auto-detected if None)
        
    Returns:
        bool: True if all references can be resolved
    """
    corpus_path = Path(corpus_dir)
    
    # Find alignment file if not specified
    if alignment_file is None:
        alignment_files = list(corpus_path.glob("**/alignment_*.xml"))
        if not alignment_files:
            print("❌ No alignment file found")
            return False
        alignment_file = alignment_files[0]
    else:
        alignment_file = Path(alignment_file)
    
    if not alignment_file.exists():
        print(f"❌ Alignment file not found: {alignment_file}")
        return False
    
    print(f"🔍 Checking alignment file: {alignment_file.name}")
    
    # Parse alignment file to get referenced files
    referenced_files = set()
    missing_files = set()
    
    try:
        with open(alignment_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if 'fromDoc=' in line or 'toDoc=' in line:
                    # Extract file references
                    import re
                    from_match = re.search(r'fromDoc="([^"]+)"', line)
                    to_match = re.search(r'toDoc="([^"]+)"', line)
                    
                    if from_match:
                        referenced_files.add(from_match.group(1))
                    if to_match:
                        referenced_files.add(to_match.group(1))
                    
                    break  # Only need to check the linkGrp line
    
    except Exception as e:
        print(f"❌ Error reading alignment file: {e}")
        return False
    
    print(f"📋 Found {len(referenced_files)} file references in alignment")
    
    # Check if referenced files exist
    for ref_file in referenced_files:
        # Look for the file relative to corpus directory
        possible_paths = [
            corpus_path / ref_file,
            corpus_path / Path(ref_file).name,
            # Look in subdirectories
            *corpus_path.rglob(Path(ref_file).name)
        ]
        
        found = False
        for possible_path in possible_paths:
            if possible_path.exists():
                print(f"  ✅ Found: {ref_file} -> {possible_path}")
                found = True
                break
        
        if not found:
            missing_files.add(ref_file)
            print(f"  ❌ Missing: {ref_file}")
    
    if missing_files:
        print(f"\n⚠️  {len(missing_files)} referenced files are missing!")
        print("You may need to download additional files or check the corpus structure.")
        return False
    else:
        print(f"\n✅ All {len(referenced_files)} referenced files found!")
        return True


def main():
    """Main function for post-processing corpus files."""
    parser = argparse.ArgumentParser(description="Post-process OPUS corpus files")
    parser.add_argument("corpus_dir", help="Corpus directory to process")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without doing it")
    parser.add_argument("--verify", action="store_true", help="Verify alignment file references")
    parser.add_argument("--alignment", help="Path to alignment file (auto-detected if not specified)")
    
    args = parser.parse_args()
    
    print(f"OPUS Corpus Post-Processor")
    print(f"Directory: {args.corpus_dir}")
    print("=" * 50)
    
    if args.verify:
        # Verify alignment references
        print("🔍 Verifying alignment file references...")
        if verify_alignment_match(args.corpus_dir, args.alignment):
            print("\n✅ Verification passed!")
        else:
            print("\n❌ Verification failed!")
            return 1
    else:
        # Compress XML files
        compressed_count = compress_xml_files(args.corpus_dir, args.dry_run)
        
        if compressed_count > 0:
            if args.dry_run:
                print(f"\n📊 Would compress {compressed_count} files")
            else:
                print(f"\n✅ Successfully compressed {compressed_count} files")
                
                # Auto-verify after compression
                print("\n🔍 Verifying alignment references...")
                if verify_alignment_match(args.corpus_dir, args.alignment):
                    print("✅ Post-compression verification passed!")
                else:
                    print("⚠️  Some alignment references still missing")
        else:
            print("\n❌ No files were compressed")
            return 1


if __name__ == "__main__":
    main()