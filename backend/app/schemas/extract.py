from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field, validator


Lang = Literal['zh', 'en']


class Evidence(BaseModel):
    start: int
    end: int
    anchor_sha256: str


class Bullet(BaseModel):
    id: str
    action: str
    outcome: str
    metric: str
    evidence: Evidence


class Experience(BaseModel):
    title: str
    company: str
    period: dict
    bullets: List[Bullet] = Field(default_factory=list)


class EducationItem(BaseModel):
    school: str
    degree: str
    graduation: str


class ResumeObjectV1(BaseModel):
    basics: dict
    hard_skills: List[str] = Field(default_factory=list)
    experiences: List[Experience] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    language: Lang
    meta: dict

# Raw extraction (LLM output with quotes, will be post-processed to pointers)
class EvidenceRaw(BaseModel):
    quote: str


class BulletRaw(BaseModel):
    id: str
    action: str
    outcome: str
    metric: str
    evidence: EvidenceRaw


class ExperienceRaw(BaseModel):
    title: str
    company: str
    period: dict
    bullets: List[BulletRaw] = Field(default_factory=list)


class ResumeExtractRaw(BaseModel):
    basics: dict
    hard_skills: List[str] = Field(default_factory=list)
    experiences: List[ExperienceRaw] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    language: Lang
    meta: dict


class JDObjectV1(BaseModel):
    role: str
    company: str
    must_have_skills: List[str] = Field(default_factory=list)
    nice_to_have_skills: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    challenges: List[str] = Field(default_factory=list)
    language: Lang
    jd_unique_terms: List[str] = Field(default_factory=list)
    meta: dict


class CoverPlanWhyMe(BaseModel):
    evidence_id: str
    line: str


class CoverPlanV1(BaseModel):
    opening: dict
    why_me: List[CoverPlanWhyMe] = Field(default_factory=list)
    why_you: dict
    cta: str
    language: Lang

    @validator('why_me')
    def check_whyme_len(cls, v):  # noqa: N805
        if len(v) > 3:
            raise ValueError('why_me must be <= 3 items')
        return v


class AnchorTextV1(BaseModel):
    anchor_sha256: str
    text: str
    doc_version_id: int
