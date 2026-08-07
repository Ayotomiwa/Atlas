# TeamA Atlas — Claude operating rules

This repository is the TeamA Atlas package (`teama`). It is a governed engineering context layer, not a general document dump.

## Trust
- `_staging/` is raw evidence and is never authoritative.
- `_curated/` is reviewed knowledge; only `status: curated` is authoritative.
- Claude may stage and propose; Claude never self-approves or merges knowledge.
- Never invent missing engineering context.

## How repository rules are organised
- `package.md` defines package identity and entrypoints.
- `index.md` files route to existing knowledge.
- A target folder's `README.md` defines semantic, granularity, evidence and reviewer rules.
- A target folder's `_template.md` defines page shape.
- Skills in `.claude/skills/` define workflows.

## Editing Atlas
- Before curating into a folder, read that folder's `README.md`, `_template.md`, and `index.md`.
- Edit relationships only on curated Markdown pages.
- Never hand-edit generated relationship data in `_curated/maps/*.json`.
- After relationship changes run `python scripts/rebuild_maps.py`.
- Before proposing changes run `python scripts/atlas_lint.py .` and tests.
- Once staging evidence has been referenced by curation, do not alter or move it. Add new corrective evidence instead.

## Navigation
Do not read the entire Atlas repository. Start from `index.md` or the relevant skill and open the smallest useful set of files.

## Operational records
- routine curation state → `_curated/status/curation-status.md`
- detailed curation reasoning → `reviews/`
- significant Atlas milestones only → `log.md`
