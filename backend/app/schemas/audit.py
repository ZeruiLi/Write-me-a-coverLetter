from pydantic import BaseModel


class AuditResponse(BaseModel):
    genId: int
    resumeId: int | None
    job_hash: str
    type: str
    model: dict
    params: dict
    timings: dict
    tokens: dict | None = None
    output_path: str | None = None
    output_summary: str | None = None
    created_at: str

