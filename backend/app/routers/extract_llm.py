from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, Depends
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.errors import AppError
from ..db import models
from ..db.session import get_session
from ..providers.filecapable import GeminiFileCapable, ProviderNotFileCapable
from ..chains.extract_resume import extract_resume_with_files
from ..chains.extract_jd import extract_jd_with_files
from ..services.anchor import normalize_text, sha256
from ..services.ingestion import save_upload


router = APIRouter(prefix="/extract", tags=["extract"])


def _persist_doc(db: Session, kind: str, path: Path, mime: str) -> models.DocumentVersion:
    # Create Document + DocumentVersion
    h_dir = settings.storage_root / "documents" / kind / datetime.utcnow().strftime("%Y%m%d%H%M%S")
    h_dir.mkdir(parents=True, exist_ok=True)
    # Move already saved file path under storage is ensured by caller
    # Persist DB rows
    doc = models.Document(kind=kind)
    db.add(doc)
    db.flush()
    dv = models.DocumentVersion(document_id=doc.id, file_sha256=Path(path).name, mime=mime)
    db.add(dv)
    db.flush()
    return dv


@router.post("/resume")
async def extract_resume(file: UploadFile = File(...), db: Session = Depends(get_session)):
    # Save file to disk
    dst_dir = settings.storage_root / "uploads" / "resume"
    dst, digest = await save_upload(file, dst_dir)
    # Provider upload
    try:
        provider = GeminiFileCapable()
        token = provider.upload(str(dst))
    except ProviderNotFileCapable as e:
        raise AppError("provider_no_file_support", 501, str(e))
    except Exception as e:
        raise AppError("provider_error", 502, str(e))
    # Run extraction
    try:
        resume_obj, audit = extract_resume_with_files(provider, token)
    except ValueError as e:
        raise AppError("schema_invalid", 422, str(e))
    # Anchor text from basic normalization (for pointer base)
    try:
        raw = Path(dst).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        raw = ""
    anchor_text = normalize_text(raw)
    anchor_sha = sha256(anchor_text)
    # Persist document + anchor + resume object
    dv = _persist_doc(db, "resume", dst, file.content_type or "application/octet-stream")
    db.add(models.AnchorText(doc_version_id=dv.id, anchor_sha256=anchor_sha, text=anchor_text))
    db.add(models.ExtractionRun(doc_version_id=dv.id, kind="resume", prompt_version="v1", model=provider.model, params_json={}, status="ok"))
    db.add(models.ResumeObject(doc_version_id=dv.id, extract_version="v1", prompt_version="v1", model=provider.model, json=resume_obj.dict()))
    return {"resumeObjId": dv.id, "docVersionId": dv.id, "extract_version": "v1", "prompt_version": "v1"}


@router.post("/jd")
async def extract_jd(file: UploadFile = File(...), db: Session = Depends(get_session)):
    dst_dir = settings.storage_root / "uploads" / "jd"
    dst, digest = await save_upload(file, dst_dir)
    try:
        provider = GeminiFileCapable()
        token = provider.upload(str(dst))
    except ProviderNotFileCapable as e:
        raise AppError("provider_no_file_support", 501, str(e))
    except Exception as e:
        raise AppError("provider_error", 502, str(e))
    try:
        jd_obj, audit = extract_jd_with_files(provider, token)
    except ValueError as e:
        raise AppError("schema_invalid", 422, str(e))
    dv = _persist_doc(db, "jd", dst, file.content_type or "application/octet-stream")
    db.add(models.ExtractionRun(doc_version_id=dv.id, kind="jd", prompt_version="v1", model=provider.model, params_json={}, status="ok"))
    db.add(models.JDObject(doc_version_id=dv.id, extract_version="v1", prompt_version="v1", model=provider.model, json=jd_obj.dict()))
    return {"jdObjId": dv.id, "docVersionId": dv.id, "extract_version": "v1", "prompt_version": "v1"}

