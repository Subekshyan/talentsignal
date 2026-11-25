"""Controlled vocabulary of skills (starter list, IT/data focus).

Extend this as you read real Nepali job descriptions. Aliases are matched
case-insensitively on word boundaries.
"""
from __future__ import annotations

import re

SKILLS: dict[str, dict] = {
    # languages
    "python": {"category": "technical", "aliases": ["python"]},
    "sql": {"category": "technical", "aliases": ["sql", "structured query language"]},
    "java": {"category": "technical", "aliases": ["java"]},
    "javascript": {"category": "technical", "aliases": ["javascript", "js", "node.js", "nodejs"]},
    "r": {"category": "technical", "aliases": ["r programming", "rstudio"]},
    # data
    "pandas": {"category": "technical", "aliases": ["pandas"]},
    "numpy": {"category": "technical", "aliases": ["numpy"]},
    "statistics": {"category": "technical", "aliases": ["statistics", "statistical analysis", "hypothesis testing"]},
    "data cleaning": {"category": "technical", "aliases": ["data cleaning", "data preprocessing", "data wrangling", "data preparation"]},
    "data visualization": {"category": "technical", "aliases": ["data visualization", "data visualisation", "dashboards", "dashboard", "matplotlib", "seaborn", "plotly"]},
    "power bi": {"category": "technical", "aliases": ["power bi", "powerbi"]},
    "tableau": {"category": "technical", "aliases": ["tableau"]},
    "excel": {"category": "technical", "aliases": ["excel", "microsoft excel", "spreadsheets"]},
    # ML / AI
    "machine learning": {"category": "technical", "aliases": ["machine learning", "predictive modelling", "predictive modeling", "classification", "regression"]},
    "deep learning": {"category": "technical", "aliases": ["deep learning", "neural network", "neural networks"]},
    "nlp": {"category": "technical", "aliases": ["nlp", "natural language processing", "text mining"]},
    "scikit-learn": {"category": "technical", "aliases": ["scikit-learn", "sklearn"]},
    "tensorflow": {"category": "technical", "aliases": ["tensorflow", "keras"]},
    "pytorch": {"category": "technical", "aliases": ["pytorch"]},
    "spacy": {"category": "technical", "aliases": ["spacy"]},
    # engineering
    "fastapi": {"category": "technical", "aliases": ["fastapi"]},
    "django": {"category": "technical", "aliases": ["django"]},
    "flask": {"category": "technical", "aliases": ["flask"]},
    "react": {"category": "technical", "aliases": ["react", "reactjs", "react.js"]},
    "rest api": {"category": "technical", "aliases": ["rest api", "rest apis", "restful", "api development"]},
    "git": {"category": "technical", "aliases": ["git", "github", "gitlab"]},
    "docker": {"category": "technical", "aliases": ["docker", "containerization"]},
    "linux": {"category": "technical", "aliases": ["linux", "unix"]},
    "aws": {"category": "technical", "aliases": ["aws", "amazon web services"]},
    "postgresql": {"category": "technical", "aliases": ["postgresql", "postgres"]},
    "mysql": {"category": "technical", "aliases": ["mysql"]},
    "mongodb": {"category": "technical", "aliases": ["mongodb"]},
    # QA
    "software testing": {"category": "technical", "aliases": ["software testing", "test cases", "test case", "manual testing", "qa testing", "quality assurance"]},
    "selenium": {"category": "technical", "aliases": ["selenium"]},
    "test automation": {"category": "technical", "aliases": ["test automation", "automation testing"]},
    # soft skills
    "communication": {"category": "soft", "aliases": ["communication", "communicate", "presentation skills"]},
    "teamwork": {"category": "soft", "aliases": ["teamwork", "team player", "collaboration", "collaborate"]},
    "problem solving": {"category": "soft", "aliases": ["problem solving", "problem-solving", "analytical skills", "analytical thinking"]},
}


def _compile(alias: str) -> re.Pattern:
    return re.compile(r"(?<![\w+#])" + re.escape(alias) + r"(?![\w+#])", re.IGNORECASE)


_PATTERNS: dict[str, list[re.Pattern]] = {
    name: [_compile(a) for a in info["aliases"]] for name, info in SKILLS.items()
}


def find_skills(text: str) -> set[str]:
    """Return canonical skill names mentioned in `text`."""
    return {name for name, pats in _PATTERNS.items() if any(p.search(text) for p in pats)}


def mentions_skill(text: str, skill: str) -> bool:
    return any(p.search(text) for p in _PATTERNS.get(skill, []))
