
from __future__ import annotations
import argparse
import json
from pathlib import Path

from .engine import METHODS, analyze


def main() -> None:
    p = argparse.ArgumentParser(description="Match a CV against a job description")
    p.add_argument("jd")
    p.add_argument("cv")
    p.add_argument("--method", default="hybrid", choices=METHODS)
    p.add_argument("--json", action="store_true", help="print the full report as JSON")
    a = p.parse_args()

    report = analyze(Path(a.cv).read_text(encoding="utf-8"), Path(a.jd).read_text(encoding="utf-8"), a.method)
    if a.json:
        print(json.dumps(report.to_dict(), indent=2, default=str))
        return

    print(f"Method: {report.method}   Suitability estimate: {report.score}/100")
    print("Counts:", report.counts)
    for w in report.warnings:
        print("WARNING:", w)
    print()
    for m in report.matches:
        r = m.requirement
        tag = "must" if r.mandatory else "pref"
        label = r.skill or r.text[:60]
        print(f"[{m.status:<16}] ({tag}) {r.kind:<10} {label}")
        for e in m.evidence[:1]:
            print(f"      evidence [{e.section}]: {e.text[:90]}")
        if m.note:
            print(f"      note: {m.note}")
    print("\nRecommendations:")
    for rec in report.recommendations:
        print(" -", rec)
    print("\n" + report.disclaimer)


if __name__ == "__main__":
    main()
