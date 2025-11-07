from __future__ import annotations

from typing import List, Set

from ..schemas.extract import ResumeObjectV1, JDObjectV1, CoverPlanWhyMe


def _norm(s: str) -> str:
    return (s or "").lower()


def select_why_me(resume: ResumeObjectV1, jd: JDObjectV1, k: int = 3) -> List[CoverPlanWhyMe]:
    must = {_norm(x) for x in (jd.must_have_skills or [])}
    nice = {_norm(x) for x in (jd.nice_to_have_skills or [])}
    chosen: List[CoverPlanWhyMe] = []
    seen_ids: Set[str] = set()

    def score_bullet(line: str) -> int:
        ln = _norm(line)
        sc = 0
        sc += sum(1 for m in must if m and m in ln) * 3
        sc += sum(1 for n in nice if n and n in ln)
        return sc

    candidates: List[tuple[int, CoverPlanWhyMe]] = []
    for exp in resume.experiences:
        for b in exp.bullets:
            line = f"{b.action} → {b.outcome} ({b.metric})"
            cand = CoverPlanWhyMe(evidence_id=b.id, line=line)
            candidates.append((score_bullet(line), cand))

    candidates.sort(key=lambda x: x[0], reverse=True)
    for sc, cand in candidates:
        if cand.evidence_id in seen_ids:
            continue
        chosen.append(cand)
        seen_ids.add(cand.evidence_id)
        if len(chosen) >= k:
            break
    return chosen

