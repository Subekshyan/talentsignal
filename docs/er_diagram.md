# ER diagram (Mermaid)

Renders on GitHub and in most Markdown viewers. Matches `backend/app/models.py`.

```mermaid
erDiagram
  USER ||--|| CANDIDATE_PROFILE : has
  USER ||--o{ CV_DOCUMENT : uploads
  USER ||--o{ JOB_SEARCH_QUERY : saves
  USER ||--o{ MATCH_RUN : requests
  USER ||--o{ JOB_APPLICATION : tracks
  USER ||--o{ NOTIFICATION : receives
  CV_DOCUMENT ||--o{ PARSED_CV_SECTION : contains
  CV_DOCUMENT ||--o{ MATCH_RUN : analyzed_in
  CANDIDATE_PROFILE ||--o{ EDUCATION : lists
  CANDIDATE_PROFILE ||--o{ EXPERIENCE : lists
  CANDIDATE_PROFILE ||--o{ PROJECT : lists
  CANDIDATE_PROFILE ||--o{ CERTIFICATION : lists
  CANDIDATE_PROFILE ||--o{ CANDIDATE_SKILL : claims
  SKILL ||--o{ CANDIDATE_SKILL : referenced_by
  SKILL |o--o{ JOB_REQUIREMENT : normalizes
  SKILL |o--o{ SKILL_GAP : names
  COMPANY ||--o{ JOB_LISTING : posts
  JOB_SOURCE ||--o{ JOB_LISTING : provides
  JOB_LISTING ||--o{ JOB_REQUIREMENT : has
  JOB_LISTING ||--o{ MATCH_RUN : target_of
  JOB_LISTING ||--o{ JOB_APPLICATION : tracked_as
  JOB_LISTING |o--o{ NOTIFICATION : about
  MATCH_RUN ||--o{ REQUIREMENT_MATCH : produces
  JOB_REQUIREMENT ||--o{ REQUIREMENT_MATCH : evaluated_in
  REQUIREMENT_MATCH ||--o{ MATCH_EVIDENCE : backed_by
  PARSED_CV_SECTION |o--o{ MATCH_EVIDENCE : cited_as
  MATCH_RUN ||--o{ SKILL_GAP : reveals
  SKILL_GAP ||--o{ RECOMMENDATION : addressed_by
```

Column details are in `backend/app/models.py`.

## System design (text)
React frontend -> FastAPI backend (auth/profile, CV parsing, JD matching, tracking) -> PostgreSQL + private CV storage.
A separate scheduled discovery worker (search API -> page fetch -> extract -> dedupe -> store) writes job listings into PostgreSQL.
