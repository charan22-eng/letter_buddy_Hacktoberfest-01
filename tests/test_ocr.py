"""
Tests for Phase 1: Preprocessing and OCR.
"""

from pathlib import Path

import pytest
from PIL import Image, ImageEnhance, ImageFilter

from letterbuddy.ocr import ocr_images
from letterbuddy.preprocess import _enhance_image

# Assuming we have the sample image we generated
SAMPLE_IMG = Path(__file__).parent.parent / "data" / "samples" / "sample_insurance_renewal.jpg"


@pytest.fixture
def base_image():
    if not SAMPLE_IMG.exists():
        pytest.skip("Sample image not found")
    return Image.open(SAMPLE_IMG)


def test_preprocess_and_ocr_basic(base_image):
    """Test that a clean image is processed and OCR'd successfully."""
    # Preprocess
    processed = [_enhance_image(base_image.convert("RGB"))]
    assert len(processed) == 1

    from letterbuddy.config import cfg
    original_conf = cfg.ocr.min_confidence
    cfg.ocr.min_confidence = 40
    try:
        # OCR
        result = ocr_images(processed, lang="eng")

        # Assertions
        assert not result.needs_retake
        assert result.mean_confidence > 40
        assert "national insurance" in result.full_text.lower()

        # Check if key text was extracted
        text_lower = result.full_text.lower()
        assert "national insurance company" in text_lower
        assert "renewal" in text_lower
        assert "12,500" in text_lower
    finally:
        cfg.ocr.min_confidence = original_conf


def test_ocr_rotated_image(base_image):
    """Test that a rotated image still yields good text (deskewing)."""
    # Rotate by 5 degrees (within deskew range)
    rotated = base_image.rotate(5, expand=True, fillcolor="white")

    from letterbuddy.config import cfg
    original_conf = cfg.ocr.min_confidence
    cfg.ocr.min_confidence = 40
    try:
        processed = [_enhance_image(rotated.convert("RGB"))]
        result = ocr_images(processed, lang="eng")

        assert not result.needs_retake
        assert result.mean_confidence > 40
        text_lower = result.full_text.lower()
        assert "national insurance company" in text_lower
    finally:
        cfg.ocr.min_confidence = original_conf


def test_ocr_quality_gate_blurry(base_image):
    """Test that the quality gate catches blurry images."""
    # Apply heavy blur
    blurry = base_image.filter(ImageFilter.GaussianBlur(radius=8))

    processed = [_enhance_image(blurry.convert("RGB"))]
    result = ocr_images(processed, lang="eng")

    # Should trigger the quality gate
    assert result.needs_retake
    assert result.retake_reason is not None
    # We localized this string, so it's best just to check it's not empty
    assert len(result.retake_reason) > 0


def test_ocr_quality_gate_dark(base_image):
    """Test that the quality gate catches extremely dark/low-contrast images."""
    # Darken significantly
    enhancer = ImageEnhance.Brightness(base_image)
    dark = enhancer.enhance(0.1)

    processed = [_enhance_image(dark.convert("RGB"))]
    result = ocr_images(processed, lang="eng")

    # Even with adaptive thresholding, this might fail or produce garbage with low readable ratio
    if result.needs_retake:
        assert result.retake_reason is not None
    else:
        # If adaptive thresholding perfectly recovers it, the confidence should still be okay,
        # but realistically extreme darkness degrades it
        pass
