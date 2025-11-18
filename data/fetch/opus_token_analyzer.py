#!/usr/bin/env python3
"""
OPUS Corpora Token Counter and Ranker
Fetches token statistics for parallel corpora and ranks them by token count.
Supports any source-target language pair.
"""

import requests
import json
import csv
import time
from pathlib import Path
import argparse
from typing import List, Dict, Optional


def load_corpora_list(file_path: str) -> List[str]:
    """
    Load list of corpora from text file.
    
    Args:
        file_path (str): Path to the text file with corpus names
        
    Returns:
        List[str]: List of corpus names
    """
    corpora = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    corpora.append(line)
        
        print(f"Loaded {len(corpora)} corpora from {file_path}")
        return corpora
        
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return []
    except Exception as e:
        print(f"❌ Error reading file {file_path}: {e}")
        return []


def fetch_corpus_stats(corpus: str, source_lang: str, target_lang: str) -> Optional[Dict]:
    """
    Fetch token statistics for a corpus from OPUS API.
    
    Args:
        corpus (str): Corpus name
        source_lang (str): Source language code
        target_lang (str): Target language code
        
    Returns:
        Optional[Dict]: Corpus statistics or None if error
    """
    try:
        # Try both language directions to find the best data
        urls = [
            f"https://opus.nlpl.eu/opusapi/?corpus={corpus}&source={source_lang}&target={target_lang}&preprocessing=xml&version=latest",
            f"https://opus.nlpl.eu/opusapi/?corpus={corpus}&source={target_lang}&target={source_lang}&preprocessing=xml&version=latest"
        ]
        
        best_stats = None
        max_pairs = 0
        
        for i, url in enumerate(urls):
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                corpora_data = data.get('corpora', [])
                
                # Find the parallel alignment entry (with both source and target)
                for entry in corpora_data:
                    entry_source = entry.get('source', '')
                    entry_target = entry.get('target', '')
                    
                    # Check if this is a valid parallel entry
                    if (entry_source and entry_target and 
                        entry_source != entry_target and
                        {entry_source, entry_target} == {source_lang, target_lang}):
                        
                        # Safe conversion of alignment_pairs to int
                        try:
                            alignment_pairs = int(entry.get('alignment_pairs', 0) or 0)
                        except (ValueError, TypeError):
                            alignment_pairs = 0
                        
                        if alignment_pairs > max_pairs:
                            max_pairs = alignment_pairs
                            best_stats = entry
                            best_stats['requested_direction'] = f"{source_lang}-{target_lang}" if i == 0 else f"{target_lang}-{source_lang}"
                
            except Exception as e:
                print(f"    Warning: Error with URL {i+1}: {e}")
                continue
        
        return best_stats
        
    except Exception as e:
        print(f"  ❌ Unexpected error for {corpus}: {e}")
        return None


