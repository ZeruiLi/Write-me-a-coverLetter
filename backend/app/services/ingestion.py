from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Tuple

from fastapi import UploadFile

ALLOWED_EXT = {"pdf", "docx", "txt", "md", "jpg", "jpeg", "png"}


def allowed_ext(filename: str) -> bool:
    return filename.lower().split(".")[-1] in ALLOWED_EXT


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


async def save_upload(file: UploadFile, dst_dir: Path) -> Tuple[Path, str]:
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / file.filename
    with dst.open("wb") as out:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)
    await file.close()
    digest = sha256_file(dst)
    return dst, digest


def read_text_from_file(path: Path) -> str:
    ext = path.suffix.lower().lstrip(".")
    if ext in {"txt", "md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    if ext == "docx":
        try:
            import docx  # type: ignore
            doc = docx.Document(str(path))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception:
            return ""
    if ext == "pdf":
        try:
            import pdfplumber  # type: ignore
            text_parts = []
            with pdfplumber.open(str(path)) as pdf:
                for page in pdf.pages:
                    text_parts.append(page.extract_text() or "")
            return "\n".join(text_parts).strip()
        except Exception:
            return ""
    if ext in {"jpg", "jpeg", "png"}:
        # handled by OCR
        return ""
    return ""

