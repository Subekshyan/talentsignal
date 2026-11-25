"""CV-to-JD matching engine.

Methods (for baseline comparison in your evaluation):
  keyword : skill dictionary only
  tfidf   : TF-IDF cosine similarity only (no dictionary)
  sbert   : Sentence-BERT similarity only (no dictionary)
  hybrid  : dictionary first, then SBERT (TF-IDF fallback) for what is left
"""
from __future__ import annotations

import datetime as dt

from . import scoring
from .cv_parser import CVUnit, ParsedCV, parse_cv
from .jd_parser import degree_fields, degree_level, parse_jd
from .models import (MATCHED, NEEDS_REVIEW, NOT_DEMONSTRATED, PARTIAL, Evidence,
                     MatchReport, Requirement, RequirementMatch)
from .recommend import recommend
from .similarity import Backend, get_backend
from .skills import SKILLS, mentions_skill

METHODS = ("keyword", "tfidf", "sbert", "hybrid")
TOP_EVIDENCE = 3


def _evidence(units: list[CVUnit], sims: list[float], method: str, k: int = TOP_EVIDENCE) -> list[Evidence]:
    ranked = sorted(range(len(units)), key=lambda i: sims[i], reverse=True)[:k]
    return [Evidence(units[i].text, units[i].section, round(sims[i], 3), method) for i in ranked if sims[i] > 0]


def _query_for(req: Requirement) -> str:
    return req.skill if req.skill else req.text


def _match_skill_keyword(req: Requirement, cv: ParsedCV) -> RequirementMatch | None:
    hits = [u for u in cv.units if mentions_skill(u.text, req.skill)]
    if not hits:
        return None
    ev = [Evidence(u.text, u.section, 1.0, "keyword") for u in hits[:TOP_EVIDENCE]]
    in_context = any(u.section not in ("skills", "header") for u in hits)
    if in_context:
        return RequirementMatch(req, MATCHED, 0.9, ev)
    return RequirementMatch(req, MATCHED, 0.7, ev,
                            note="Listed in your skills section; add a project or job bullet showing how you used it.")


def _match_by_similarity(req: Requirement, cv: ParsedCV, backend: Backend) -> RequirementMatch:
    sims = backend.similarities(_query_for(req))
    if not sims:
        return RequirementMatch(req, NOT_DEMONSTRATED, 0.0)
    best = max(sims)
    ev = _evidence(cv.units, sims, backend.name)
    if best >= backend.matched_at:
        return RequirementMatch(req, MATCHED, round(best, 3), ev, note=f"Semantic match ({backend.name}); verify the evidence.")
    if best >= backend.partial_at:
        return RequirementMatch(req, PARTIAL, round(best, 3), ev, note="Related wording found, but not a clear match.")
    return RequirementMatch(req, NOT_DEMONSTRATED, round(best, 3), [])


def _match_experience(req: Requirement, cv: ParsedCV) -> RequirementMatch:
    emp, intern = cv.employment_months / 12, cv.internship_months / 12
    need = req.min_years or 0
    ev = [Evidence(u.text, u.section, 1.0, "dates") for u in cv.units if u.section == "experience"][:TOP_EVIDENCE]
    if emp >= need:
        return RequirementMatch(req, MATCHED, 0.8, ev, note=f"~{emp:.1f} years of dated employment found.")
    if emp + intern >= need:
        return RequirementMatch(req, NEEDS_REVIEW, 0.5, ev,
                                note=f"Meets {need:g} years only if internships count (~{intern:.1f} years internship).")
    if emp + intern > 0:
        return RequirementMatch(req, PARTIAL, 0.5, ev,
                                note=f"~{emp + intern:.1f} years found vs {need:g} required; verify dates.")
    return RequirementMatch(req, NOT_DEMONSTRATED, 0.0, [],
                            note="No dated work experience found. Projects are not counted as employment.")


def _match_education(req: Requirement, cv: ParsedCV) -> RequirementMatch:
    lines = cv.education_lines
    if not lines:
        return RequirementMatch(req, NOT_DEMONSTRATED, 0.0, [], note="No education section found.")
    best_level = max((degree_level(l) or 0 for l in lines), default=0)
    ev = [Evidence(l, "education", 1.0, "education") for l in lines[:TOP_EVIDENCE]]
    if best_level < (req.degree_level or 0):
        return RequirementMatch(req, NOT_DEMONSTRATED, 0.0, ev, note="Degree level not shown at the required level.")
    cand_fields = {f for l in lines for f in degree_fields(l)}
    related_ok = "related" in req.text.lower()
    if not req.fields or (cand_fields & set(req.fields)) or (related_ok and cand_fields):
        return RequirementMatch(req, MATCHED, 0.85, ev)
    return RequirementMatch(req, NEEDS_REVIEW, 0.5, ev,
                            note="Degree level is met, but the field of study could not be confirmed.")


def analyze(cv_text: str, jd_text: str, method: str = "hybrid", today: dt.date | None = None) -> MatchReport:
    if method not in METHODS:
        raise ValueError(f"method must be one of {METHODS}")
    cv = parse_cv(cv_text, today)
    reqs = parse_jd(jd_text)
    warnings: list[str] = []

    use_keywords = method in ("keyword", "hybrid")
    backend: Backend | None = None
    if method in ("tfidf", "sbert", "hybrid"):
        wanted = "tfidf" if method == "tfidf" else "sbert"
        try:
            backend = get_backend(wanted)
            backend.fit([u.text for u in cv.units], [_query_for(r) for r in reqs])
        except Exception as exc:  # sbert missing or model not downloadable
            if method == "hybrid":
                warnings.append(f"SBERT unavailable ({exc}); using TF-IDF as the similarity fallback.")
                backend = get_backend("tfidf")
                backend.fit([u.text for u in cv.units], [_query_for(r) for r in reqs])
            else:
                raise

    matches: list[RequirementMatch] = []
    for req in reqs:
        m: RequirementMatch | None = None
        if req.kind == "experience":
            m = _match_experience(req, cv)
        elif req.kind == "education":
            m = _match_education(req, cv)
        elif req.kind == "skill":
            if use_keywords:
                m = _match_skill_keyword(req, cv)
            if m is None and backend is not None:
                m = _match_by_similarity(req, cv, backend)
            if m is None:
                m = RequirementMatch(req, NOT_DEMONSTRATED, 0.0)
        else:  # other (free-text requirement)
            if backend is not None:
                m = _match_by_similarity(req, cv, backend)
            else:
                m = RequirementMatch(req, NEEDS_REVIEW, 0.0, [],
                                     note="Free-text requirement; needs a semantic method or manual review.")
        matches.append(m)

    return MatchReport(
        method=method,
        score=scoring.suitability(matches),
        counts=scoring.counts(matches),
        by_kind=scoring.by_kind(matches),
        matches=matches,
        recommendations=recommend(matches),
        warnings=warnings,
    )
