# Team Atlas — DataLens package

Team Atlas is the DataLens Atlas package: governed engineering and data context readable by humans and coding agents. Curated pages are reviewed operating context; staging pages are evidence and are never authoritative.

## Lifecycle

**Stage → Curate → Propose → Human review → Merge → Refresh**

Refresh is reporting-only: it flags stale reviewed pages and never changes status automatically.

## Stage evidence

1. Choose the matching bucket under `_staging/`.
2. Copy its `_template.md` to `STG-YYYYMMDD-<slug>.md`.
3. Record source, capture date and links. Do not infer missing facts.
4. Once used for curation, keep the staging file immutable and archive in place.

## Curate

Run `/atlas-curate` with the staging file. The skill chooses the target type, loads the curated template, reconciles existing context, proposes evidence-backed relationships, rebuilds maps and runs lint. Proposed pages remain `status: draft-curated`.

For an unevidenced body section use exactly:

*Not covered — no evidence in current staging material.*

## Validate locally

Requires Python 3.11+.

```bash
pip install -r scripts/requirements.txt
python scripts/atlas_lint.py . --self-test
python scripts/rebuild_maps.py --check
python scripts/atlas_lint.py .
```

Never hand-edit `_curated/maps/*.json`; edit page relationships and regenerate them.

## Propose and review

Create a feature branch, include staged evidence, proposed curated page, index/status updates and generated maps, then open a merge request or pull request. A human reviewer decides whether a page becomes `status: curated`, supplies `reviewed_by` and `last_reviewed`, and merges. Claude never self-approves.

## Templates

- Curated: `_curated/<concept>/_template.md`
- Staging: `_staging/<bucket>/_template.md`
- Reviews: `reviews/_template.md`
- Taxonomy: `taxonomy/`

## CI

`.gitlab-ci.yml` runs lint, generated-map consistency and scheduled freshness reporting. The lint/map jobs are temporarily `allow_failure: true` for the initial two-week adoption window.

## Worked end-to-end example

This example demonstrates the lifecycle without asserting any real DataLens system facts.

1. **Stage a repository observation.** Copy `_staging/components/_template.md` to `_staging/components/STG-20260807-example-repo.md`. Record only evidence actually observed, set `target_type: atlas.component`, and leave `status: new` until ready.
2. **Run `/atlas-curate`.** The skill reads the staging entry and component template, then identifies an existing page to update or proposes a new grouped component page. Unknown body sections use the exact not-covered marker.
3. **Resolve relationships.** Each proposed edge points at a real Atlas ID, carries `kind` where required, and has relationship-level `confidence`; anything below `reviewed` explains what evidence is missing.
4. **Regenerate and validate.** Run `python scripts/rebuild_maps.py`, update the relevant `index.md` and `_curated/status/curation-status.md`, then run `python scripts/atlas_lint.py .`.
5. **Propose.** Commit on a feature branch and open a merge request or pull request. The proposed curated page remains `status: draft-curated`.
6. **Human review and merge.** A reviewer checks evidence and relationships. Only the reviewer promotes to `status: curated`, supplies `reviewed_by` and `last_reviewed`, and merges.
7. **Refresh later.** Scheduled CI runs ATLAS021 to report pages older than 180 days. It never alters status.
