# Curated schema information

Schema-info pages store reviewed knowledge about durable tables, events, files, APIs, datasets and other contracts whose physical shape or semantics matter to engineering decisions.

## Placement and identity

Store each page at `_curated/schema-info/<primary-domain>/<record>.md`. The primary domain must be registered in `atlas-package.json` and match the folder. Stable `schema.*` IDs describe the durable contract, never the repository path, physical table name or Atlas filename.

Schema records remain pages rather than a fourth map collection. Component and flow I/O entries route to them by stable ID; `atlas_query.py`, the domain index or an exact ID search resolves the page and trust state.

## Content

Document physical identity/platform, grain, keys, temporal behavior, compatibility/versioning, important fields, known producers/consumers, approved joins, quality limitations and authority-supplied classification/access constraints. Do not copy raw schema dumps when an authorised source link is sufficient.

`asset_type` and `temporal_model` are controlled by `taxonomy/concept-fields.yaml`. Classification remains authority-supplied and must not be guessed.

Use `links` for standards, supersession, implementation and other governed context. Producers and consumers author their durable I/O on component/flow pages; do not create reciprocal generic relationships on schema pages.

Material meaning, grain, keys, compatibility and joins require attributable evidence. Missing evidence remains explicit coverage or open questions. Never include credentials, production rows, customer data or sensitive payloads.

Run `python scripts/rebuild_atlas.py` after page/domain/status changes so catalogues and map routes remain current.
