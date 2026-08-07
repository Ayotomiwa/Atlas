# Curation status

## Purpose

`_curated/status/` tracks **routine operational state of the curation process**. It answers questions such as: what staging evidence was recently considered, which area has a proposal pending, and where is the associated PR/MR or review record?

It does **not** contain authoritative engineering facts.

## `curation-status.md`

Use `curation-status.md` as a compact ledger. A useful row/state entry should identify, where applicable:

- concept area;
- last curation run/date;
- staging evidence considered;
- proposed curated pages;
- review state/outcome;
- coverage note or blocker;
- related PR/MR.

Keep it operational and scan-friendly; detailed reasoning belongs elsewhere.

## Separation from other records

| Record | Responsibility |
|---|---|
| curated concept page | engineering knowledge and evidence-backed meaning |
| `reviews/` | detailed curation decision, accepted/rejected claims and human-review boundary |
| `_curated/status/curation-status.md` | routine curation workflow state |
| `log.md` | significant Atlas-level milestones only |
| staging entry | immutable raw evidence once consumed |

Do not turn an index, staging file or root log into a second status ledger.

## Promotion and rejection state

When staging evidence is curated, deferred, rejected or found conflicting, record the outcome in the review/status workflow. **Do not mutate already-consumed staging evidence to mark the result.** Its immutability is part of the evidence chain.

## Coverage language

Status notes may say that an area is incomplete, blocked or awaiting evidence. They must not imply engineering truth from workflow state. For example, `no proposal yet` means only that curation has not produced a proposal; it does not mean the dependency or concept does not exist.

## Maintenance

`atlas-curate` should update routine curation status as part of a non-trivial proposal. Keep stale/closed entries understandable enough that a reviewer can follow the evidence → proposal → review path without using this file as the source of the underlying engineering claim.
