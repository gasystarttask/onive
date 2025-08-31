#!/usr/bin/env python3
"""
Text cleaning utilities for preprocessing raw text data.
Removes unwanted characters, normalizes whitespace, and handles encoding issues.
"""

import re
import unicodedata
from pathlib import Path
import argparse


def clean_text(text):
    """
    Clean and normalize text data.
    
    Args:
        text (str): Input text to clean
        
    Returns:
        str: Cleaned text
    """
    # Remove control characters
    text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C' or char in '\n\t')
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Remove excessive punctuation
    text = re.sub(r'[.]{3,}', '...', text)
    text = re.sub(r'[!]{2,}', '!', text)
    text = re.sub(r'[?]{2,}', '?', text)
    
    return text


def clean_file(input_path, output_path):
    """
    Clean text file and save to output path.
    
    Args:
        input_path (str): Path to input file
        output_path (str): Path to output file
    """
    print(f"Cleaning text file: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    cleaned_content = clean_text(content)
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    print(f"Cleaned text saved to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean text files")
    parser.add_argument("input", help="Input file path")
    parser.add_argument("output", help="Output file path")
    
    args = parser.parse_args()
    clean_file(args.input, args.output)
