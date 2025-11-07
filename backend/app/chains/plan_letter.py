from __future__ import annotations

from typing import List

from ..schemas.extract import ResumeObjectV1, JDObjectV1, CoverPlanV1, CoverPlanWhyMe


def plan_letter(resume: ResumeObjectV1, jd: JDObjectV1, lang: str) -> CoverPlanV1:
    # naive auto-pick up to 3 bullets
    chosen: List[CoverPlanWhyMe] = []
    for exp in resume.experiences:
        for b in exp.bullets:
            if len(chosen) < 3:
                chosen.append(CoverPlanWhyMe(evidence_id=b.id, line=f"{b.action} → {b.outcome} ({b.metric})"))
    opening = {"company": jd.company, "role": jd.role, "hook": ""}
    why_you = {"focus_points": (jd.challenges or jd.responsibilities or [])[:3]}
    cta = "I would be glad to walk through relevant projects."
    return CoverPlanV1(opening=opening, why_me=chosen, why_you=why_you, cta=cta, language=lang)  # type: ignore

