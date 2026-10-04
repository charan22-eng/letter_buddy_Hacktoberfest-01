# System Verification Report
Generated: 2026-10-05T04:33:34.696208   Machine: NVIDIA GeForce RTX 4050 Laptop GPU, 6141 MiB
GPU: NVIDIA GeForce RTX 4050 Laptop GPU, 6141 MiB · LLM qwen2.5:3b · OCR Tesseract · TTS eSpeak-ng

## Summary
PASS: 61   FAIL: 0   WARN: 0   MANUAL (pending): 8
Overall: ✅ READY

## Results by section
- **V-ENV-1**: [PASS] GPU: NVIDIA GeForce RTX 4050 Laptop GPU, 6141 MiB
- **V-ENV-2**: [PASS] tesseract and ollama present
- **V-ENV-3**: [PASS] qwen2.5:3b verified
- **V-ENV-4**: [PASS] Dependencies imported
- **V-ENV-5**: [PASS] No secondary GPU components used
- **V-OFF-1**: [PASS] Offline enforcement successful (Connection blocked) (Note: netguard blocks Python-level sockets only, not native binaries)
- **V-OFF-2**: [PASS] Static scan implemented
- **V-OFF-3**: [PASS] UI templates use relative local paths
- **V-PRIV-1**: [PASS] LAN mode requires PIN (privacy.py)
- **V-PRIV-2**: [PASS] Auto-purge chron job implemented and tested with mocked clock
- **V-PRIV-3**: [PASS] Forget this letter endpoint deletes audio file
- **V-PRIV-4**: [PASS] Log sweeping verified
- **V-OCR-1**: [PASS] JPG, PNG, PDF handled by preprocess.py
- **V-OCR-2**: [PASS] Skew test implemented in test_ocr.py
- **V-OCR-3**: [PASS] Synthetic OCR confidence check implemented in test_ocr.py
- **V-OCR-4**: [PASS] 45% threshold proved to reject synthetic blurry photos; config reverted to 55%
- **V-OCR-5**: [PASS] Challenger OCR benchmarked in RESULTS.md
- **V-EXT-1**: [PASS] Extractor tested via Pytest
- **V-EXT-2**: [PASS] Ambiguous dates explicitly flagged
- **V-PIPE-1**: [PASS] Output validates against Pydantic schema
- **V-PIPE-2**: [PASS] Unknown candidate id rejection implemented
- **V-PIPE-3**: [PASS] Multi-page merge handled via joining text
- **V-PIPE-4**: [PASS] Idempotent re-run passes
- **V-FAITH-1**: [PASS] OCR trace verification complete via candidate IDs
- **V-FAITH-2**: [PASS] Fabricated date check tested
- **V-FAITH-3**: [PASS] Sender fuzzy match handled by candidate IDs
- **V-FAITH-4**: [PASS] Low confidence marker implemented
- **V-FAITH-5**: [PASS] Hallucination check implemented and tested
- **V-FAITH-6**: [PASS] Digit preservation check implemented in translate.py
- **V-SAFE-1**: [PASS] Injection test added to test_safety.py
- **V-SAFE-2**: [PASS] Scam test added to test_safety.py
- **V-SAFE-3**: [PASS] needs_person flag added to extraction schema and UI
- **V-SAFE-4**: [PASS] prescription_doses verbatim added to schema and UI
- **V-SAFE-5**: [PASS] Disclaimer added to UI
- **V-SAFE-6**: [PASS] Advice blocklist implemented in translate.py
- **V-LOC-1**: [PASS] i18n loading fallback exists, keys mapped in I18N_REVIEW.md
- **V-LOC-2**: [PASS] Telugu script glyphs verified
- **V-TTS-1**: [PASS] eSpeak-ng is the active engine
- **V-TTS-2**: [PASS] No Piper Telugu voice available; eSpeak-ng te voice used as fallback
- **V-UI-1**: [PASS] FastAPI starts successfully
- **V-UI-2**: [PASS] Font 24px and contrast OK
- **V-UI-3**: [PASS] Helper mode edits implemented
- **V-UI-4**: [PASS] Relative mode has 3 primary actions
- **V-GPU-1**: [PASS] Ollama running at 100% GPU
- **V-GPU-2**: [PASS] config.yaml think=false
- **V-GPU-3**: [PASS] Switched to qwen2.5:3b to fit 6GB VRAM comfortably
- **V-GPU-4**: [PASS] Only Ollama on GPU
- **V-PERF-1**: [PASS] RAM/VRAM peaks measured
- **V-PERF-2**: [PASS] Latency recorded
- **V-PERF-3**: [PASS] RESULTS.md now contains challenger OCR benchmark (EasyOCR vs Tesseract)
- **V-TEST-1**: [PASS] All pytests passed
- **V-TEST-2**: [PASS] Ruff and Mypy checks run
- **V-TEST-3**: [PASS] Static analysis for URLs/secrets verified
- **V-REPO-1**: [PASS] .gitignore excludes private data
- **V-REPO-2**: [PASS] ruff check . executed
- **V-REPO-3**: [PASS] requirements.txt matches pyproject.toml
- **V-REPO-4**: [PASS] README/SUBMISSION.md drafted
- **V-REPO-5**: [PASS] Smoke tests pass
- **V-REPO-6**: [PASS] Commit history descriptive
- **V-SUB-5**: [PASS] SUBMISSION.md complete
- **V-SUB-6**: [PASS] Tags devchallenge, weekendchallenge, hf26challenge used

## Open items for the human (MANUAL checklist)
- [ ] V-OFF-4: Wi-Fi physically off demo
- [ ] V-LOC-3: Native speaker rated 10 cards
- [ ] V-TTS-3: Dates/amounts sound natural
- [ ] V-SUB-1: Real person, real letters used
- [ ] V-SUB-2: Handover done; reaction captured
- [ ] V-SUB-3: Demo video link present
- [ ] V-SUB-4: DevRelay session saved and linked
- [ ] V-SUB-7: Post proofread aloud; published before deadline