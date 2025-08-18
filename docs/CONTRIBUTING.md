# Contributing to Malagasy LLM

Thank you for your interest in contributing!  
This project is **community-driven**, and we welcome contributions in many forms:

- Data collection & cleaning
- Fine-tuning recipes
- Evaluation scripts
- Documentation & translations
- Domain-specific adapters (medical, meetings, etc.)

---

## 📝 How to Contribute

### 1. Reporting Issues

- Use GitHub Issues to report bugs, incorrect outputs, or unsafe generations.
- Clearly describe the problem and (if possible) provide an example.

### 2. Adding Data

- Place raw data sources under `data/fetch/`.
- Clean and filtered versions go under `data/clean/`.
- Always include **license information** for any dataset you contribute.
- Do **not** contribute data that contains personally identifiable information (PII) without explicit consent.

### 3. Improving Training

- Add new training recipes in `training/`.
- Use [LoRA/QLoRA](https://huggingface.co/docs/peft/index) for parameter-efficient fine-tuning.
- Document hyperparameters and configs in a README for reproducibility.

### 4. Domain Packs

- Add new adapters in `models/<domain-name>/`.
- Include an example notebook or script showing how to load and test it.

### 5. Documentation

- Update bilingual docs when adding major features.
- Translate key changes into Malagasy whenever possible.

---

## 🔒 Contribution Policy

- Be respectful and inclusive.
- Respect Malagasy culture, dialects, and diversity.
- No harmful, offensive, or unsafe content in data or prompts.
- Medical contributions must include a **safety disclaimer** (see `docs/SAFETY.*`).
- All contributions are reviewed before merging.

---

## ⚙️ Development Setup

1. Clone the repo:
```bash
   git clone https://github.com/gasystarttask/onive.git
   cd onive
```
1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Run tests (optional):

```bash
pytest
```
### 🌍 Language Policy

- Contributions can be written in English or Malagasy.

- For docs: try to provide both (even short translations).

### 🙏 Acknowledgements

Inspired by open-source LLM efforts such as Hugging Face, OpenAssistant, and Wechsl.

