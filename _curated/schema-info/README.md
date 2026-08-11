# Curated schema information

Schema-info pages store reviewed knowledge about durable tables, events, files, APIs, datasets and other contracts whose physical shape or semantics matter to engineering decisions.

## Placement and identity

Store each page at `_curated/schema-info/<primary-domain>/<record>.md`. The primary domain must be registered in `atlas-package.json` and match the folder. Stable `schema.*` IDs describe the durable contract, never the repository path, physical table name or Atlas filename.

Schema records remain pages rather than a fourth map collection. Component and flow I/O entries route to them by stable ID; `atlas_query.py`, the domain index or an exact ID search resolves the page and trust state.

A schema page may embed individually addressable durable assets as `asset.*` records. Assets inherit the page, domain, lifecycle, trust and coverage. Author lineage only from each asset through `inputs`; query traversal derives reverse consumers. A known local input uses an `asset.*` ID, while an unknown external input keeps a readable `name` without an invented ID. Assets remain on their owning schema page and never create a schema map or standalone page.

## Content

Document physical identity/platform, grain, keys, temporal behavior, compatibility/versioning, important fields, known producers/consumers, approved joins, quality limitations and authority-supplied classification/access constraints. Do not copy raw schema dumps when an authorised source link is sufficient.

Schema-level `asset_type`, embedded `data_asset_type`, and `temporal_model` are controlled by `taxonomy/concept-fields.yaml`. Keep `physical_name`, `platform`, and authority-supplied `classification` as compact routing/filter fields in frontmatter; explain and evidence their meaning in the body. Grain, keys, and latest-record rules remain body content because they need qualification and attribution rather than a second unexplained scalar copy. Never guess classification.

Use `links` for standards, supersession, implementation and other governed context. Producers and consumers author their durable I/O on component/flow pages; do not create reciprocal generic relationships on schema pages.

Material meaning, grain, keys, compatibility and joins require attributable evidence. Missing evidence remains explicit coverage or open questions. Never include credentials, production rows, customer data or sensitive payloads.

Run `python scripts/rebuild_atlas.py` after page/domain/status changes so catalogues and map routes remain current.

## Review

Before approving a schema-info page, confirm that:

- business meaning comes from an authority or SME, not from column and field names;
- physical identity and platform match the source definition;
- grain is stated precisely enough that a row's meaning is unambiguous;
- primary and business keys are distinguished, and any surrogate key is identified as such;
- `temporal_model` matches the described update behaviour;
- compatibility and versioning describe what consumers may rely on;
- producers and consumers are authored on the component/flow pages that make those claims, not reciprocally here;
- embedded assets have stable semantic IDs, evidenced identity and input lineage, with no invented ID for an unknown external source;
- approved joins are reviewed rather than plausible, and known quality limitations are recorded;
- classification is authority-supplied, and no credentials, production rows or customer data appear anywhere on the page.
