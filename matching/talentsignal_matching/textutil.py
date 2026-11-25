"""Small text helpers."""
from __future__ import annotations

import re

BULLET = re.compile(r"^\s*(?:[-*•▪●◦]|\d+[.)])\s+")


def clean_line(line: str) -> str:
    return BULLET.sub("", line).strip()


def is_bullet(line: str) -> bool:
    return bool(BULLET.match(line))


def split_units(text: str) -> list[str]:
    """Split text into evidence-sized units (bullets / sentences)."""
    units: list[str] = []
    for raw in text.splitlines():
        line = clean_line(raw)
        if not line:
            continue
        parts = re.split(r"(?<=[.!?])\s+(?=[A-Z])", line)
        units.extend(p.strip() for p in parts if p.strip())
    return units
