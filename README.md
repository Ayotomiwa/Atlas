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
