from __future__ import annotations

from typing import Dict

from ..schemas.extract import CoverPlanV1


def generate_letter_html(plan: CoverPlanV1) -> str:
    opening = plan.opening
    why_me_items = plan.why_me
    why_you = plan.why_you
    cta = plan.cta
    html = f"""
<header>
  <h1>Application for {opening.get('role','')} at {opening.get('company','')}</h1>
</header>
<main>
  <section>
    <p>{opening.get('hook','')}</p>
  </section>
  <section>
    <p><strong>Why Me</strong></p>
    {''.join(f'<p data-evidence-id="{w.evidence_id}">{w.line}</p>' for w in why_me_items)}
  </section>
  <section>
    <p><strong>Why You</strong></p>
    {''.join(f'<p>{p}</p>' for p in (why_you.get('focus_points') or []) )}
  </section>
  <section>
    <p>{cta}</p>
  </section>
</main>
<footer></footer>
""".strip()
    return html

