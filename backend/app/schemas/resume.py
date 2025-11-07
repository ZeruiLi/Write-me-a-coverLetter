from typing import List, Optional
from pydantic import BaseModel


class ResumeCreateResponse(BaseModel):
    resumeId: int
    snapshot: bool


class ResumeOut(BaseModel):
    id: int
    fileName: str
    tags: List[str] = []
    lang: Optional[str] = None
    createdAt: str

