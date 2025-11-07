from __future__ import annotations

from typing import Any, Dict

from ..providers.gemini import GeminiProvider


def build_parse_chain(provider: GeminiProvider):
    # Placeholder for LCEL chain; return provider for now
    return provider


def parse_resume(text: str, meta: dict, provider: GeminiProvider) -> Dict[str, Any]:
    # Try LLM-based parsing if possible; fallback to heuristic
    snapshot = {
        "name": None,
        "contact": {"email": None, "phone": None, "location": None},
        "links": {},
        "summary": None,
        "skills": [],
        "experiences": [],
        "education": [],
        "language": meta.get("language"),
        "source": {"file_path": meta.get("file_path"), "sha256": meta.get("sha256")},
    }

    prompt = (
        "Extract structured resume fields as strict JSON with keys: name, contact{email,phone,location},"
        " links(object), summary, skills(array of strings), experiences(array of {company,role,start,end,bullets}),"
        " education(array of {school,degree,graduation}). Only output JSON.\n\nResume text: \n" + (text[:8000] if text else "")
    )
    try:
        chain = build_parse_chain(provider)
        content = chain.generate(prompt)
        import json

        data = json.loads(content)
        snapshot.update({k: v for k, v in data.items() if k in snapshot})
        return snapshot
    except Exception:
        # Heuristic fallback: pick first lines as summary
        lines = (text or "").splitlines()
        summary = " ".join(lines[:5]).strip() if lines else None
        snapshot["summary"] = summary
        return snapshot

