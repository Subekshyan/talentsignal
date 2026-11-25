"""Requirement-level scoring.

Weights are preliminary and configurable. They need to be justified and tested
on your evaluation set. Known gap: evidence is not yet de-duplicated across
requirements (see docs/NOTES.md).
"""
from __future__ import annotations

from collections import defaultdict

from .models import MATCHED, NEEDS_REVIEW, NOT_DEMONSTRATED, PARTIAL, RequirementMatch

STATUS_CREDIT = {MATCHED: 1.0, PARTIAL: 0.5, NEEDS_REVIEW: 0.25, NOT_DEMONSTRATED: 0.0}
MANDATORY_WEIGHT = 2.0
PREFERRED_WEIGHT = 1.0


def _weight(m: RequirementMatch) -> float:
    return MANDATORY_WEIGHT if m.requirement.mandatory else PREFERRED_WEIGHT


def active_matches(matches: list[RequirementMatch]) -> list[RequirementMatch]:
    """For 'X or Y' alternatives keep only the best-supported one."""
    best: dict[str, RequirementMatch] = {}
    for m in matches:
        g = m.requirement.alt_group
        if g and (g not in best or STATUS_CREDIT[m.status] > STATUS_CREDIT[best[g].status]):
            best[g] = m
    return [m for m in matches if not m.requirement.alt_group or best[m.requirement.alt_group] is m]


def suitability(matches: list[RequirementMatch]) -> float:
    matches = active_matches(matches)
    total = sum(_weight(m) for m in matches)
    if total == 0:
        return 0.0
    got = sum(_weight(m) * STATUS_CREDIT[m.status] for m in matches)
    return round(100 * got / total, 1)


def by_kind(matches: list[RequirementMatch]) -> dict[str, float]:
    groups: dict[str, list[RequirementMatch]] = defaultdict(list)
    for m in active_matches(matches):
        groups[m.requirement.kind].append(m)
    return {k: suitability(v) for k, v in groups.items()}


def counts(matches: list[RequirementMatch]) -> dict[str, int]:
    out = {MATCHED: 0, PARTIAL: 0, NEEDS_REVIEW: 0, NOT_DEMONSTRATED: 0}
    for m in active_matches(matches):
        out[m.status] += 1
    return out
