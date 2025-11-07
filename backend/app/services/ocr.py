from __future__ import annotations

from pathlib import Path


def ocr_image(path: Path, lang: str = "chi_sim+eng") -> str:
    try:
        from PIL import Image  # type: ignore
        import pytesseract  # type: ignore
        img = Image.open(str(path))
        return pytesseract.image_to_string(img, lang=lang)
    except Exception:
        return ""


def ocr_pdf(path: Path, lang: str = "chi_sim+eng") -> str:
    # Minimal placeholder: recommend pdfplumber text; full pdf2image OCR out-of-scope for bootstrap
    return ""

