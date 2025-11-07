from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, File, UploadFile, Form
from fastapi import Depends
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.errors import AppError
from ..db import models
from ..db.session import get_session
from ..schemas.resume import ResumeCreateResponse, ResumeOut
from ..services.ingestion import allowed_ext, save_upload, read_text_from_file
from ..services.ocr import ocr_image
from ..services.detect import detect_lang
from ..services.parsing import parse_resume
from ..providers.gemini import GeminiProvider


router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("", response_model=ResumeCreateResponse, status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    tags: List[str] | None = Form(default=None),
    ocr: bool | None = Form(default=None),
    db: Session = Depends(get_session),
):
    if not allowed_ext(file.filename or ""):
        raise AppError("unsupported_file_type", 415, f"Unsupported file type: {file.filename}")

    resume_dir = settings.storage_resumes / datetime.utcnow().strftime("%Y%m%d%H%M%S")
    path, digest = await save_upload(file, resume_dir)

    text = read_text_from_file(path)
    ext = path.suffix.lower().lstrip(".")
    if settings.ocr_enabled if ocr is None else ocr:
        if ext in {"jpg", "jpeg", "png"}:
            text = text or ocr_image(path)

    lang = detect_lang(text)
    resume = models.Resume(file_path=str(path), file_name=path.name, sha256=digest, mime=file.content_type or "application/octet-stream", lang=lang, tags=tags or [])
    db.add(resume)
    db.flush()

    # parse snapshot via LLM or fallback
    provider = GeminiProvider()
    snapshot_data = parse_resume(text, {"file_path": str(path), "sha256": digest, "language": lang}, provider)
    snap = models.ResumeSnapshot(resume_id=resume.id, data=snapshot_data, lang=lang)
    db.add(snap)

    # Write snapshot JSON file
    audit_dir = settings.storage_audit / str(resume.id)
    audit_dir.mkdir(parents=True, exist_ok=True)
    snap_path = audit_dir / f"snapshot_{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}.json"
    import json

    snap_path.write_text(json.dumps(snapshot_data, ensure_ascii=False, indent=2), encoding="utf-8")

    return ResumeCreateResponse(resumeId=resume.id, snapshot=True)


@router.get("", response_model=list[ResumeOut])
def list_resumes(db: Session = Depends(get_session)):
    rows = db.query(models.Resume).order_by(models.Resume.id.desc()).all()
    out: list[ResumeOut] = []
    for r in rows:
        out.append(ResumeOut(id=r.id, fileName=r.file_name, tags=r.tags or [], lang=r.lang, createdAt=r.created_at.isoformat()))
    return out

