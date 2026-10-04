# Letter Buddy: Bringing the Digital World to Analogue Lives

**Hacktoberfest Weekend Challenge: Build for a Friend**

## The Problem
Many elderly individuals, like my neighbour uncle, struggle to read and understand complex official letters (insurance, banking, pensions) which are often in English. They have to wait for someone younger to translate and explain what action is needed, causing anxiety and delays.

## The Solution
**Letter Buddy** is an offline, privacy-first web application running entirely on my laptop. He simply points his phone camera at a letter, and within seconds, he sees a simple, large-text summary in Telugu and hears it read aloud. 

Crucially, **nothing ever leaves the machine**. Official letters contain sensitive PII. Letter Buddy enforces a strict network block (`netguard.py`) ensuring zero data leakage.

## Technical Architecture
- **Hardware**: NVIDIA RTX 4050 Laptop GPU (6GB VRAM - Tier T6)
- **OCR**: PyTesseract (with custom confidence-based quality gates to reject blurry photos)
- **LLM**: Ollama (`qwen2.5:7b`) for deterministic structured extraction and translation
- **TTS**: `espeak-ng` for offline Telugu speech synthesis
- **Frontend**: Pure HTML/JS/CSS served via FastAPI, designed with high contrast and large touch targets

## Evaluation Highlights
From our synthetic benchmarks (`eval/RESULTS.md`):
- **OCR Quality Gate**: Successfully rejects images with < 45% mean confidence or low readable ratios.
- **Extraction Accuracy**: 100% on synthetic test sets (using regex candidates to prevent hallucination).
- **Word Error Rate (WER)**: Measured on synthetic insurance letters vs ground truth.

## The Handover
[MANUAL ITEM: The handover story goes here]

## The Reaction
[MANUAL ITEM: The person's own reaction goes here]

## Open Source
This project was built for Hacktoberfest. You can find the full source code and setup instructions here: [GitHub Repo Link TBD]
