#!/bin/bash
# Install optimizations for OPUS downloader

echo "Installing optimization dependencies..."

# Install basic optimization package
pip install tqdm

echo "✅ Optimization dependencies installed!"
echo ""
echo "Usage examples:"
echo "# Download with default 4 workers"
echo "python data/fetch/download_opus.py NLLB --source mg --target en"
echo ""
echo "# Download with 8 concurrent workers (faster)"
echo "python data/fetch/download_opus.py NLLB --source mg --target en --workers 8"
echo ""
echo "# Download only alignment files with 6 workers"
echo "python data/fetch/download_opus.py NLLB --source mg --target en --types alignment --workers 6"