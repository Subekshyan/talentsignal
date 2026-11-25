"""Rule-based CV text parser (Phase 1 baseline).

Works on plain text. PDF/DOCX -> text extraction comes in Phase 2
(PyMuPDF, python-docx) and should feed this module.
"""
from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field

from .textutil import clean_line, split_units

SECTION_ALIASES = {
    "skills": ["skills", "technical skills", "core competencies", "key skills"],
    "education": ["education", "academic background", "qualifications"],
    "experience": ["experience", "work experience", "employment", "professional experience", "internship", "internships"],
    "projects": ["projects", "academic projects", "personal projects"],
    "certifications": ["certifications", "certificates", "training", "courses"],
    "summary": ["summary", "profile", "objective", "about me"],
}
_ALIAS_TO_SECTION = {a: s for s, als in SECTION_ALIASES.items() for a in als}

MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
_DATE = r"(?:[A-Za-z]{3,9}\.?\s+)?(?:19|20)\d{2}"
RANGE = re.compile(rf"({_DATE})\s*(?:-|–|—|to)\s*({_DATE}|present|current|now)", re.IGNORECASE)


@dataclass
class CVUnit:
    text: str
    section: str


@dataclass
class ParsedCV:
    sections: dict[str, list[str]]
    units: list[CVUnit]
    employment_months: int = 0
    internship_months: int = 0
    education_lines: list[str] = field(default_factory=list)


def _heading(line: str) -> str | None:
    key = line.strip().strip(":").strip().lower()
    return _ALIAS_TO_SECTION.get(key)


def parse_date(token: str, today: dt.date) -> tuple[int, int]:
    """Return (year, month). Year-only dates use January (conservative)."""
    t = token.strip().lower()
    if t in {"present", "current", "now"}:
        return today.year, today.month
    year = int(re.search(r"(?:19|20)\d{2}", t).group())
    m = re.match(r"[a-z]{3}", t)
    month = MONTHS.get(m.group(), 1) if m else 1
    return year, month


def range_months(start: str, end: str, today: dt.date) -> int:
    y1, m1 = parse_date(start, today)
    y2, m2 = parse_date(end, today)
    return max(0, (y2 - y1) * 12 + (m2 - m1))


def parse_cv(text: str, today: dt.date | None = None) -> ParsedCV:
    today = today or dt.date.today()
    sections: dict[str, list[str]] = {"header": []}
    current = "header"
    for raw in text.splitlines():
        if not raw.strip():
            continue
        h = _heading(clean_line(raw))
        if h:
            current = h
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(raw.rstrip())

    units: list[CVUnit] = []
    for sec, lines in sections.items():
        for u in split_units("\n".join(lines)):
            units.append(CVUnit(text=u, section=sec))

    emp = intern = 0
    exp_lines = sections.get("experience", [])
    for i, line in enumerate(exp_lines):
        m = RANGE.search(line)
        if not m:
            continue
        months = range_months(m.group(1), m.group(2), today)
        context = (exp_lines[i - 1] if i else "") + " " + line
        if "intern" in context.lower():
            intern += months
        else:
            emp += months

    return ParsedCV(
        sections=sections,
        units=units,
        employment_months=emp,
        internship_months=intern,
        education_lines=[clean_line(l) for l in sections.get("education", [])],
    )
