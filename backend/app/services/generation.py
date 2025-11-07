from __future__ import annotations

from typing import Tuple

from ..providers.gemini import GeminiProvider


def truncate_chars(text: str, limit: int) -> str:
    return (text or "")[:limit]


def short_answer(resume_snap: dict, jd: dict, question: str, lang: str, params: dict, provider: GeminiProvider) -> Tuple[str, dict]:
    # If provider is usable, ask LLM; else heuristic
    prompt = (
        f"Question: {question}\nLanguage: {lang}\n"
        "Constraints: single paragraph, <=200 characters, no Markdown or HTML.\n"
        f"Resume snapshot: {resume_snap}\nJob: {jd}\n"
        "Answer succinctly."
    )
    timings = {}
    try:
        content = provider.generate(prompt)
    except Exception:
        # Fallback: deterministic text from summary and role
        role = jd.get("role") if isinstance(jd, dict) else None
        summary = resume_snap.get("summary") or "Experienced candidate"
        base = f"Applying for {role or 'the role'}. {summary}"
        content = base
    return truncate_chars(content.replace("\n", " "), 200), timings


def letter(resume_snap: dict, jd: dict, params: dict, provider: GeminiProvider) -> Tuple[str, dict]:
    lang = params.get("language", "auto")
    style = params.get("style", "Formal")
    paragraphs_max = int(params.get("paragraphs_max", 5))
    target_words = int(params.get("target_words", 400))
    include = params.get("include_keywords", [])
    avoid = params.get("avoid_keywords", [])

    prompt = (
        f"Write a cover letter in {lang} with style {style}. Paragraphs <= {paragraphs_max}, target words {target_words}.\n"
        f"Must include keywords: {include}. Avoid keywords: {avoid}.\n"
        "Output semantic HTML only (<header>,<main>,<section>,<p>,<footer>), no Markdown.\n"
        f"Resume snapshot: {resume_snap}\nJob: {jd}\n"
    )
    timings = {}
    try:
        content = provider.generate(prompt)
        if not content.strip().startswith("<"):
            # not HTML, fallback to simple HTML
            raise ValueError("Non-HTML response")
    except Exception:
        # Fallback HTML template
        name = resume_snap.get("name") or "Candidate"
        contact = resume_snap.get("contact") or {}
        header_line = " | ".join(str(x) for x in [contact.get("email"), contact.get("phone"), contact.get("location")] if x)
        body = (resume_snap.get("summary") or "I am excited to apply.")
        content = f"""
<header>
  <h1>{name}</h1>
  <p>{header_line}</p>
</header>
<main>
  <section>
    <p>{body}</p>
  </section>
</main>
<footer>
  <p>Sincerely,<br/>{name}</p>
</footer>
""".strip()
    return content, timings

