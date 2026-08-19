# Generated Atlas maps

Maps provide deterministic, sparse routing and direct connection views. Curated Markdown remains the source of truth: maps connect; pages explain behavior, evidence, failure context and uncertainty.

## Choose a map

| Question | Start here | Primary collections |
|---|---|---|
| How does an end-to-end path run and what performs each step? | [Flow/component map](flow-component/flow-component-map.json) | `flows.steps` |
| Which repository owns a component and what does it depend on? | [Repository/component map](repository-component/repository-component-map.json) | `repositories`, `components` |
| Which infrastructure package/resource is used, triggered or monitored? | [Infrastructure dependency map](infra-dependency/infra-dependency-map.json) | `packages`, `resources` |

Schema, embedded data-asset, runbook, standard, incident and concept records remain curated pages. Stable IDs are resolved through the query tool or an exact curated-page lookup. Asset lineage is loaded directly from schema pages; structured conflicts remain page context and never become map records.

For an ordinary description, use typed `atlas_query.py find` first and open the selected page. These maps are for direct/reverse traversal after stable-ID selection, not the initial natural-language search corpus.

## Maintenance contract

- Authors edit structured fields on curated Markdown pages, never generated JSON.
- Stable Atlas IDs are keys; filesystem and repository paths are mutable locators.
- Flow steps are the sole participant representation.
- Only `downstream_flows`, compact repository/package containment IDs and typed `used_by` are generated reverse conveniences.
- Other reverse, cross-repository and transitive paths are computed by `atlas_query.py`.
- Possible, unconfirmed and conflicting facts remain in normal semantic collections with confidence and evidence.
- Optional empty arrays, objects, strings and nulls are omitted from generated records.
- Narrative impact, monitoring detail and full question context remain on pages.
- `metadata.generated` is deterministic; no update timestamp is emitted.

Rebuild maps, catalogues and managed page views together:

```powershell
python scripts/rebuild_atlas.py
```

Query direct and transitive routes without expanding JSON manually:

```powershell
python scripts/atlas_query.py resolve comp.example-ingest
python scripts/atlas_query.py find "component that ingests examples" --type component
python scripts/atlas_query.py context .
python scripts/atlas_query.py neighbors comp.example-ingest
python scripts/atlas_query.py impact comp.example-ingest --direction downstream
```

The query tool derives trust from lifecycle: `status: curated` is authoritative and deprecated content is `deprecated` and non-authoritative. It reports Git separately through a compact checkout-state advisory, which never blocks traversal or changes authority. `context` resolves physical Git/path information to ordered repository/component candidates without hiding ambiguity. Open linked pages when the map cannot answer the question completely.
