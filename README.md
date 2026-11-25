# TalentSignal

AI-powered job discovery, explainable CV-to-job matching, skill-gap analysis and application tracking. Initial market: Nepal (IT roles first).

The user picks a vacancy, TalentSignal maps each job requirement to evidence in the CV (matched / partial / needs review / not demonstrated), explains the result, suggests job-specific improvements, and tracks everything on a dashboard.

## Quick start (Phase 1: matching engine)

```bash
cd matching
pip install -e ".[dev]"          # add ".[sbert]" for Sentence-BERT
python -m pytest                 # run tests
cd ..
python -m talentsignal_matching.cli data/samples/jd_data_analyst.txt data/samples/cv_sample.txt --method keyword
```

Methods: `keyword`, `tfidf`, `sbert`, `hybrid` (compare these in your evaluation).

## Run the API

```bash
pip install -e matching
pip install -r backend/requirements.txt
cd backend
DATABASE_URL=sqlite:///dev.db uvicorn app.main:app --reload   # then open http://localhost:8000/docs
python -m pytest
```

Or with Postgres: `docker compose up --build` (Docker files are written but not yet tested).

## Layout

```
matching/   engine: JD/CV parsing, keyword + TF-IDF + SBERT matching, scoring, recommendations
backend/    FastAPI app and SQLAlchemy models (docs/er_diagram.md)
worker/     discovery pipeline (Phase 6, not started)
frontend/   React app (Phase 4, not started)
data/       sample fictional JD/CV; real CVs only anonymized and with consent, never in git
docs/       ER diagram, labelling guide, known gaps (NOTES.md)
```

## Design principles
- User chooses the job.
- Evidence before score: every result traces to CV text.
- "Not demonstrated" is not "does not have".
- Show the source and link to the original posting.
- Respect robots.txt, terms of service and rate limits. Never bypass logins, CAPTCHAs or paywalls.
- Protect CVs: consent, minimal retention, user deletion.

## MVP scope (must-have)
1. Account and candidate profile
2. CV upload (PDF/DOCX), parsing, user review of extracted data
3. Job search over one evaluated provider or a few permitted sources, plus a curated fallback dataset
4. Job detail page with original source URL
5. Select a job, run requirement-level CV-to-JD mapping
6. Explainable suitability score with evidence
7. Skill-gap analysis and job-specific recommendations
8. Dashboard: saved / analyzed / applied jobs, skill gaps
9. Basic application status tracking

Out of scope for MVP: auto-apply, scraping every portal, employer accounts, social features.

## Build order
| Phase | Goal | Done when |
|-------|------|-----------|
| 0 | Repo, environment, dataset plan | Repo runs; labelling guide written |
| 1 | Matching prototype | Rule, TF-IDF, SBERT and hybrid compared on a labelled set |
| 2 | CV parsing | PDF/DOCX -> structured records on real sample CVs |
| 3 | Backend + database | Auth, profile, CV upload, job import, match endpoint |
| 4 | Frontend | Upload, job list, job detail, match result view |
| 5 | Dashboard and tracking | Saved/applied pipeline, recurring gaps |
| 6 | Job discovery | Permitted sources only, scheduled worker |
| 7 | Evaluation and write-up | Metrics, error analysis, human review |

## Evaluation plan
- Extraction: precision, recall, F1
- Requirement matching: precision, recall, F1 on matched / partial / not-demonstrated
- Ranking: Precision@K, MAP, NDCG
- Human review of explanations; baseline comparison; error analysis

## Status
Phase 0 done (structure, labelling guide). Phase 1 started: baseline engine works on sample data, not yet evaluated on a real labelled set. See `docs/NOTES.md` for known gaps.
