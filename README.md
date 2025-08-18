# Onive
## Malagasy LLM – based on Qwen2.5-7B-Instruct

This project provides an open-source Malagasy Large Language Model (LLM) built on `Qwen2.5-7B-Instruct`, a strong multilingual instruction-tuned model. Our goal is to make high-quality natural language processing accessible for the Malagasy language, enabling both general-purpose conversation and specialized applications.

Although Malagasy is a low-resource language, we leverage Language Adaptive Fine-Tuning (LAFT) on public Malagasy corpora (Wikipedia, OSCAR, Tatoeba, JW300) and Parameter-Efficient Fine-Tuning (PEFT) methods such as LoRA/QLoRA. This allows us to train effectively on a single 32 GB GPU while preserving the performance of the base model.

### ✨ Key Features

Conversational agent in Malagasy – natural and fluent responses.

Domain packs for specialized use-cases:

### 📝 Medical assistant

Summarizes prescriptions into clear, structured outputs (anaran’ny fanafody, habetsahana, fomba fandraisana, fampitandremana).

Helps practitioners by transcribing consultations (doctor–patient dialogue) into clean, organized notes.

### 📊 Meeting and workshop assistants – extract agendas, action items, and summaries in Malagasy.

Efficient training – lightweight adapters that can be easily shared or merged.

Community-driven – open datasets, code, and evaluation tools.

### 📅 Roadmap

Phase 1: Collect and clean Malagasy corpora.

Phase 2: LAFT adaptation + instruction-tuning.

Phase 3: Domain-specific adapters for healthcare and meetings.

Phase 4: Evaluation, preference tuning, and open demo release.

By publishing models, code, and training recipes openly, we hope to foster a Malagasy NLP community where developers, researchers, and practitioners can build on top of this work. The project is designed to be modular and extensible, so anyone can create derived applications in Malagasy, from healthcare to business tools.

### 📖 Documentation:  
- [Model Card (English)](docs/MODEL_CARD.en.md) | [Karatra modely (Malagasy)](docs/MODEL_CARD.mg.md)  
- [Safety (EN)](docs/SAFETY.en.md) | [Fiarovana (MG)](docs/SAFETY.mg.md)  
- [Roadmap](docs/ROADMAP.md)  
- [Contributing](docs/CONTRIBUTING.md)
