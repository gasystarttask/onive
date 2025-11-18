#!/usr/bin/env python3
"""
OPUS Corpora Malagasy Language Checker
Fetches all OPUS corpora and checks which ones support Malagasy ('mg') language.
Creates a CSV report with corpus name vs Malagasy language support status.
"""

import requests
import csv
import json
import time
from pathlib import Path
import argparse
from typing import List, Dict, Tuple


def fetch_corpora_list() -> List[str]:
    """
    Fetch all available corpora from OPUS API.
    
    Returns:
        List[str]: List of corpus names
    """
    print("Fetching list of all OPUS corpora...")
    
    try:
        response = requests.get("https://opus.nlpl.eu/opusapi/?corpora=True", timeout=30)
        response.raise_for_status()
        
        data = response.json()
        corpora = data.get('corpora', [])
        
        print(f"Found {len(corpora)} corpora")
        return corpora
        
    except requests.RequestException as e:
        print(f"Error fetching corpora list: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing corpora response: {e}")
        return []


def check_malagasy_support(corpus: str) -> Tuple[bool, List[str]]:
    """
    Check if a corpus supports Malagasy language.
    
    Args:
        corpus (str): Corpus name
        
    Returns:
        Tuple[bool, List[str]]: (has_malagasy, list_of_languages)
    """
    try:
        url = f"https://opus.nlpl.eu/opusapi/?languages=True&corpus={corpus}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        languages = data.get('languages', [])
        
        has_malagasy = 'mg' in languages
        return has_malagasy, languages
        
    except requests.RequestException as e:
        print(f"  ❌ Error checking {corpus}: {e}")
        return False, []
    except json.JSONDecodeError as e:
        print(f"  ❌ Error parsing response for {corpus}: {e}")
        return False, []


def process_corpora(corpora: List[str], delay: float = 0.5) -> List[Dict]:
    """
    Process all corpora and check Malagasy support.
    
    Args:
        corpora (List[str]): List of corpus names
        delay (float): Delay between API calls to be respectful
        
    Returns:
        List[Dict]: Results with corpus info and Malagasy support status
    """
    results = []
    
    print(f"\nChecking Malagasy language support for {len(corpora)} corpora...")
    print("This may take a while due to API rate limiting...")
    
    for i, corpus in enumerate(corpora, 1):
        print(f"[{i}/{len(corpora)}] Checking {corpus}...")
        
        has_malagasy, languages = check_malagasy_support(corpus)
        
        result = {
            'corpus': corpus,
            'has_malagasy': has_malagasy,
            'malagasy_status': 'Yes' if has_malagasy else 'No',
            'total_languages': len(languages),
            'languages': ', '.join(sorted(languages)) if languages else 'N/A'
        }
        
        results.append(result)
        
        if has_malagasy:
            print(f"  ✅ {corpus} supports Malagasy! ({len(languages)} total languages)")
        else:
            print(f"  ❌ {corpus} does not support Malagasy ({len(languages)} total languages)")
        
        # Be respectful to the API
        time.sleep(delay)
    
    return results


def save_to_csv(results: List[Dict], output_file: str):
    """
    Save results to CSV file.
    
    Args:
        results (List[Dict]): Results from corpus checking
        output_file (str): Output CSV file path
    """
    print(f"\nSaving results to {output_file}...")
    
    # Ensure output directory exists
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['corpus', 'malagasy_status', 'has_malagasy', 'total_languages', 'languages']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(results)
    
    print(f"✅ Results saved to {output_file}")


def generate_summary(results: List[Dict]):
    """
    Generate and print summary statistics.
    
    Args:
        results (List[Dict]): Results from corpus checking
    """
    total_corpora = len(results)
    malagasy_corpora = [r for r in results if r['has_malagasy']]
    
    print(f"\n{'='*50}")
    print("SUMMARY REPORT")
    print(f"{'='*50}")
    print(f"Total corpora checked: {total_corpora}")
    print(f"Corpora with Malagasy support: {len(malagasy_corpora)}")
    print(f"Percentage with Malagasy: {len(malagasy_corpora)/total_corpora*100:.1f}%")
    
    if malagasy_corpora:
        print(f"\nCorpora supporting Malagasy:")
        for corpus in sorted(malagasy_corpora, key=lambda x: x['corpus']):
            print(f"  • {corpus['corpus']} ({corpus['total_languages']} languages)")
    
    # Top corpora by language count
    top_multilingual = sorted(results, key=lambda x: x['total_languages'], reverse=True)[:10]
    print(f"\nTop 10 most multilingual corpora:")
    for corpus in top_multilingual:
        status = "✅" if corpus['has_malagasy'] else "❌"
        print(f"  {status} {corpus['corpus']}: {corpus['total_languages']} languages")


def save_malagasy_corpora_list(results: List[Dict], output_file: str):
    """
    Save a simple list of corpora that support Malagasy.
    
    Args:
        results (List[Dict]): Results from corpus checking
        output_file (str): Output text file path
    """
    malagasy_corpora = [r['corpus'] for r in results if r['has_malagasy']]
    
    if malagasy_corpora:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# OPUS Corpora Supporting Malagasy Language\n")
            f.write(f"# Generated automatically - {len(malagasy_corpora)} corpora found\n\n")
            for corpus in sorted(malagasy_corpora):
                f.write(f"{corpus}\n")
        
        print(f"✅ Malagasy corpora list saved to {output_file}")


def main():
    """Main function to orchestrate the corpus checking process."""
    parser = argparse.ArgumentParser(description="Check OPUS corpora for Malagasy language support")
    parser.add_argument("--output", default="./opus_malagasy_corpora.csv", 
                       help="Output CSV file path")
    parser.add_argument("--delay", type=float, default=0.5,
                       help="Delay between API calls (seconds)")
    parser.add_argument("--list-only", action="store_true",
                       help="Only save list of Malagasy corpora (no full CSV)")
    
    args = parser.parse_args()
    
    print("OPUS Corpora Malagasy Language Checker")
    print("="*40)
    
    # Step 1: Fetch all corpora
    corpora = fetch_corpora_list()
    if not corpora:
        print("❌ Failed to fetch corpora list. Exiting.")
        return
    
    # Step 2: Check each corpus for Malagasy support
    results = process_corpora(corpora, delay=args.delay)
    
    if not results:
        print("❌ No results to save. Exiting.")
        return
    
    # Step 3: Save results
    if not args.list_only:
        save_to_csv(results, args.output)
    
    # Save simple list of Malagasy corpora
    list_output = args.output.replace('.csv', '_malagasy_only.txt')
    save_malagasy_corpora_list(results, list_output)
    
    # Step 4: Generate summary
    generate_summary(results)
    
    print(f"\n🎉 Process completed successfully!")


if __name__ == "__main__":
    main()