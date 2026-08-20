# Datalens Atlas — Claude operating rules

This repository is the Datalens Atlas package (`datalens`). It is a governed engineering context layer, not a general document dump.

## Trust
- `_staging/` is raw evidence and is never authoritative.
- Every `_curated/` page with `status: curated` is authoritative; Git branch and merge state are separate checkout advisories.
- Claude may stage and curate through the required evidence and independent-review workflow; Claude never merges or publishes knowledge.
- Never invent missing engineering context.

## Human interaction
- Present normal Atlas use as four intents: **Ask Atlas**, **Teach Atlas**, **Sync Atlas**, and **Curate Atlas**.
- Read `.claude/skills/_shared/human-intents.md` when routing Atlas work and `.claude/skills/_shared/persistence-approval.md` before any write-capable workflow. For authoring, staging handoffs or curation also read `.claude/skills/_shared/curation-safety.md`.
- Infer the specialist workflow from ordinary language. Do not require the user to know skill names, staging buckets, lifecycle codes or query commands.
- Use exactly one concrete preview and one scope-bound approval per persistence operation; internal handoffs do not reset approval.
- Reuse an existing feature branch for related Atlas writes and state its name non-blockingly. Ask for a suggested/custom branch only on the default branch, detached HEAD or unrelated history. Local commits never authorise push or merge.
- Repository onboarding establishes a full curation-ready baseline from one immutable selected source snapshot. Incremental merged-change processing begins only after coverage exists.
- For many confirmed infrastructure boundaries, use `atlas-onboard-infra-portfolio` to pilot and batch the existing repository onboarding workflow. It stops at committed staging evidence and never curates the portfolio.

## How repository rules are organised
- `atlas-package.json` defines machine package identity, domains and entrypoints; known-package lookups may route directly to maps/indexes/pages.
- `index.md` files route to existing knowledge.
- A target folder's `README.md` defines semantic, granularity, evidence and reviewer rules.
- A target folder's `_template.md` defines page shape.
- Skills in `.claude/skills/` define workflows.

## Editing Atlas
- Before staging or curating, read `atlas-package.json` and follow its registered paths: `types` and `statuses` always; `concept_fields` for controlled concept/asset/resource fields; `standard_categories` for standards; and the registered `map_fields` contract before map-bound fields/relationships. Read the destination's `README.md`, `_template.md`, and `index.md`; do not load unrelated taxonomy.
- Edit structured routing fields only on curated Markdown pages.
- Never hand-edit generated map data below `_curated/maps/`.
- After structured routing changes run `python scripts/rebuild_atlas.py`.
- Run full lint before and after staging/curation writes. New or touched-scope findings block; unchanged unrelated baseline findings are reported afterward and do not block or become repair scope. Package-wide lint and CI remain strict.
- For curation, follow the shared Git order: branch/baseline, approval, `curating`, materialisation, exact checkpoint commit, aggregate lint classification, at most two safe mechanical repair passes, rebuild/check, validated commit, immutable-range review, then `consumed` and finalization commit. Current/changed-shared/new/unexplained findings block; unchanged unrelated baseline findings are advisory and never repaired. Global lint and CI remain strict.
- After a staging record is first committed, do not edit its evidence content, path or ID. The only permitted later mutation is top-level frontmatter `status`; corrections are new staging evidence.
- Treat `status: new` staging records as the normal curation queue. Do not automatically recurate terminal records.
- `_intake/` is mutable, non-authoritative source-processing state and is not governed by staging immutability. Use `/atlas-stage-changes` and its deterministic helper rather than hand-editing checkpoints.

## Curation review
- Independent review completes semantic curation. The Atlas PR/MR is the later publication/human-audit record and does not change page authority; do not duplicate it into a `reviews/` folder.
- A curation PR/MR should identify staging consumed, outcome, curated changes, material claims not promoted, connection decisions/open questions and validation results.
- `_curated/status/curation-status.md` is a compact latest checkpoint only, never a per-record ledger.
- Recover only approved damaged paths from the local checkpoint commit or another verified revision. Never reset broadly or restore all `_curated/`; preserve unrelated tracked and untracked work. Consumed evidence stays consumed.

## Navigation
Do not read the entire Atlas repository. Start from `index.md` or the relevant skill and open the smallest useful set of files.

When Claude is running inside this Atlas checkout, stored-knowledge questions still use `atlas-discover`: search curated records without treating the Atlas path as product context. Questions about Atlas implementation use local repository evidence instead.

Use `python scripts/atlas_query.py staging` for the cross-bucket evidence queue. Use `/atlas-stage-changes` when asked to assess merged default-branch changes since a shared source cursor. Use `/atlas-onboard-infra-portfolio` for a confirmed multi-product infrastructure inventory; it delegates every item to repository onboarding.

## Operational records
- staging lifecycle/queue state → each `_staging/` record's `status`
- merged-source observation/consideration cursor → `_intake/checkpoints/<source-key>.json`
- infrastructure portfolio onboarding queue → `_intake/onboarding/<campaign-id>.json`
- latest curation checkpoint → `_curated/status/curation-status.md`
- publication and later human-review history → Atlas PR/MR and Git history
- significant Atlas milestones only → `log.md`
