# Data Fetching Scripts

This directory contains scripts for automatically downloading datasets used in the project.

## Scripts

### `download_oscar.py`
Downloads OSCAR corpus data for specified languages.

**Usage:**
```bash
python download_oscar.py --lang mg --output ./downloads
```

### `download_opus.sh`
Downloads parallel text data from OPUS collection.

**Usage:**
```bash
./download_opus.sh en-mg ./downloads/opus
```

## Requirements

- Python 3.7+
- `requests` library for Python scripts
- `wget` and `unzip` for shell scripts

## Notes

- All scripts create necessary output directories automatically
- Downloads are resumable where supported
- Check dataset licenses before use
