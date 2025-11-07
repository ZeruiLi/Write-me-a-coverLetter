from __future__ import annotations

from fastapi import APIRouter
from ..schemas.job import JobNormalizeRequest, JobNormalized


router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/normalize", response_model=JobNormalized)
def normalize_job(req: JobNormalizeRequest) -> JobNormalized:
    # Heuristic normalization: split by lines, look for keywords
    text = (req.text or "").strip()
    lines = [l.strip("-• ") for l in text.splitlines() if l.strip()]
    role = lines[0] if lines else None
    resp = JobNormalized(
        role=role,
        responsibilities=[l for l in lines[1:6]],
        requirements=[l for l in lines[6:11]],
        keywords=[],
        language="zh" if any("的" in l for l in lines) else "en",
    )
    return resp

