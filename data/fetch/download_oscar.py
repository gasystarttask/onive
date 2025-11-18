#!/usr/bin/env python3
"""
Download script for OSCAR-2301 dataset from Hugging Face.
Automatically fetches OSCAR corpus data for language model training.
"""

import os
import argparse
from pathlib import Path
from datasets import load_dataset
from huggingface_hub import hf_hub_download, login
import pandas as pd


def download_oscar(language_code="mg", output_dir="./downloads", subset="meta", 
                  cache_dir=None, streaming=False, split="train", token=None):
    """
    Download OSCAR-2301 dataset for specified language from Hugging Face.
    
    Args:
        language_code (str): Language code (e.g., 'mg' for Malagasy)
        output_dir (str): Directory to save downloaded files
        subset (str): Dataset subset ('meta' for metadata, or language code for full data)
        cache_dir (str): Cache directory for Hugging Face datasets
        streaming (bool): Whether to use streaming mode for large datasets
        split (str): Dataset split to download ('train', 'validation', etc.)
        token (str): Hugging Face authentication token
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading OSCAR-2301 dataset for language: {language_code}")
    print(f"Output directory: {output_path}")
    print(f"Subset: {subset}")
    print(f"Streaming mode: {streaming}")
    
    try:
        if subset == "meta":
            # Download metadata
            print("Downloading dataset metadata...")
            dataset = load_dataset(
                "oscar-corpus/OSCAR-2301", 
                subset,
                cache_dir=cache_dir,
                streaming=streaming,
                token=token
            )
        else:
            # Download specific language data
            print(f"Downloading language data for: {language_code}")
            dataset = load_dataset(
                "oscar-corpus/OSCAR-2301", 
                language_code,
                split=split,
                cache_dir=cache_dir,
                streaming=streaming,
                token=token
            )
        
        if not streaming:
            # Save to local files
            output_file = output_path / f"oscar_2301_{language_code}_{subset}.jsonl"
            
            if subset == "meta":
                # Handle metadata differently
                print("Processing metadata...")
                df = pd.DataFrame(dataset[split])
                df.to_json(output_file, orient='records', lines=True)
            else:
                # Save text data
                print("Saving text data...")
                with open(output_file, 'w', encoding='utf-8') as f:
                    for example in dataset:
                        f.write(f"{example}\n")
            
            print(f"Dataset saved to: {output_file}")
        else:
            print("Streaming mode enabled - data not saved locally")
            print("Use the returned dataset object for processing")
        
        print("Download completed successfully!")
        return dataset
        
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        if "gated dataset" in str(e).lower():
            print("\nTo access OSCAR-2301:")
            print("1. Visit: https://huggingface.co/datasets/oscar-corpus/OSCAR-2301")
            print("2. Click 'Request access'")
            print("3. Fill out the form explaining your use case")
            print("4. Wait for approval (may take several days)")
            print("5. Login with: python -c 'from huggingface_hub import login; login()'")
        else:
            print("Make sure you have the required dependencies installed:")
            print("pip install datasets huggingface_hub pandas")
        raise


def list_available_languages():
    """List available languages in OSCAR-2301 dataset."""
    try:
        print("Loading dataset metadata to check available languages...")
        meta_dataset = load_dataset("oscar-corpus/OSCAR-2301", "meta", streaming=True)
        
        # Get available configurations
        from datasets import get_dataset_config_names
        configs = get_dataset_config_names("oscar-corpus/OSCAR-2301")
        
        print("Available language codes:")
        for config in sorted(configs):
            if config != "meta":
                print(f"  - {config}")
                
    except Exception as e:
        print(f"Error listing languages: {e}")
        if "gated dataset" in str(e).lower():
            print("Access to OSCAR-2301 is required to list languages.")
            print("Please request access first at: https://huggingface.co/datasets/oscar-corpus/OSCAR-2301")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download OSCAR-2301 dataset from Hugging Face")
    parser.add_argument("--lang", default="mg", help="Language code (e.g., 'mg' for Malagasy)")
    parser.add_argument("--output", default="./downloads", help="Output directory")
    parser.add_argument("--subset", default="meta", help="Dataset subset ('meta' or language code)")
    parser.add_argument("--cache-dir", help="Cache directory for HuggingFace datasets")
    parser.add_argument("--streaming", action="store_true", help="Use streaming mode for large datasets")
    parser.add_argument("--split", default="train", help="Dataset split to download")
    parser.add_argument("--list-langs", action="store_true", help="List available language codes")
    parser.add_argument("--token", help="Hugging Face authentication token")
    
    args = parser.parse_args()
    
    if args.list_langs:
        list_available_languages()
    else:
        download_oscar(
            language_code=args.lang,
            output_dir=args.output,
            subset=args.subset,
            cache_dir=args.cache_dir,
            streaming=args.streaming,
            split=args.split,
            token=args.token
        )
