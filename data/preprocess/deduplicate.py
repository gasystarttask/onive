#!/usr/bin/env python3
"""
Text deduplication utilities.
Removes duplicate sentences and near-duplicate content from text datasets.
"""

import hashlib
import argparse
from pathlib import Path
from collections import defaultdict
import difflib


def compute_hash(text):
    """
    Compute hash for text deduplication.
    
    Args:
        text (str): Input text
        
    Returns:
        str: Hash string
    """
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def is_near_duplicate(text1, text2, threshold=0.85):
    """
    Check if two texts are near-duplicates using similarity ratio.
    
    Args:
        text1 (str): First text
        text2 (str): Second text
        threshold (float): Similarity threshold
        
    Returns:
        bool: True if texts are near-duplicates
    """
    similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
    return similarity >= threshold


def deduplicate_text(lines, exact_only=False):
    """
    Remove duplicate lines from text.
    
    Args:
        lines (list): List of text lines
        exact_only (bool): If True, only remove exact duplicates
        
    Returns:
        list: Deduplicated lines
    """
    if exact_only:
        seen = set()
        unique_lines = []
        
        for line in lines:
            line_hash = compute_hash(line.strip())
            if line_hash not in seen:
                seen.add(line_hash)
                unique_lines.append(line)
        
        return unique_lines
    
    else:
        # Near-duplicate removal (more expensive)
        unique_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            is_duplicate = False
            for existing_line in unique_lines:
                if is_near_duplicate(line, existing_line.strip()):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_lines.append(line + '\n')
        
        return unique_lines


def deduplicate_file(input_path, output_path, exact_only=False):
    """
    Deduplicate text file.
    
    Args:
        input_path (str): Path to input file
        output_path (str): Path to output file
        exact_only (bool): If True, only remove exact duplicates
    """
    print(f"Deduplicating text file: {input_path}")
    print(f"Mode: {'Exact duplicates only' if exact_only else 'Near-duplicates included'}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    original_count = len(lines)
    unique_lines = deduplicate_text(lines, exact_only)
    final_count = len(unique_lines)
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(unique_lines)
    
    print(f"Removed {original_count - final_count} duplicates")
    print(f"Final count: {final_count} lines")
    print(f"Deduplicated text saved to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deduplicate text files")
    parser.add_argument("input", help="Input file path")
    parser.add_argument("output", help="Output file path")
    parser.add_argument("--exact-only", action="store_true", 
                       help="Only remove exact duplicates")
    
    args = parser.parse_args()
    deduplicate_file(args.input, args.output, args.exact_only)
