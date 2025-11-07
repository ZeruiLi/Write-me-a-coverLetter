from __future__ import annotations

import re
from bs4 import BeautifulSoup  # type: ignore

from ..schemas.extract import CoverPlanV1, JDObjectV1


def _paragraphs(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    return [p.get_text(strip=True) for p in soup.find_all('p')]


def validate_letter(html: str, plan: CoverPlanV1, jd: JDObjectV1) -> None:
    # each paragraph no more than 3 lines (approx by sentence count)
    for p in _paragraphs(html):
        if p.count('.') + p.count('。') > 3:
            raise ValueError('guardrail_failed: paragraph too long')
    # at least one jd unique term present
    terms = set((jd.jd_unique_terms or [])[:5])
    if terms and not any(t in html for t in terms):
        raise ValueError('guardrail_failed: no jd unique term')
    # evidence id presence in HTML
    for item in plan.why_me:
        if f'data-evidence-id="{item.evidence_id}"' not in html:
            raise ValueError('guardrail_failed: missing evidence id in html')

