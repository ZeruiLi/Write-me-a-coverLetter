from __future__ import annotations

import json
from typing import Tuple

from pydantic import ValidationError

from ..providers.filecapable import FileCapableLLM, ProviderNotFileCapable
from ..schemas.extract import ResumeObjectV1


RESUME_EXTRACT_PROMPT_V1 = (
    "You are a precise information extractor. Read the attached resume file and output STRICT JSON matching this schema:\n"
    "{\n  basics: {name, email, phone, location},\n  hard_skills: string[],\n  experiences: [ {title, company, period:{start,end}, bullets:[{id, action, outcome, metric, evidence:{quote}}] } ],\n  education: [ {school, degree, graduation} ],\n  language: 'zh'|'en',\n  meta: {}\n}\n"
    "Rules:\n- bullets must have measurable AOM (Action/Outcome/Metric) and include exact evidence.quote from the file text.\n"
    "- Output JSON only, no comments."
)


def extract_resume_with_files(llm: FileCapableLLM, file_token: str) -> Tuple[ResumeObjectV1, dict]:
    prompt = RESUME_EXTRACT_PROMPT_V1
    text = llm.generate(prompt, files=[file_token])
    try:
        data = json.loads(text)
        obj = ResumeObjectV1(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        raise ValueError(f"schema_invalid: {e}")
    return obj, {"prompt": prompt}

