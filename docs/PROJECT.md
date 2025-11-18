# Repo layout
```bash
onive/
│
├── data/                  # Data handling
│   ├── fetch/             # Scripts to download OSCAR, JW300, etc.
│   ├── clean/             # LangID, deduplication, filtering
│   └── README.md          # Data sources + licenses
│
├── training/              # Training recipes
│   ├── laft/              # Language Adaptive Fine-Tuning
│   ├── sft/               # Supervised Fine-Tuning (LoRA/QLoRA)
│   ├── dpo/               # Preference optimization
│   └── README.md
│
├── eval/                  # Evaluation scripts
│   ├── perplexity/
│   ├── summarization/
│   ├── translation/
│   └── human_eval/
│
├── serving/               # Inference
│   ├── vllm/              # API + configs
│   └── demo/              # HF Spaces / Gradio apps
│
├── models/                # Released adapters/checkpoints
│   ├── base/              # Qwen2.5-7B-Instruct (reference)
│   ├── malagasy-sft/      # Main Malagasy adapter
│   ├── medical/           # Prescription + consultation
│   └── meetings/          # Workshop/meeting assistant
│
├── docs/                  # Documentation
│   ├── MODEL_CARD.en.md
│   ├── MODEL_CARD.mg.md
│   ├── SAFETY.en.md
│   ├── SAFETY.mg.md
│   └── ROADMAP.md
│
├── README.md              # Main project description
└── LICENSE
```