def analyze_corpus_tokens(corpora: List[str], source_lang: str, target_lang: str, delay: float = 0.5) -> List[Dict]:
    """
    Analyze token counts for all corpora.
    
    Args:
        corpora (List[str]): List of corpus names
        source_lang (str): Source language code
        target_lang (str): Target language code
        delay (float): Delay between API calls
        
    Returns:
        List[Dict]: Corpus statistics sorted by total tokens
    """
    results = []
    
    print(f"\nAnalyzing token counts for {len(corpora)} corpora ({source_lang}-{target_lang})...")
    print("This may take a while due to API rate limiting...")
    
    for i, corpus in enumerate(corpora, 1):
        print(f"[{i}/{len(corpora)}] Analyzing {corpus}...")
        
        stats = fetch_corpus_stats(corpus, source_lang, target_lang)
        
        if stats:
            # Extract key metrics with safe type conversion
            try:
                source_tokens = int(stats.get('source_tokens', 0) or 0)
            except (ValueError, TypeError):
                source_tokens = 0
            
            try:
                target_tokens = int(stats.get('target_tokens', 0) or 0)
            except (ValueError, TypeError):
                target_tokens = 0
            
            try:
                alignment_pairs = int(stats.get('alignment_pairs', 0) or 0)
            except (ValueError, TypeError):
                alignment_pairs = 0
            
            try:
                documents = int(stats.get('documents', 0) or 0)
            except (ValueError, TypeError):
                documents = 0
            
            try:
                size_mb = float(stats.get('size', 0) or 0)
            except (ValueError, TypeError):
                size_mb = 0.0
            
            result = {
                'corpus': corpus,
                'source_language': stats.get('source', ''),
                'target_language': stats.get('target', ''),
                'requested_direction': stats.get('requested_direction', f"{source_lang}-{target_lang}"),
                'source_tokens': source_tokens,
                'target_tokens': target_tokens,
                'total_tokens': source_tokens + target_tokens,
                'alignment_pairs': alignment_pairs,
                'documents': documents,
                'size_mb': size_mb,
                'version': stats.get('version', ''),
                'url': stats.get('url', ''),
                'avg_tokens_per_pair': round((source_tokens + target_tokens) / alignment_pairs, 2) if alignment_pairs > 0 else 0
            }
            
            results.append(result)
            
            direction_info = f"({stats.get('source', '')}-{stats.get('target', '')})"
            print(f"  ✅ {corpus} {direction_info}: {alignment_pairs:,} pairs, {source_tokens:,} + {target_tokens:,} = {source_tokens + target_tokens:,} tokens")
        else:
            print(f"  ❌ No data found for {corpus} with {source_lang}-{target_lang}")
            # Add empty entry to track failed corpora
            results.append({
                'corpus': corpus,
                'source_language': 'N/A',
                'target_language': 'N/A',
                'requested_direction': f"{source_lang}-{target_lang}",
                'source_tokens': 0,
                'target_tokens': 0,
                'total_tokens': 0,
                'alignment_pairs': 0,
                'documents': 0,
                'size_mb': 0,
                'version': 'N/A',
                'url': 'N/A',
                'avg_tokens_per_pair': 0
            })
        
        # Be respectful to the API
        time.sleep(delay)
    
    # Sort by total tokens (descending)
    results.sort(key=lambda x: x['total_tokens'], reverse=True)
    
    return results


