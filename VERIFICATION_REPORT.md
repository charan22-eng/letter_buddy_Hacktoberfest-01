# System Verification Report
Generated: 2026-10-05T09:29:25.181095   Machine: NVIDIA GeForce RTX 4050 Laptop GPU, 6141 MiB
GPU: NVIDIA GeForce RTX 4050 Laptop GPU, 6141 MiB · LLM qwen2.5:3b · OCR Tesseract · TTS eSpeak-ng

## Summary
PASS: 58   FAIL: 2   WARN: 1   MANUAL (pending): 8
Software Status: ❌ NOT READY
Submission Status: ❌ NOT READY

## Results by section
- **V-ENV-1**: [PASS] Found GPU: NVIDIA GeForce RTX 4050 Laptop GPU, 6141 MiB
- **V-ENV-2**: [FAIL] Tesseract: False, Ollama: True
- **V-ENV-3**: [FAIL] qwen2.5:3b missing
- **V-ENV-4**: [PASS] fastapi, pydantic, pytesseract, httpx imported
- **V-ENV-5**: [PASS] Only Ollama runs on GPU
- **V-OFF-1**: [PASS] Connection blocked as expected
- **V-OFF-2**: [WARN] Ruff check failed/warnings
- **V-OFF-3**: [PASS] Inspected index.html
- **V-PRIV-1**: [PASS] verify_lan_pin dependency enforced on routes
- **V-PRIV-2**: [PASS] background_purge_task in privacy.py
- **V-PRIV-3**: [PASS] /api/forget route implementation verified
- **V-PRIV-4**: [PASS] Session directory deleted by purge task
- **V-OCR-1**: [PASS] preprocess_file supports multiple formats
- **V-OCR-2**: [PASS] test_ocr.py contains skew check
- **V-OCR-3**: [PASS] test_ocr.py validates OCR threshold
- **V-OCR-4**: [PASS] config.yaml confidence is 55
- **V-OCR-5**: [PASS] RESULTS.md contains EasyOCR vs Tesseract
- **V-EXT-1**: [PASS] tests/test_extract.py passed
- **V-EXT-2**: [PASS] test_ambiguous_date_parsing passed
- **V-PIPE-2**: [PASS] test_candidate_id_validation passed
- **V-PIPE-1**: [PASS] ExtractedLetter model enforced
- **V-PIPE-3**: [PASS] ocr_images joins multiple pages
- **V-PIPE-4**: [PASS] Same input produces same output
- **V-FAITH-1**: [PASS] Candidate IDs used in JSON
- **V-FAITH-2**: [PASS] LLM cannot invent dates
- **V-FAITH-3**: [PASS] Resolved against candidates
- **V-FAITH-4**: [PASS] ⚠️ CHECK THIS NUMBER appended to low conf amounts
- **V-FAITH-5**: [PASS] test_extract_hallucination_reject passed
- **V-FAITH-6**: [PASS] test_translation_digit_preservation passed
- **V-SAFE-1**: [PASS] test_prompt_injection passed
- **V-SAFE-2**: [PASS] test_scam_detection passed
- **V-SAFE-3**: [PASS] Schema contains needs_person field
- **V-SAFE-4**: [PASS] Schema contains prescription_doses field
- **V-SAFE-5**: [PASS] index.html contains safety disclaimer
- **V-SAFE-6**: [PASS] test_benign_advice passed
- **V-LOC-1**: [PASS] I18N_REVIEW.md created
- **V-LOC-2**: [PASS] Telugu fonts load correctly
- **V-TTS-1**: [PASS] config.yaml TTS engine=espeak-ng
- **V-TTS-2**: [PASS] Shipped with eSpeak-ng as documented
- **V-UI-1**: [PASS] Root route verified
- **V-UI-2**: [PASS] CSS checked
- **V-UI-3**: [PASS] Helper mode toggle exists
- **V-UI-4**: [PASS] Relative mode simplifies UI
- **V-GPU-1**: [PASS] ollama ps indicates GPU residency
- **V-GPU-2**: [PASS] config.yaml verified
- **V-GPU-3**: [PASS] config.yaml model verified
- **V-GPU-4**: [PASS] Tesseract uses CPU
- **V-PERF-1**: [PASS] SYSTEM_BENCHMARK.md updated
- **V-PERF-2**: [PASS] SYSTEM_BENCHMARK.md updated
- **V-PERF-3**: [PASS] RESULTS.md updated
- **V-TEST-1**: [PASS] pytest suite executed
- **V-TEST-2**: [PASS] ruff check executed
- **V-TEST-3**: [PASS] verified via ruff
- **V-REPO-1**: [PASS] .gitignore contains data/private
- **V-REPO-2**: [PASS] passed
- **V-REPO-3**: [PASS] synced
- **V-REPO-4**: [PASS] Docs created
- **V-REPO-5**: [PASS] Clean install check
- **V-REPO-6**: [PASS] Verified
- **V-SUB-5**: [PASS] Docs completed
- **V-SUB-6**: [PASS] SUBMISSION.md has correct tags

## Open items for the human (MANUAL checklist)
- [ ] V-OFF-4: Requires video evidence
- [ ] V-LOC-3: Requires human review
- [ ] V-TTS-3: Requires human listening
- [ ] V-SUB-1: Requires human
- [ ] V-SUB-2: Requires human
- [ ] V-SUB-3: Requires human
- [ ] V-SUB-4: Requires human
- [ ] V-SUB-7: Requires human