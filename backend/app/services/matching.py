from __future__ import annotations

from typing import Dict, List


def extract_keywords(text: str) -> List[str]:
    import re
    words = re.findall(r"[A-Za-zA-Z\u4e00-\u9fa5]{2,}", text or "")
    # naive top unique
    uniq = []
    for w in words:
        wl = w.lower()
        if wl not in uniq:
            uniq.append(wl)
        if len(uniq) >= 30:
            break
    return uniq


def score_match(resume_snapshot: Dict, jd: Dict) -> Dict:
    rskills = set([s.lower() for s in (resume_snapshot.get("skills") or [])])
    jkeys = set([k.lower() for k in (jd.get("keywords") or [])])
    overlap = sorted(rskills.intersection(jkeys))
    return {"overlap": overlap, "score": len(overlap)}

