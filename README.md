# Letter Buddy

Letter Buddy is an offline, privacy-first application designed to help elderly individuals (or anyone needing assistance) read and understand complex official letters such as bank notices, utility bills, insurance renewals, and government letters.

## Why it exists
Many people receive official correspondence in English but may only read or understand another language (like Telugu). These letters often contain high-stakes information, deadlines, and amounts to pay. Uploading these private documents to cloud services (like ChatGPT or Google Cloud) poses severe privacy risks. Letter Buddy solves this by processing everything 100% locally on your machine, ensuring private data never leaves your computer.

## Privacy Model
- **100% Local Inference:** All OCR and LLM processing runs locally.
- **No Telemetry, No Analytics, No CDN:** The application is entirely self-contained.
- **Session Auto-Purge:** The application stores artifacts (images, OCR text, audio) in isolated sessions and automatically purges them after 1 hour (or immediately if the user clicks "Forget this letter").
- **Network Guard:** Python-level sockets are blocked from making external connections (loopback only).

## Architecture
1. **Input:** User uploads an image (JPG/PNG) or PDF.
2. **Preprocess:** Converts PDF to images and normalizes formats.
3. **OCR:** Tesseract extracts raw text from the image.
4. **Extraction:** Deterministic regex extracts candidates (dates, amounts, contacts, etc.) and assigns IDs.
5. **Understanding:** A local LLM (qwen2.5:3b via Ollama) extracts structured information strictly referencing candidate IDs to prevent hallucinations.
6. **Safety:** Deterministic rules check for high-stakes documents and scams.
7. **Localization:** The summary is translated (e.g., to Telugu).
8. **TTS:** eSpeak-ng generates audio of the translated summary.
9. **UI:** FastAPI serves a clean, accessible web interface.

## Installation

### Windows Setup
Run the included setup script:
```powershell
.\scripts\setup.ps1
```

### Dependencies Setup
1. **Ollama:** Install from [ollama.com](https://ollama.com/). Pull the required model: `ollama run qwen2.5:3b`.
2. **Tesseract OCR:** Install Tesseract (e.g., via `winget install UB-Mannheim.TesseractOCR`). Ensure it is in your PATH.
3. **eSpeak-ng:** Install eSpeak-ng for offline text-to-speech.

### Quickstart
Create a virtual environment and install dependencies:
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -e ".[dev,eval]"
```

## CLI Examples
Read a letter and print raw OCR:
```bash
letterbuddy read data/samples/sample_insurance_renewal.jpg
```
Explain a letter (full pipeline) and optionally read aloud:
```bash
letterbuddy explain data/samples/sample_insurance_renewal.jpg --speak
```
Start the web UI:
```bash
letterbuddy serve --port 8000
```

## Web UI Example
Once the server is running, open `http://127.0.0.1:8000` in your browser. Upload a letter, and the application will display a simplified "Letter Card" with the sender, summary, date, amount, and deadline.

## Safety Limitations
- **No Legal/Medical/Financial Advice:** The application only summarizes what is written.
- **High-Stakes Flag:** Court, tax, and medical documents will trigger a `needs_person` flag, warning the user to consult a trusted person.
- **Scam Detection:** Known scam patterns (urgent OTP requests, fake authority threats) will trigger a critical warning.

## GPU Model Selection
The default model is `qwen2.5:3b` running on Ollama, which requires ~6GB VRAM (comfortably runs on an RTX 3050/4050 Laptop GPU). 

## Evaluation Results
- **OCR:** ~49% Word Error Rate on synthetic English+Telugu documents (Tesseract).
- **LLM:** Zero hallucinations detected on candidate extraction using ID grounding.

## Tests
Run the test suite:
```bash
pytest
```

## Repository Structure
- `src/letterbuddy/`: Core application logic (OCR, extraction, safety, privacy, TTS).
- `src/letterbuddy/web/`: FastAPI application and static UI assets.
- `tests/`: Automated test suite (pytest).
- `scripts/`: Verification and setup scripts.
- `eval/`: Evaluation results and benchmarks.

## License
MIT License.
