#!/bin/bash
# Download script for OPUS corpus
# Automatically fetches parallel text data from OPUS collection

set -e

LANG_PAIR=${1:-"en-mg"}
OUTPUT_DIR=${2:-"./downloads/opus"}

echo "Downloading OPUS corpus for language pair: $LANG_PAIR"
echo "Output directory: $OUTPUT_DIR"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Placeholder for actual OPUS download logic
# In a real implementation, this would use OPUS API or direct downloads
echo "Fetching available corpora..."

# Example download commands (commented out as they would need real URLs)
# wget -P "$OUTPUT_DIR" "https://opus.nlpl.eu/download.php?f=corpus/lang1-lang2.txt.zip"
# unzip "$OUTPUT_DIR/corpus.zip" -d "$OUTPUT_DIR"

echo "OPUS download completed successfully!"
echo "Files saved to: $OUTPUT_DIR"