def save_detailed_report(results: List[Dict], output_file: str, source_lang: str, target_lang: str):
    """
    Save detailed analysis to CSV file.
    
    Args:
        results (List[Dict]): Analysis results
        output_file (str): Output CSV file path
        source_lang (str): Source language code
        target_lang (str): Target language code
    """
    print(f"\nSaving detailed report to {output_file}...")
    
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    fieldnames = [
        'rank', 'corpus', 'source_language', 'target_language', 'requested_direction',
        'total_tokens', 'source_tokens', 'target_tokens',
        'alignment_pairs', 'avg_tokens_per_pair', 'documents',
        'size_mb', 'version', 'url'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header with metadata
        writer.writerow({
            'rank': f'# Analysis for {source_lang}-{target_lang} language pair',
            'corpus': '', 'source_language': '', 'target_language': '', 'requested_direction': '',
            'total_tokens': '', 'source_tokens': '', 'target_tokens': '',
            'alignment_pairs': '', 'avg_tokens_per_pair': '', 'documents': '',
            'size_mb': '', 'version': '', 'url': ''
        })
        
        writer.writeheader()
        
        for rank, result in enumerate(results, 1):
            result['rank'] = rank
            writer.writerow(result)
    
    print(f"✅ Detailed report saved to {output_file}")


def generate_summary_report(results: List[Dict], source_lang: str, target_lang: str):
    """
    Generate and print summary statistics.
    
    Args:
        results (List[Dict]): Analysis results
        source_lang (str): Source language code
        target_lang (str): Target language code
    """
    valid_results = [r for r in results if r['total_tokens'] > 0]
    
    print(f"\n{'='*60}")
    print(f"{source_lang.upper()}-{target_lang.upper()} CORPORA TOKEN ANALYSIS SUMMARY")
    print(f"{'='*60}")
    
    print(f"Total corpora analyzed: {len(results)}")
    print(f"Corpora with data: {len(valid_results)}")
    print(f"Failed to analyze: {len(results) - len(valid_results)}")
    
    if valid_results:
        total_tokens = sum(r['total_tokens'] for r in valid_results)
        total_pairs = sum(r['alignment_pairs'] for r in valid_results)
        
        print(f"\nOverall Statistics:")
        print(f"  Total tokens across all corpora: {total_tokens:,}")
        print(f"  Total alignment pairs: {total_pairs:,}")
        print(f"  Average tokens per corpus: {total_tokens // len(valid_results):,}")
        
        print(f"\nTop 10 Corpora by Token Count:")
        print("-" * 80)
        print(f"{'Rank':<4} {'Corpus':<20} {'Direction':<12} {'Total Tokens':<15} {'Pairs':<10}")
        print("-" * 80)
        
        for i, result in enumerate(valid_results[:10], 1):
            direction = f"{result['source_language']}-{result['target_language']}"
            print(f"{i:<4} {result['corpus']:<20} {direction:<12} {result['total_tokens']:,<15} {result['alignment_pairs']:,<10}")
        
        # Language direction distribution
        print(f"\nActual Language Pair Distribution:")
        lang_pairs = {}
        for r in valid_results:
            pair = f"{r['source_language']}-{r['target_language']}"
            lang_pairs[pair] = lang_pairs.get(pair, 0) + 1
        
        for pair, count in sorted(lang_pairs.items()):
            print(f"  {pair}: {count} corpora")


def save_top_corpora_list(results: List[Dict], output_file: str, source_lang: str, target_lang: str, top_n: int = 10):
    """
    Save a simple ranked list of top corpora.
    
    Args:
        results (List[Dict]): Analysis results
        output_file (str): Output text file path
        source_lang (str): Source language code
        target_lang (str): Target language code
        top_n (int): Number of top corpora to include
    """
    valid_results = [r for r in results if r['total_tokens'] > 0]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Top {top_n} OPUS Corpora for {source_lang.upper()}-{target_lang.upper()} by Token Count\n")
        f.write(f"# Generated automatically - ranked by total tokens\n\n")
        
        for i, result in enumerate(valid_results[:top_n], 1):
            direction = f"{result['source_language']}-{result['target_language']}"
            f.write(f"{i}. {result['corpus']}\n")
            f.write(f"   Tokens: {result['total_tokens']:,} ({result['source_tokens']:,} + {result['target_tokens']:,})\n")
            f.write(f"   Pairs: {result['alignment_pairs']:,}\n")
            f.write(f"   Direction: {direction}\n")
            f.write(f"   URL: {result['url']}\n\n")
    
    print(f"✅ Top corpora list saved to {output_file}")


def main():
    """Main function to orchestrate the token analysis."""
    parser = argparse.ArgumentParser(description="Analyze OPUS corpora token counts for any language pair")
    parser.add_argument("--input", default="./opus_malagasy_corpora_malagasy_only.txt",
                       help="Input file with corpora list")
    parser.add_argument("--output", 
                       help="Output CSV file for detailed analysis (default: auto-generated)")
    parser.add_argument("--source", default="mg",
                       help="Source language code (default: mg)")
    parser.add_argument("--target", default="en", 
                       help="Target language code (default: en)")
    parser.add_argument("--delay", type=float, default=0.5,
                       help="Delay between API calls (seconds)")
    parser.add_argument("--top-n", type=int, default=10,
                       help="Number of top corpora to highlight")
    
    args = parser.parse_args()
    
    # Auto-generate output filename if not provided
    if not args.output:
        base_name = Path(args.input).stem
        args.output = f"./opus_{args.source}_{args.target}_token_analysis.csv"
    
    print(f"OPUS {args.source.upper()}-{args.target.upper()} Corpora Token Analysis")
    print("="*50)
    
    # Load corpora list
    corpora = load_corpora_list(args.input)
    if not corpora:
        print("❌ No corpora to analyze. Exiting.")
        return
    
    # Analyze token counts
    results = analyze_corpus_tokens(corpora, args.source, args.target, delay=args.delay)
    
    if not results:
        print("❌ No results to save. Exiting.")
        return
    
    # Save detailed report
    save_detailed_report(results, args.output, args.source, args.target)
    
    # Save top corpora list
    top_list_file = args.output.replace('.csv', '_top_corpora.txt')
    save_top_corpora_list(results, top_list_file, args.source, args.target, args.top_n)
    
    # Generate summary
    generate_summary_report(results, args.source, args.target)
    
    print(f"\n🎉 Token analysis completed successfully!")


if __name__ == "__main__":
    main()