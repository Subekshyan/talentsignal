# Labelling guide (draft v0)

Goal: build human labels to evaluate requirement matching. Two people should label a subset so you can report agreement.

## Unit of labelling
One row = one (job requirement, CV) pair.

## Labels
| Label | Use when |
|-------|----------|
| `matched` | The CV clearly shows the requirement, ideally with use in a project or job (not just a skills list). |
| `partial` | Related or weaker evidence: skills-list only for a "hands-on" requirement, related tool, less experience than asked. |
| `needs_review` | Evidence exists but depends on something unclear (dates missing, internship vs job, degree equivalence). |
| `not_demonstrated` | No clear evidence in the CV. This does NOT mean the person lacks the skill. |

## Rules to decide up front
- **Experience:** academic projects do not count as paid employment. Internships are tracked separately; say in the label notes whether they were counted.
- **Skills list only:** a bare mention in a Skills section is `matched` for a plain skill requirement, `partial` if the job asks for hands-on or years of use.
- **Related tools** (e.g. Power BI vs Tableau when the job says "or"): treat "X or Y" as satisfied by either.
- **Degree equivalence:** record `needs_review` and explain rather than guessing.

## File format (data/labels.csv)
`job_id,cv_id,requirement_text,requirement_type,mandatory,label,evidence_text,annotator,notes`

## Privacy
- Only use CVs with written consent. Remove names, phone numbers, emails, addresses and photos before storing them in `data/`.
- Keep anything identifiable out of git (see .gitignore).
