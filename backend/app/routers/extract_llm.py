from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, Depends
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.errors import AppError
from ..db import models
from ..db.session import get_session
from ..clients.filecap import extract_resume_file, extract_jd_file, FilecapUnavailable
from ..chains.extract_resume import extract_resume_with_files
from ..chains.extract_jd import extract_jd_with_files
from ..services.anchor import normalize_text, sha256, find_span
from ..schemas.extract import ResumeObjectV1, ResumeExtractRaw, Evidence
from ..services.ingestion import save_upload


router = APIRouter(prefix="/extract", tags=["extract"])


def _persist_doc(db: Session, kind: str, path: Path, mime: str, file_sha256: str | None = None) -> models.DocumentVersion:
    # Create Document + DocumentVersion
    h_dir = settings.storage_root / "documents" / kind / datetime.utcnow().strftime("%Y%m%d%H%M%S")
    h_dir.mkdir(parents=True, exist_ok=True)
    # Move already saved file path under storage is ensured by caller
    # Persist DB rows
    doc = models.Document(kind=kind)
    db.add(doc)
    db.flush()
    dv = models.DocumentVersion(document_id=doc.id, file_sha256=(file_sha256 or Path(path).name), mime=mime)
    db.add(dv)
    db.flush()
    return dv


@router.post("/resume")
async def extract_resume(file: UploadFile = File(...), db: Session = Depends(get_session)):
    # Save file to disk
    dst_dir = settings.storage_root / "uploads" / "resume"
    dst, digest = await save_upload(file, dst_dir)
    # Provider upload
    # Call sidecar filecap
    try:
        raw_obj = extract_resume_file(str(dst))
    except FilecapUnavailable as e:
        raise AppError("provider_no_file_support", 501, str(e))
    # Anchor text from basic normalization (for pointer base)
    try:
        raw = Path(dst).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        raw = ""
    anchor_text = normalize_text(raw)
    anchor_sha = sha256(anchor_text)
    # Build pointer-based ResumeObjectV1
    try:
        # map raw to pointer evidence
        experiences = []
        for exp in raw_obj.experiences:
            bullets = []
            for b in exp.bullets:
                start, end = find_span(anchor_text, b.evidence.quote)
                bullets.append({
                    "id": b.id,
                    "action": b.action,
                    "outcome": b.outcome,
                    "metric": b.metric,
                    "evidence": {"start": start, "end": end, "anchor_sha256": anchor_sha},
                })
            experiences.append({
                "title": exp.title,
                "company": exp.company,
                "period": exp.period,
                "bullets": bullets,
            })
        resume_obj = ResumeObjectV1(
            basics=raw_obj.basics,
            hard_skills=raw_obj.hard_skills,
            experiences=experiences,  # type: ignore
            education=raw_obj.education,
            language=raw_obj.language,
            meta=raw_obj.meta,
        )
    except Exception as e:
        raise AppError("schema_invalid", 422, f"evidence pointer mapping failed: {e}")
    # Persist document + anchor + resume object
    dv = _persist_doc(db, "resume", dst, file.content_type or "application/octet-stream", file_sha256=digest)
    db.add(models.AnchorText(doc_version_id=dv.id, anchor_sha256=anchor_sha, text=anchor_text))
    db.add(models.ExtractionRun(doc_version_id=dv.id, kind="resume", prompt_version="v1", model=provider.model, params_json={}, status="ok"))
    robj = models.ResumeObject(doc_version_id=dv.id, extract_version="v1", prompt_version="v1", model=provider.model, json=resume_obj.dict())
    db.add(robj)
    db.flush()
    return {"resumeObjId": robj.id, "docVersionId": dv.id, "extract_version": "v1", "prompt_version": "v1"}


@router.post("/jd")
async def extract_jd(file: UploadFile = File(...), db: Session = Depends(get_session)):
    dst_dir = settings.storage_root / "uploads" / "jd"
    dst, digest = await save_upload(file, dst_dir)
    try:
        jd_obj = extract_jd_file(str(dst))
    except FilecapUnavailable as e:
        raise AppError("provider_no_file_support", 501, str(e))
    dv = _persist_doc(db, "jd", dst, file.content_type or "application/octet-stream", file_sha256=digest)
    db.add(models.ExtractionRun(doc_version_id=dv.id, kind="jd", prompt_version="v1", model=provider.model, params_json={}, status="ok"))
    jobj = models.JDObject(doc_version_id=dv.id, extract_version="v1", prompt_version="v1", model=provider.model, json=jd_obj.dict())
    db.add(jobj)
    db.flush()
    return {"jdObjId": jobj.id, "docVersionId": dv.id, "extract_version": "v1", "prompt_version": "v1"}
