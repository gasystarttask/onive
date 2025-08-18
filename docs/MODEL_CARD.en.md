# Malagasy LLM – based on Qwen2.5-7B-Instruct

## Model Description
This is an **open-source Malagasy Large Language Model (LLM)** adapted from **Qwen2.5-7B-Instruct**.  
It is designed for **general conversation in Malagasy** and domain-specific applications such as **medical transcription, prescription summarization, and meeting assistants**.

- **Base model:** Qwen2.5-7B-Instruct  
- **Technique:** Language Adaptive Fine-Tuning (LAFT) + Parameter-Efficient Fine-Tuning (PEFT)  
- **Hardware:** Fits on a single 32GB GPU (LoRA/QLoRA)  
- **Languages:** Malagasy (primary), retains some multilingual ability  

## Intended Uses
- Chatbots & assistants in Malagasy  
- Summarization of prescriptions and consultations (*for practitioners only, not for direct patient use*)  
- Meeting/workshop summarization  

## Limitations
- Not a medical authority. Should not replace professional judgment.  
- Trained on limited Malagasy data; may produce hallucinations.  
- Safety mitigations still in progress.  

## License
Released under Apache-2.0. Qwen2.5 base licensing applies.  

## Citation
TBD – after first release.
