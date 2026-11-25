"""Rule-based job description -> structured requirements."""
from __future__ import annotations

import re

from .models import Requirement
from .skills import find_skills
from .textutil import clean_line, is_bullet

PREFERRED_HINTS = ("preferred", "nice to have", "good to have", "bonus", "advantage", "a plus", "is a plus")
REQUIRED_HINTS = ("requirement", "qualification", "must have", "what you", "you have", "skills", "you bring", "who you are")
SKIP_HINTS = ("responsibilit", "about", "what we offer", "benefit", "who we are", "how to apply", "duties")

YEARS = re.compile(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:-\s*\d+\s*)?years?", re.IGNORECASE)

DEGREE_LEVELS = [
    (4, re.compile(r"\b(phd|doctorate)\b", re.I)),
    (3, re.compile(r"\b(master'?s?|msc|m\.sc|mba|m\.tech)\b", re.I)),
    (2, re.compile(r"\b(bachelor'?s?|bsc|b\.sc|b\.e|b\.tech|bit|bca|bbs)\b", re.I)),
    (1, re.compile(r"\b(diploma|plus two|\+2)\b", re.I)),
]
GENERIC_DEGREE = re.compile(r"\bdegree\b", re.I)

FIELDS = [
    "computer science", "computer engineering", "information technology", "software engineering",
    "data science", "statistics", "mathematics", "engineering",
]


def degree_level(text: str) -> int | None:
    for level, pat in DEGREE_LEVELS:
        if pat.search(text):
            return level
    return 2 if GENERIC_DEGREE.search(text) else None


def degree_fields(text: str) -> list[str]:
    low = text.lower()
    return [f for f in FIELDS if f in low]


def _mode_for_heading(line: str) -> str | None:
    low = line.lower()
    if any(h in low for h in PREFERRED_HINTS):
        return "preferred"
    if any(h in low for h in SKIP_HINTS):
        return "skip"
    if any(h in low for h in REQUIRED_HINTS):
        return "required"
    return None


def _is_heading(raw: str) -> bool:
    line = raw.strip()
    if not line or is_bullet(raw):
        return False
    return line.endswith(":") or (len(line) <= 60 and not line.endswith("."))


def parse_jd(text: str) -> list[Requirement]:
    lines = [l for l in text.splitlines() if l.strip()]
    saw_heading = any(_is_heading(l) and _mode_for_heading(l.strip(" :")) for l in lines)
    mode: str | None = None if saw_heading else "required"

    reqs: list[Requirement] = []
    seen_skills: dict[str, Requirement] = {}
    n = 0

    def add(req: Requirement) -> None:
        nonlocal n
        n += 1
        req.id = f"r{n}"
        reqs.append(req)

    for raw in lines:
        if _is_heading(raw):
            new_mode = _mode_for_heading(raw.strip(" :"))
            if new_mode:
                mode = new_mode
            continue
        if mode in (None, "skip"):
            continue
        line = clean_line(raw)
        low = line.lower()
        mandatory = mode == "required" and not any(h in low for h in PREFERRED_HINTS)

        skills = find_skills(line)
        group = None
        if len(skills) > 1 and re.search(r"\bor\b|/", low):
            group = f"g{n}_{len(reqs)}"
        for s in sorted(skills):
            if s in seen_skills:
                if mandatory and not seen_skills[s].mandatory:
                    seen_skills[s].mandatory = True
                continue
            r = Requirement(id="", text=line, kind="skill", mandatory=mandatory, skill=s, alt_group=group)
            seen_skills[s] = r
            add(r)

        ym = YEARS.search(line)
        if ym:
            add(Requirement(id="", text=line, kind="experience", mandatory=mandatory, min_years=float(ym.group(1))))

        lvl = degree_level(line)
        if lvl is not None:
            add(Requirement(id="", text=line, kind="education", mandatory=mandatory,
                            degree_level=lvl, fields=degree_fields(line)))

        if not skills and not ym and lvl is None and len(line) >= 20:
            add(Requirement(id="", text=line, kind="other", mandatory=mandatory))
    return reqs
