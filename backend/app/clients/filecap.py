from __future__ import annotations

import os
from typing import Any

import requests

from ..schemas.extract import ResumeExtractRaw, JDObjectV1


class FilecapUnavailable(Exception):
    pass


def _base_url() -> str:
    url = os.getenv("FILECAP_URL")
    if not url:
        raise FilecapUnavailable("FILECAP_URL not set")
    return url.rstrip("/")


def extract_resume_file(path: str, prompt_version: str = "v1") -> ResumeExtractRaw:
    url = _base_url() + "/extract/resume_file"
    try:
        with open(path, "rb") as f:
            resp = requests.post(url, files={"file": (os.path.basename(path), f)}, timeout=60)
    except Exception as e:
        raise FilecapUnavailable(str(e))
    if resp.status_code != 200:
        raise FilecapUnavailable(f"filecap error: {resp.status_code} {resp.text}")
    data = resp.json()
    return ResumeExtractRaw(**data)


def extract_jd_file(path: str, prompt_version: str = "v1") -> JDObjectV1:
    url = _base_url() + "/extract/jd_file"
    try:
        with open(path, "rb") as f:
            resp = requests.post(url, files={"file": (os.path.basename(path), f)}, timeout=60)
    except Exception as e:
        raise FilecapUnavailable(str(e))
    if resp.status_code != 200:
        raise FilecapUnavailable(f"filecap error: {resp.status_code} {resp.text}")
    data = resp.json()
    return JDObjectV1(**data)

