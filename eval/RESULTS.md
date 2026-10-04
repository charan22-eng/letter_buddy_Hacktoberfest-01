# Evaluation Results
- **Sample**: sample_insurance_renewal.jpg

## OCR Benchmark
We benchmarked Tesseract and EasyOCR on the synthetic insurance letter.
- **Tesseract (eng only)**: 2.3% WER (0.33s)
- **Tesseract (eng+tel)**: 49.43% WER (0.50s)
- **EasyOCR (en, te)**: 43.68% WER (4.95s)

**Conclusion**: The ~54% (now ~49%) WER reported earlier was caused by running the `eng+tel` bilingual model on a purely English document, causing Tesseract to hallucinate Telugu characters. EasyOCR is 10x slower and performs similarly poorly on this mixed-language setup for English text. We will stick with Tesseract but dynamically prefer `eng` or use `eng+tel` only when necessary, or simply accept the confidence hit for English letters if Telugu is strictly required. For the final app, Tesseract is the winner because it is faster and fits within the offline requirements without adding 200MB+ dependencies like EasyOCR/PyTorch.

## LLM Verification
- Model: `qwen2.5:3b`
- **Extraction Accuracy**: 100% (Passed synthetic checks)
- **VRAM Residency**: 100% (Model fits inside 6GB VRAM on RTX 3050)
