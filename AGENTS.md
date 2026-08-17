# Datalens Atlas — Codex operating rules

This repository is the Datalens Atlas package (`datalens`). It is a governed engineering context layer, not a general document dump.

## Trust
- `_staging/` is raw evidence and is never authoritative.
- Every `_curated/` page with `status: curated` is authoritative; Git branch and merge state are separate checkout advisories.
- Codex may stage and curate through the required evidence and independent-review workflow; Codex never merges or publishes knowledge.
- Never invent missing engineering context.

## Human interaction
- Present normal Atlas use as four intents: **Ask Atlas**, **Teach Atlas**, **Sync Atlas**, and **Curate Atlas**.
- Read `.agents/skills/_shared/human-intents.md` when routing Atlas work and `.agents/skills/_shared/persistence-approval.md` before any write-capable workflow. For authoring, staging handoffs or curation also read `.agents/skills/_shared/curation-safety.md`.
- Infer the specialist workflow from ordinary language. Do not require the user to know skill names, staging buckets, lifecycle codes or query commands.
- Use exactly one concrete preview and one scope-bound approval per persistence operation; internal handoffs do not reset approval.
- Repository onboarding establishes a full curation-ready baseline from one immutable selected source snapshot. Incremental merged-change processing begins only after coverage exists.

## How repository rules are organised
- `atlas-package.json` defines machine package identity, domains and entrypoints; known-package lookups may route directly to maps/indexes/pages.
- `index.md` files route to existing knowledge.
- A target folder's `README.md` defines semantic, granularity, evidence and reviewer rules.
- A target folder's `_template.md` defines page shape.
- Codex skills in `.agents/skills/` define workflows; specialist agent profiles live in `.codex/agents/`.

## Editing Atlas
- Before staging or curating, read `atlas-package.json` and follow its registered paths: `types` and `statuses` always; `concept_fields` for controlled concept/asset/resource fields; `standard_categories` for standards; and the registered `map_fields` contract before map-bound fields/relationships. Read the destination's `README.md`, `_template.md`, and `index.md`; do not load unrelated taxonomy.
- Edit structured routing fields only on curated Markdown pages.
- Never hand-edit generated map data below `_curated/maps/`.
- After structured routing changes run `python scripts/rebuild_atlas.py`.
- For curation, follow the shared order: approval, work guard, `curating`, materialisation, materialized checkpoint, aggregate lint classification, at most two safe mechanical repair passes, scope-clean check, rebuild/check, review, then `consumed`. Run full lint after materialisation; current/shared/new/unexpected findings block, while demonstrably unrelated baseline findings are advisory and never repaired. Global lint and CI remain strict.
- After a staging record is first committed, do not edit its evidence content, path or ID. The only permitted later mutation is top-level frontmatter `status`; corrections are new staging evidence.
- Treat `status: new` staging records as the normal curation queue. Do not automatically recurate terminal records.
- `_intake/` is mutable, non-authoritative source-processing state and is not governed by staging immutability. Use `atlas-stage-changes` and its deterministic helper rather than hand-editing checkpoints.

## Curation review
- Independent review completes semantic curation. The Atlas PR/MR is the later publication/human-audit record and does not change page authority; do not duplicate it into a `reviews/` folder.
- A curation PR/MR should identify staging consumed, outcome, curated changes, material claims not promoted, connection decisions/open questions and validation results.
- `_curated/status/curation-status.md` is a compact latest checkpoint only, never a per-record ledger.
- Recover only a damaged curated page from its materialized checkpoint or verified revision. Never restore all `_curated/` in a mixed checkout; preserve tracked and untracked work. Consumed evidence stays consumed.

## Navigation
Do not read the entire Atlas repository. Start from `index.md` or the relevant skill and open the smallest useful set of files.

Use `python scripts/atlas_query.py staging` for the cross-bucket evidence queue. Use `atlas-stage-changes` when asked to assess merged default-branch changes since a shared source cursor; it stages approved evidence but never curates it.

## Operational records
- staging lifecycle/queue state → each `_staging/` record's `status`
- merged-source observation/consideration cursor → `_intake/checkpoints/<source-key>.json`
- latest curation checkpoint → `_curated/status/curation-status.md`
- publication and later human-review history → Atlas PR/MR and Git history
- significant Atlas milestones only → `log.md`
