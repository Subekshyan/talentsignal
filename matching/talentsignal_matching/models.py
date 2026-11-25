"""Data structures shared by the matching engine."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

MATCHED = "matched"
PARTIAL = "partial"
NEEDS_REVIEW = "needs_review"
NOT_DEMONSTRATED = "not_demonstrated"

DISCLAIMER = (
    "This score estimates how closely the evidence in your CV lines up with this job. "
    "It is not a probability of being hired. 'Not demonstrated' means your CV shows no "
    "clear evidence, not that you lack the skill."
)


@dataclass
class Requirement:
    id: str
    text: str
    kind: str  # skill | experience | education | other
    mandatory: bool = True
    skill: str | None = None
    min_years: float | None = None
    degree_level: int | None = None
    fields: list[str] = field(default_factory=list)
    alt_group: str | None = None  # "Power BI or Tableau": satisfying one satisfies the group


@dataclass
class Evidence:
    text: str
    section: str
    score: float
    method: str  # keyword | tfidf | sbert | dates | education


@dataclass
class RequirementMatch:
    requirement: Requirement
    status: str
    confidence: float
    evidence: list[Evidence] = field(default_factory=list)
    note: str = ""


@dataclass
class MatchReport:
    method: str
    score: float
    counts: dict[str, int]
    by_kind: dict[str, float]
    matches: list[RequirementMatch]
    recommendations: list[str]
    warnings: list[str] = field(default_factory=list)
    disclaimer: str = DISCLAIMER

    def to_dict(self) -> dict:
        return asdict(self)
