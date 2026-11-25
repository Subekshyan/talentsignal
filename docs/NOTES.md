# Known gaps and decisions (keep this honest)

## Not yet done in the matching engine
- **Evidence double-counting:** the same CV sentence can support several requirements and is counted each time. The brief asks to avoid this; design and test a rule on real data.
- **Thresholds are placeholders** (`similarity.py`). TF-IDF 0.35 / 0.15 and SBERT 0.55 / 0.40 were not tuned. Tune on the labelled set.
- **SBERT is untested here.** The code path exists; install `sentence-transformers` and run `--method sbert` / `hybrid` yourself. Without it, `hybrid` falls back to TF-IDF and warns.
- **Skill dictionary is a starter list** (~40 skills). Grow it from real Nepali job descriptions.
- **Experience duration is approximate:** year-only dates count from January; overlapping roles are summed; "intern" is detected by keyword.
- **Soft skills** (e.g. communication) are matched by keyword only and are weak signals.
- **Plain text only.** PDF/DOCX extraction is Phase 2.
- **English only.**

## Not yet done elsewhere
- Backend: no auth, uploads, or persistence of match runs yet (models exist; endpoints do not). Docker files are written but untested.
- No Alembic migrations (tables created with `create_all` for dev).
- Frontend and discovery worker are empty placeholders.

## Decisions
- `SuitabilityScore` is stored on `MatchRun`; `SavedJob` is the first status of `JobApplication`.
- "X or Y" requirements are grouped (`alt_group`): the best-supported alternative counts.
- Scoring: matched 1.0, partial 0.5, needs_review 0.25, not_demonstrated 0; mandatory weight 2, preferred 1. Preliminary.
