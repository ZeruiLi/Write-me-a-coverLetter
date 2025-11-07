from typing import List, Optional
from pydantic import BaseModel, Field


class JobNormalizeRequest(BaseModel):
    text: str


class JobNormalized(BaseModel):
    role: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    language: Optional[str] = None  # 'zh' | 'en'

