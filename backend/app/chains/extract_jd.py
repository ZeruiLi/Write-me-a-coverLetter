from __future__ import annotations

import json
from typing import Tuple

from pydantic import ValidationError

from ..providers.filecapable import FileCapableLLM
from ..schemas.extract import JDObjectV1


JD_EXTRACT_PROMPT_V1 = (
    "Read the attached job description and output STRICT JSON with this schema:\n"
    "{\n  role:string, company:string, must_have_skills:string[], nice_to_have_skills:string[], responsibilities:string[], challenges:string[], language:'zh'|'en', jd_unique_terms:string[], meta:{}\n}\n"
    "Rules: jd_unique_terms should include at least 3 terms unique to this JD (product names, internal terms). Output JSON only."
)


def extract_jd_with_files(llm, file_token: str) -> Tuple[JDObjectV1, dict]:
    prompt = JD_EXTRACT_PROMPT_V1
    text = llm.generate(prompt, files=[file_token])
    try:
        data = json.loads(text)
        obj = JDObjectV1(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        raise ValueError(f"schema_invalid: {e}")
    return obj, {"prompt": prompt}

