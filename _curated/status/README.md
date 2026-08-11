# Curation status checkpoint

## Purpose

`_curated/status/` contains a **small operational checkpoint**, not a per-record curation ledger and not engineering truth.

The scalable source of curation eligibility is each staging record's own `status`. Do not mirror every staging record here.

## `curation-status.md`

Keep only the latest useful checkpoint, for example:

- last curation run/date;
- last staging record(s) consumed/considered;
- last outcome;
- curated target(s) touched;
- related Atlas PR/MR when known;
- a short blocker/coverage note if useful.

Merge order naturally determines which checkpoint is latest. Historical publication and human-review detail already exists in Git and the Atlas PR/MR.

## Separation of responsibilities

| Record | Responsibility |
|---|---|
| staging entry | raw evidence plus its own lifecycle status |
| curated concept page | engineering knowledge and evidence-backed meaning |
| Atlas PR/MR | later publication and human-review/audit trail |
| `_curated/status/curation-status.md` | latest operational checkpoint only |
| `log.md` | significant Atlas-level milestones only |

## Lifecycle source of truth

Do not use this file to decide whether a staging record is eligible. Use the staging record's status:

- `new` — eligible;
- `curating` — active/in progress;
- `consumed`, `no-change`, `deferred`, `rejected` — not automatically eligible.

The checkpoint may summarise the latest consumed record and outcome, but it is informational and must never become an ordering cursor. Staging can be processed out of chronological order and new findings can arrive independently of code changes.

## Maintenance

`atlas-curate` may update this checkpoint as part of a curation run. Keep it compact and overwrite the latest checkpoint rather than appending an unbounded history.
