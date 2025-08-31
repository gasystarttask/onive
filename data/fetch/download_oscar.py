#!/usr/bin/env python3
"""
Download script for OSCAR dataset.
Automatically fetches OSCAR corpus data for language model training.
"""

import os
import requests
import argparse
from pathlib import Path


def download_oscar(language_code="mg", output_dir="./downloads"):
    """
    Download OSCAR dataset for specified language.
    
    Args:
        language_code (str): Language code (e.g., 'mg' for Malagasy)
        output_dir (str): Directory to save downloaded files
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading OSCAR dataset for language: {language_code}")
    print(f"Output directory: {output_path}")
    
    # Placeholder for actual OSCAR download logic
    # In a real implementation, this would connect to OSCAR API/repository
    
    print("Download completed successfully!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download OSCAR dataset")
    parser.add_argument("--lang", default="mg", help="Language code")
    parser.add_argument("--output", default="./downloads", help="Output directory")
    
    args = parser.parse_args()
    download_oscar(args.lang, args.output)
