import datetime as dt
from pathlib import Path

import pytest

from talentsignal_matching import analyze
from talentsignal_matching.cv_parser import parse_cv, range_months
from talentsignal_matching.jd_parser import parse_jd
from talentsignal_matching.models import MATCHED, NEEDS_REVIEW, NOT_DEMONSTRATED

SAMPLES = Path(__file__).resolve().parents[2] / "data" / "samples"
JD = (SAMPLES / "jd_data_analyst.txt").read_text()
CV = (SAMPLES / "cv_sample.txt").read_text()
TODAY = dt.date(2026, 11, 20)


def by_label(report):
    return {(m.requirement.skill or m.requirement.kind + ":" + m.requirement.text[:20]): m for m in report.matches}


def test_range_months():
    assert range_months("Jun 2023", "Dec 2023", TODAY) == 6
    assert range_months("2022", "Present", TODAY) == (2026 - 2022) * 12 + 10


def test_jd_parser_splits_required_and_preferred():
    reqs = parse_jd(JD)
    skills = {r.skill: r for r in reqs if r.kind == "skill"}
    assert skills["python"].mandatory and skills["sql"].mandatory
    assert not skills["machine learning"].mandatory
    assert not skills["docker"].mandatory
    # responsibilities section must not become requirements
    assert "weekly reports" not in " ".join(r.text for r in reqs)
    assert any(r.kind == "experience" and r.min_years == 1 for r in reqs)
    assert any(r.kind == "education" for r in reqs)


def test_cv_parser_months_and_sections():
    cv = parse_cv(CV, TODAY)
    assert cv.internship_months == 6 and cv.employment_months == 0
    assert "skills" in cv.sections and "education" in cv.sections


def test_keyword_method_statuses():
    m = by_label(analyze(CV, JD, "keyword", TODAY))
    assert m["python"].status == MATCHED
    assert m["pandas"] if "pandas" in m else True
    assert m["statistics"].status == NOT_DEMONSTRATED          # not in CV
    assert m["power bi"].status == MATCHED                      # in internship bullet
    assert m["machine learning"].status == MATCHED              # regression -> ML alias
    assert m["docker"].status == NOT_DEMONSTRATED
    # 6 months internship vs 1 year required -> not a definitive match
    exp = [x for x in analyze(CV, JD, "keyword", TODAY).matches if x.requirement.kind == "experience"][0]
    assert exp.status != MATCHED


def test_or_alternatives_are_not_double_penalised():
    reqs = parse_jd(JD)
    groups = {r.skill: r.alt_group for r in reqs if r.kind == "skill"}
    assert groups["power bi"] and groups["power bi"] == groups["tableau"]
    r = analyze(CV, JD, "keyword", TODAY)
    # Power BI is evidenced, so Tableau must not count as a missed requirement
    assert "tableau" not in " ".join(r.recommendations).lower()
    assert r.counts[NOT_DEMONSTRATED] == 3  # statistics, communication, docker


def test_skills_only_listing_is_flagged():
    m = by_label(analyze(CV, JD, "keyword", TODAY))
    assert "skills section" in m["sql"].note.lower()


def test_score_in_range_and_disclaimer():
    r = analyze(CV, JD, "keyword", TODAY)
    assert 0 <= r.score <= 100
    assert "not a probability" in r.disclaimer


def test_tfidf_runs():
    r = analyze(CV, JD, "tfidf", TODAY)
    assert 0 <= r.score <= 100


def test_hybrid_falls_back_when_sbert_missing():
    r = analyze(CV, JD, "hybrid", TODAY)
    assert 0 <= r.score <= 100
    try:
        import sentence_transformers  # noqa: F401
    except ImportError:
        assert any("SBERT unavailable" in w for w in r.warnings)


def test_bad_method():
    with pytest.raises(ValueError):
        analyze(CV, JD, "nope")
