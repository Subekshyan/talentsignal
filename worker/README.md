# Discovery worker (Phase 6)

Not started. Pipeline: search API -> page fetch -> extract (Trafilatura/BeautifulSoup) -> parse JD -> dedupe -> store in PostgreSQL.

Before writing any fetching code, record for each source whether automated access is permitted (terms of service and robots.txt) in the `job_sources.allowed` column. Do not fetch from sources where it is not confirmed. Do not bypass logins, CAPTCHAs or paywalls.
