from __future__ import annotations

import hashlib
from datetime import datetime

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from ..db.session import get_session
from ..db import models
from ..core.config import settings
from ..core.errors import AppError
from ..schemas.extract import CoverPlanV1
from ..chains.plan_letter import plan_letter
from ..chains.generate_letter2 import generate_letter_html
from ..guardrails.validate import validate_letter


router = APIRouter(prefix="/generate", tags=["generate"])


@router.post("/letter2")
def letter2(body: dict = Body(...), db: Session = Depends(get_session)):
    resume_obj_id = body.get('resumeObjId')
    jd_obj_id = body.get('jdObjId')
    style = body.get('style', 'Formal')
    lang = body.get('language', 'auto')
    if not resume_obj_id or not jd_obj_id:
        raise AppError('bad_request', 400, 'resumeObjId and jdObjId required')
    rrow = db.query(models.ResumeObject).get(resume_obj_id)
    jrow = db.query(models.JDObject).get(jd_obj_id)
    if not rrow or not jrow:
        raise AppError('not_found', 404, 'objects not found')
    resume = rrow.json
    jd = jrow.json
    # Plan
    plan = plan_letter(models.Base.model_validate_json if False else CoverPlanV1,  # type: ignore
                       resume, jd, (jd.get('language') if lang == 'auto' else lang))  # type: ignore
    if not isinstance(plan, CoverPlanV1):
        plan = plan_letter(resume, jd, (jd.get('language') if lang == 'auto' else lang))  # type: ignore
    # Generate
    html = generate_letter_html(plan)
    # Validate
    try:
        from ..schemas.extract import JDObjectV1 as _JD
        validate_letter(html, plan, _JD(**jd))
    except Exception as e:
        raise AppError('guardrail_failed', 422, str(e))
    # Persist run
    h_html = hashlib.sha256(html.encode('utf-8')).hexdigest()
    run = models.GenerationRun(resume_obj_id=resume_obj_id, jd_obj_id=jd_obj_id, plan_json_sha='-', html_sha=h_html, model='-', params_json={'style':style,'language':lang}, timings_json={})
    db.add(run)
    # Save HTML to storage
    out_dir = settings.storage_exports / f"letter2_{run.created_at.strftime('%Y%m%d%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / 'letter.html'
    path.write_text(html, encoding='utf-8')
    return {"genId": run.id, "html": html}

