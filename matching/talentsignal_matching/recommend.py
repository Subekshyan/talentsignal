"""Job-specific recommendations. Never tells the user to claim what they lack."""
from __future__ import annotations

from .models import NEEDS_REVIEW, NOT_DEMONSTRATED, PARTIAL, RequirementMatch
from .scoring import active_matches


def recommend(matches: list[RequirementMatch]) -> list[str]:
    recs: list[str] = []
    for m in active_matches(matches):
        r = m.requirement
        label = r.skill or r.text
        tag = "required" if r.mandatory else "preferred"
        if m.status == NOT_DEMONSTRATED:
            if r.kind == "skill":
                recs.append(
                    f"[{tag}] {label}: no clear evidence in your CV. If you have genuinely used it, "
                    f"add a project or bullet showing how. If not, consider learning it with a small project."
                )
            elif r.kind == "experience":
                recs.append(
                    f"[{tag}] Experience requirement ({r.text}): no dated work found. Add dates to real "
                    f"internships or jobs; academic projects are shown separately from paid experience."
                )
            elif r.kind == "education":
                recs.append(f"[{tag}] Education requirement ({r.text}): your CV does not clearly show it.")
            else:
                recs.append(f"[{tag}] '{r.text}': your CV shows no clear evidence for this.")
        elif m.status in (PARTIAL, NEEDS_REVIEW):
            recs.append(f"[{tag}] {label}: {m.note or 'only partly supported; review the evidence and clarify your CV if accurate.'}")
    return recs
