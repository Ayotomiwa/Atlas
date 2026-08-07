# DataLens Atlas — agent instructions

This repository is the **DataLens Atlas package** (`atlas.datalens`), one of the federated Clearwater Atlas packages. It is not the central repository.

## What this repository is
Curated, human-reviewed engineering context for DataLens. `_curated/` is authoritative. `_staging/` is raw evidence and is never authoritative.

## Routing
1. Start at `index.md`, then `_curated/index.md`.
2. Route by concept area, or by domain via `_curated/domains/<domain>/index.md`.
3. For impact questions, start in `_curated/maps/`.
4. For a flow question, start at `_curated/maps/flow-component-map.json`.
5. Open the smallest set of pages that answers the question.

## Trust rules
- Only cite pages with `status: curated`. Label `draft-curated` explicitly as draft.
- Never present `_staging/` content as authoritative.
- Cite the Atlas `id` and file path for every Atlas-backed claim.
- If Atlas does not cover the question, label the answer as not Atlas-backed.
- A missing relationship means “not captured”, never “does not exist”.

## Write rules
- Never hand-edit `_curated/maps/*.json`; edit page relationships and run `python scripts/rebuild_maps.py`.
- Never modify a staging file after it has been used for curation.
- Run `python scripts/atlas_lint.py .` before proposing any change.
- Propose; never self-approve. All promotion goes through a merge request.
