from __future__ import annotations

from sqlalchemy.orm import Session
from ..db import models


def record_generation(db: Session, gen: models.Generation) -> None:
    db.add(gen)
    db.flush()


def get_audit(db: Session, gen_id: int) -> dict:
    gen = db.get(models.Generation, gen_id)
    if not gen:
        return {}
    return {
        "genId": gen.id,
        "resumeId": gen.resume_id,
        "job_hash": gen.job_hash,
        "type": gen.type,
        "model": {"provider": gen.provider, "name": gen.model, "temperature": gen.temperature, "top_p": gen.top_p, "seed": gen.seed},
        "params": gen.params,
        "timings": gen.timings,
        "tokens": gen.tokens,
        "output_path": gen.output_path,
        "output_summary": gen.output_summary,
        "created_at": gen.created_at.isoformat(),
    }

