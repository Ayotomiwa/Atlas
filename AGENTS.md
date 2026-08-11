# TeamA Atlas — Codex operating rules

This repository is the TeamA Atlas package (`teama`). It is a governed engineering context layer, not a general document dump.

## Trust
- `_staging/` is raw evidence and is never authoritative.
- `_curated/` is reviewed knowledge; only human-reviewed, merged `status: curated` content is authoritative.
- Codex may stage and propose; Codex never self-approves or merges knowledge.
- Never invent missing engineering context.

## How repository rules are organised
- `atlas-package.json` defines machine package identity, domains and entrypoints; known-package lookups may route directly to maps/indexes/pages.
- `index.md` files route to existing knowledge.
- A target folder's `README.md` defines semantic, granularity, evidence and reviewer rules.
- A target folder's `_template.md` defines page shape.
- Codex skills in `.agents/skills/` define workflows; specialist agent profiles live in `.codex/agents/`.

## Editing Atlas
- Before curating into a folder, read that folder's `README.md`, `_template.md`, and `index.md`.
- Edit structured routing fields only on curated Markdown pages.
- Never hand-edit generated map data below `_curated/maps/`.
- After structured routing changes run `python scripts/rebuild_atlas.py`.
- Before proposing changes run `python scripts/atlas_lint.py .` plus currently authorised relevant validation, and disclose any deferred tests or freshness checks.
- After a staging record is first committed, do not edit its evidence content, path or ID. The only permitted later mutation is top-level frontmatter `status`; corrections are new staging evidence.
- Treat `status: new` staging records as the normal curation queue. Do not automatically recurate terminal records.

## Curation review
- The Atlas PR/MR is the curation review/audit record; do not duplicate it into a `reviews/` folder.
- A curation PR/MR should identify staging consumed, outcome, curated changes, material claims not promoted, connection decisions/open questions and validation results.
- `_curated/status/curation-status.md` is a compact latest checkpoint only, never a per-record ledger.

## Navigation
Do not read the entire Atlas repository. Start from `index.md` or the relevant skill and open the smallest useful set of files.

## Operational records
- staging lifecycle/queue state → each `_staging/` record's `status`
- latest curation checkpoint → `_curated/status/curation-status.md`
- human curation review/history → Atlas PR/MR and Git history
- significant Atlas milestones only → `log.md`
