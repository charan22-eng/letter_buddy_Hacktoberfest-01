"""
Letter Buddy – OCR engine (Phase 1).

Runs Tesseract on preprocessed images.
Implements the quality gate to reject bad photos.
"""

from __future__ import annotations

import os
from typing import Any

import pytesseract
from PIL import Image
from pydantic import BaseModel

from letterbuddy.config import cfg

# Configure Tesseract path if it's on Windows
if os.name == 'nt':
    tess_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if os.path.exists(tess_path):
        pytesseract.pytesseract.tesseract_cmd = tess_path

    # Set TESSDATA_PREFIX to our local tessdata
    tessdata_dir = cfg.resolve_path("tessdata")
    if tessdata_dir.exists():
        os.environ["TESSDATA_PREFIX"] = str(tessdata_dir)


class OcrResult(BaseModel):
    needs_retake: bool = False
    retake_reason: str | None = None
    mean_confidence: float = 0.0
    full_text: str = ""
    pages: int = 1


def _check_quality(data: dict[str, Any], min_conf: int, min_ratio: float) -> tuple[bool, str | None, float]:
    """
    Check OCR quality using confidence scores.
    Returns: (needs_retake, reason, mean_confidence)
    """
    confidences = [int(c) for c in data.get('conf', []) if c != '-1']

    if not confidences:
        return True, "blurry", 0.0

    mean_conf = sum(confidences) / len(confidences)
    readable_words = sum(1 for c in confidences if c >= min_conf)
    readable_ratio = readable_words / len(confidences)

    if mean_conf < min_conf:
        return True, "blurry", mean_conf

    if readable_ratio < min_ratio:
        return True, "dark", mean_conf

    # Could add more checks for cut_off or tilted based on bounding boxes

    return False, None, mean_conf


def ocr_images(images: list[Image.Image], lang: str | None = None) -> OcrResult:
    """
    Run Tesseract OCR on a list of images and apply quality gates.
    """
    if lang is None:
        lang = cfg.ocr.langs

    all_text = []
    total_conf = 0.0
    pages = len(images)

    # We'll use the first page's quality as the primary gate
    # For a robust implementation, you might want to aggregate or check all pages

    needs_retake = False
    reason = None
    mean_conf = 0.0

    for i, img in enumerate(images):
        try:
            # Auto-detect script if lang is default
            if lang is None or lang == cfg.ocr.langs:
                try:
                    osd = pytesseract.image_to_osd(img)
                    current_lang = "eng+tel" if "Telugu" in osd else "eng"
                except:
                    current_lang = "eng"
            else:
                current_lang = lang

            # Get detailed data including confidence
            data = pytesseract.image_to_data(img, lang=current_lang, output_type=pytesseract.Output.DICT)

            # Check quality (we mainly gate on the first page, or if a page is really bad)
            is_bad, bad_reason, page_conf = _check_quality(data, cfg.ocr.min_confidence, cfg.ocr.min_readable_ratio)

            if is_bad and i == 0:
                needs_retake = True
                reason = bad_reason
                mean_conf = page_conf
                break # Bail out early if first page is bad

            total_conf += page_conf

            # Get the actual text
            text = pytesseract.image_to_string(img, lang=current_lang)
            all_text.append(text)

        except pytesseract.TesseractError:
            needs_retake = True
            reason = "error"
            break

    if not needs_retake and pages > 0:
        mean_conf = total_conf / pages

    if reason:
        from letterbuddy.config import get_label
        # Translate the reason code to a localized message
        reason_msg = get_label(f"quality.{reason}")
    else:
        reason_msg = None

    return OcrResult(
        needs_retake=needs_retake,
        retake_reason=reason_msg,
        mean_confidence=mean_conf,
        full_text="\n\n--- Page Break ---\n\n".join(all_text),
        pages=pages
    )
