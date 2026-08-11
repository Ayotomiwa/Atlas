# Atlas controlled values and compiler contracts

Taxonomy contains classifications that authors choose. Compiler contracts are separate because endpoint and direction rules are implementation detail, not author vocabulary.

| File | Responsibility |
|---|---|
| `taxonomy/types.yaml` | Record types, folders, ID prefixes and grouping model |
| `taxonomy/statuses.yaml` | Lifecycle, confidence and coverage values |
| `taxonomy/concept-fields.yaml` | Node classifications grouped by repository, component, flow, infrastructure, schema, standard and shared use |
| `taxonomy/standard-categories.yaml` | Standards category vocabulary |
| `contracts/map-fields.yaml` | Compiler-only field endpoints, internal action meanings, impact direction and map registrations |

## Human model

The current record supplies the source and the field supplies the natural connection: `depends_on`, `consumes`, `produces`, `reads_from`, `writes_to`, `upstream_flows`, and similar. An entry identifies a stable local `id` or an external `name`; it never repeats a generic relationship name.

Qualifiers only classify what the field genuinely needs. Examples are `dependency_type`, `asset_type`, `data_asset_type`, `entry_point_type`, `participant.type` and `resource_type`. Their values are grouped under the relevant node type in `concept-fields.yaml`, so authors can see who owns each vocabulary. The shared `asset_type` classifies component and flow I/O targets; `schema.data_asset_type` classifies embedded data assets themselves.

Repository types distinguish a standalone Git boundary, an optional physical monorepo root, an evidenced logical monorepo project, a genuinely nested project, a mirror, other and unknown. `repository_root` is a locator rather than taxonomy: it is `.` or a POSIX path relative to the physical Git root and may change without changing the stable ID.

## IDs

Curated IDs use a registered prefix plus one or more semantic kebab-case segments. Add segments only to remove ambiguity. IDs are never derived from repository/package paths, domain folders, URLs or filenames and do not change when those locators move.

Schema identifiers such as `atlas/1.0`, `atlas-map/1.0`, `atlas-package/1.0` and `atlas-taxonomy/1.0` retain the Atlas product name.
