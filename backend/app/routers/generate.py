from __future__ import annotations

import hashlib
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.config import settings
from ..db import models
from ..db.session import get_session
from ..schemas.generate import (
    GenerateShortRequest,
    GenerateShortResponse,
    GenerateLetterRequest,
    GenerateLetterResponse,
)
from ..services.generation import short_answer, letter
from ..services.detect import detect_lang
from ..services.audit import record_generation
from ..providers.gemini import GeminiProvider


router = APIRouter(prefix="/generate", tags=["generate"])


def _hash_inputs(resume_id: int, job_text: str) -> str:
    h = hashlib.sha256()
    h.update(f"{resume_id}|{job_text}".encode("utf-8"))
    return h.hexdigest()[:12]


@router.post("/short", response_model=GenerateShortResponse)
def gen_short(req: GenerateShortRequest, db: Session = Depends(get_session)):
    resume = db.get(models.Resume, req.resumeId)
    if not resume:
        from ..core.errors import AppError
        raise AppError("resume_not_found", 404)

    # Normalize job text
    job_text = req.job.get("text") if isinstance(req.job, dict) else " ".join((req.job.role or "", *req.job.requirements, *req.job.responsibilities))
    job_lang = detect_lang(job_text)
    out_lang = req.language if req.language != "auto" else (resume.lang or job_lang or settings.default_output_lang)

    # Load last snapshot
    snap = (
        db.query(models.ResumeSnapshot)
        .filter(models.ResumeSnapshot.resume_id == resume.id)
        .order_by(models.ResumeSnapshot.id.desc())
        .first()
    )
    snap_data = snap.data if snap else {}

    provider = GeminiProvider()
    text, timings = short_answer(snap_data, req.job if isinstance(req.job, dict) else req.job.model_dump(), req.question, out_lang, {}, provider)

    gen = models.Generation(
        resume_id=resume.id,
        job_hash=_hash_inputs(resume.id, job_text),
        type="short",
        provider=settings.model_provider,
        model="gemini-2.5-flash",
        temperature=0.6,
        top_p=1.0,
        seed=0,
        params={"language": out_lang, "question": req.question},
        prompt="",
        timings=timings,
        tokens={},
        output_path=None,
        output_summary=text[:120],
        created_at=datetime.utcnow(),
    )
    record_generation(db, gen)

    return GenerateShortResponse(genId=gen.id, text=text)


@router.post("/letter", response_model=GenerateLetterResponse)
def gen_letter(req: GenerateLetterRequest, db: Session = Depends(get_session)):
    resume = db.get(models.Resume, req.resumeId)
    if not resume:
        from ..core.errors import AppError
        raise AppError("resume_not_found", 404)

    job_text = req.job.get("text") if isinstance(req.job, dict) else " ".join((req.job.role or "", *req.job.requirements, *req.job.responsibilities))
    job_lang = detect_lang(job_text)
    out_lang = req.language if req.language != "auto" else (resume.lang or job_lang or settings.default_output_lang)

    snap = (
        db.query(models.ResumeSnapshot)
        .filter(models.ResumeSnapshot.resume_id == resume.id)
        .order_by(models.ResumeSnapshot.id.desc())
        .first()
    )
    snap_data = snap.data if snap else {}
    provider = GeminiProvider()

    content, timings = letter(
        snap_data,
        req.job if isinstance(req.job, dict) else req.job.model_dump(),
        {
            "language": out_lang,
            "style": req.style,
            "paragraphs_max": req.paragraphs_max,
            "target_words": req.target_words,
            "include_keywords": req.include_keywords,
            "avoid_keywords": req.avoid_keywords,
            "format": req.format,
        },
        provider,
    )

    gen = models.Generation(
        resume_id=resume.id,
        job_hash=_hash_inputs(resume.id, job_text),
        type="letter",
        provider=settings.model_provider,
        model="gemini-2.5-flash",
        temperature=0.6,
        top_p=1.0,
        seed=0,
        params={
            "language": out_lang,
            "style": req.style,
            "paragraphs_max": req.paragraphs_max,
            "target_words": req.target_words,
            "include_keywords": req.include_keywords,
            "avoid_keywords": req.avoid_keywords,
            "format": req.format,
        },
        prompt="",
        timings=timings,
        tokens={},
        output_path=None,
        output_summary=(content[:120] if content else None),
        created_at=datetime.utcnow(),
    )
    record_generation(db, gen)

    meta = {"style": req.style, "language": out_lang, "counts": {"chars": len(content or "")}}
    return GenerateLetterResponse(genId=gen.id, format=req.format, content=content, meta=meta)

