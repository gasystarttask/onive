### Metadata + Download scripts

Inside `data/` we keep:

```bash
data/
├── fetch/
│   ├── download_oscar.py
│   ├── download_opus.sh
│   └── README.md
├── preprocess/
│   ├── clean_text.py
│   ├── normalize_malagasy.py
│   └── deduplicate.py
└── metadata/
    ├── dataset_catalog.yaml
    └── licenses.md
```

- dataset_catalog.yaml → tracks source, size, license, usage policy.
- Scripts automatically fetch and prepare datasets reproducibly.