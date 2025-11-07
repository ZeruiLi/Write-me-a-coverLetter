from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel

import google.generativeai as genai  # type: ignore


class ResumeExtractRaw(BaseModel):
    basics: dict
    hard_skills: list[str]
    experiences: list[dict]
    education: list[dict]
    language: str
    meta: dict


class JDObjectV1(BaseModel):
    role: str
    company: str
    must_have_skills: list[str]
    nice_to_have_skills: list[str]
    responsibilities: list[str]
    challenges: list[str]
    language: str
    jd_unique_terms: list[str]
    meta: dict


app = FastAPI(title="filecap-service")


def _model() -> Any:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY missing")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("models/gemini-1.5-pro")


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.post("/extract/resume_file")
async def extract_resume_file(file: UploadFile = File(...)):
    m = _model()
    uploaded = genai.upload_file(file.file, mime_type=file.content_type)
    prompt = (
        "Output STRICT JSON with fields: basics{name,email,phone,location}, hard_skills[], experiences["
        "{title,company,period:{start,end}, bullets[{id,action,outcome,metric,evidence:{quote}}]}], education["
        "{school,degree,graduation}], language('zh'|'en'), meta{}"
    )
    resp = m.generate_content([{ "file_data": {"file_uri": uploaded.uri}}, {"text": prompt}])
    return ResumeExtractRaw.model_validate_json(resp.text or "{}")


@app.post("/extract/jd_file")
async def extract_jd_file(file: UploadFile = File(...)):
    m = _model()
    uploaded = genai.upload_file(file.file, mime_type=file.content_type)
    prompt = (
        "Output STRICT JSON with fields: role, company, must_have_skills[], nice_to_have_skills[], responsibilities[], challenges[], language('zh'|'en'), jd_unique_terms[], meta{}"
    )
    resp = m.generate_content([{ "file_data": {"file_uri": uploaded.uri}}, {"text": prompt}])
    return JDObjectV1.model_validate_json(resp.text or "{}")

