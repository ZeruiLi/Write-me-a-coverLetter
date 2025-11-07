from typing import List, Optional, Literal, Union
from pydantic import BaseModel, Field
from .job import JobNormalized


Question = Literal['why_company','why_you','biggest_achievement']
LangOpt = Literal['auto','zh','en']
Style = Literal['Formal','Warm','Tech']


class GenerateShortRequest(BaseModel):
    resumeId: int
    job: Union[dict, JobNormalized]
    question: Question
    language: LangOpt = 'auto'


class GenerateShortResponse(BaseModel):
    genId: int
    text: str


class GenerateLetterRequest(BaseModel):
    resumeId: int
    job: Union[dict, JobNormalized]
    style: Style = 'Formal'
    paragraphs_max: int = Field(default=5, ge=1, le=7)
    target_words: int = Field(default=400, ge=200, le=700)
    include_keywords: List[str] = Field(default_factory=list)
    avoid_keywords: List[str] = Field(default_factory=list)
    language: LangOpt = 'auto'
    format: Literal['html','md'] = 'html'


class GenerateLetterResponse(BaseModel):
    genId: int
    format: Literal['html','md']
    content: str
    meta: dict

