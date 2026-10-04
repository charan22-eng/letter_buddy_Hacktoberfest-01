"""
Letter Buddy – Image preprocessing (Phase 1).

Handles both images (JPG, PNG) and PDFs.
Applies deskewing, denoising, and adaptive contrast to prepare for OCR.
"""

from __future__ import annotations

import io
from pathlib import Path

import cv2
import fitz  # PyMuPDF
import numpy as np
from PIL import Image, ImageOps


def preprocess_file(filepath: str | Path) -> list[Image.Image]:
    """
    Read a file (PDF or image) and return a list of preprocessed PIL Images (one per page).
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    ext = path.suffix.lower()

    if ext == ".pdf":
        return _process_pdf(path)
    elif ext in (".jpg", ".jpeg", ".png"):
        return _process_image(path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def _process_pdf(path: Path) -> list[Image.Image]:
    """Extract pages from PDF as images and preprocess."""
    doc = fitz.open(path)
    images = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        # 300 DPI is usually good for OCR
        pix = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))

        # Convert to PIL Image
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data)).convert("RGB")
        images.append(_enhance_image(img))

    return images


def _process_image(path: Path) -> list[Image.Image]:
    """Read a single image file, handle EXIF, and preprocess."""
    img = Image.open(path)
    # Handle EXIF orientation
    img = ImageOps.exif_transpose(img)
    img = img.convert("RGB")
    return [_enhance_image(img)]


def _enhance_image(pil_img: Image.Image) -> Image.Image:
    """
    Apply OpenCV preprocessing to improve OCR:
    - Grayscale
    - Deskew (basic)
    - Denoise
    - Adaptive thresholding / Contrast
    """
    # Convert PIL Image to OpenCV format (numpy array)
    cv_img = np.array(pil_img)
    # Convert RGB to BGR (OpenCV format)
    cv_img = cv_img[:, :, ::-1].copy()

    # Convert to grayscale
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

    # Denoise (median blur works well for salt-and-pepper noise)
    denoised = cv2.medianBlur(gray, 3)

    # Adaptive Thresholding to handle uneven lighting (shadows, phone flashes)
    binary = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Optional: Basic deskewing logic
    coords = np.column_stack(np.where(binary == 0))
    if len(coords) > 0:
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # Only rotate if the angle is significant
        if abs(angle) > 0.5 and abs(angle) < 45:
            (h, w) = binary.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            binary = cv2.warpAffine(binary, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # Convert back to PIL Image
    result_img = Image.fromarray(binary)
    return result_img
