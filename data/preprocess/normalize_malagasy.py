#!/usr/bin/env python3
"""
Malagasy text normalization utilities.
Handles Malagasy-specific text processing and normalization.
"""

import re
import unicodedata
import argparse
from pathlib import Path


# Malagasy alphabet and character mappings
MALAGASY_CHARS = set('abdefghijklmnoprstuvyzàáâãäèéêëìíîïòóôõöùúûüýÿ')


def normalize_malagasy_text(text):
    """
    Normalize Malagasy text with language-specific rules.
    
    Args:
        text (str): Input Malagasy text
        
    Returns:
        str: Normalized text
    """
    # Convert to lowercase for processing
    text = text.lower()
    
    # Normalize diacritics while preserving Malagasy-specific ones
    text = unicodedata.normalize('NFD', text)
    
    # Handle common Malagasy spelling variations
    text = re.sub(r'\bc\b', 'k', text)  # Replace standalone 'c' with 'k'
    text = re.sub(r'\bqu\b', 'k', text)  # Replace 'qu' with 'k'
    
    # Normalize punctuation spacing
    text = re.sub(r'\s*([,.;:!?])\s*', r'\1 ', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text


def normalize_file(input_path, output_path):
    """
    Normalize Malagasy text file.
    
    Args:
        input_path (str): Path to input file
        output_path (str): Path to output file
    """
    print(f"Normalizing Malagasy text: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    normalized_lines = [normalize_malagasy_text(line) for line in lines]
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(normalized_lines)
    
    print(f"Normalized text saved to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Normalize Malagasy text")
    parser.add_argument("input", help="Input file path")
    parser.add_argument("output", help="Output file path")
    
    args = parser.parse_args()
    normalize_file(args.input, args.output)
