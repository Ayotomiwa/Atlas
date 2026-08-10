# TeamA Atlas

TeamA Atlas is a governed engineering context package for humans and AI agents. It stores attributable raw evidence in `_staging/`, reviewed reusable knowledge in `_curated/`, and deterministic routing views in generated maps.

Claude workflows in `.claude/` are canonical and load from this live checkout with `claude --add-dir <ATLAS_ROOT>`. Codex adaptations live in `.agents/skills/` and `.codex/agents/`.

## Start by question

- Source repository or monorepo orientation: [`_curated/repositories/index.md`](_curated/repositories/index.md)
- Component behavior/dependencies: [`_curated/components/index.md`](_curated/components/index.md)
- End-to-end flow: [`_curated/flows/index.md`](_curated/flows/index.md)
- Infrastructure usage/impact: [`_curated/infra/index.md`](_curated/infra/index.md)
- Data/interface contract: [`_curated/schema-info/index.md`](_curated/schema-info/index.md)
- Direct or transitive machine routing: `python scripts/atlas_query.py ...`
- Raw review queue: [`_staging/index.md`](_staging/index.md)

Known-package access starts directly at the appropriate index, map, stable ID or page. It does not need to route through the package manifest.

## Package federation

[`atlas-package.json`](atlas-package.json) is the machine-only package manifest. It declares identity, ownership, aliases, controlled domains, entrypoints, map paths, taxonomy paths and compiler-contract paths. Human routing explanation stays in this README and [`index.md`](index.md).

Domains are registered inline before architecture records use them:

```json
{
  "id": "orders",
  "title": "Orders",
  "aliases": ["order-processing"],
  "routing_description": "Order capture, validation and fulfilment architecture."
}
```

The domain controls storage and routing, not identity. A stable ID such as `comp.sds-client` may remain unchanged when its repository, file path or primary domain moves; add further semantic segments only when they are needed to prevent ambiguity.

A future Atlas-core registry should store only:

```json
{
  "package_id": "package.teama",
  "aliases": ["teama", "team-a", "team a"],
  "manifest_location": "<authorised TeamA Atlas location>/atlas-package.json",
  "status": "active"
}
```

The registry discovers packages. Once a package is known, direct access uses that package's maps and indexes.

## Trust and lifecycle

- `_staging/` is raw, attributable evidence and never authoritative.
- `_curated/` contains reviewable knowledge; local records may be used for routing with their lifecycle status preserved.
- Only human-reviewed, merged `status: curated` content is authoritative. The package manifest does not prescribe a branch. The query tool gives a non-blocking warning outside `main` or `master` because results may include unmerged work.
- Agents stage and propose; they never self-approve or merge.
- Missing evidence remains unknown. Absence from a map never proves no dependency or impact.

Committed staging evidence is treated as immutable by policy. Only top-level lifecycle status changes later; corrections use a new staging record. This remains a review rule rather than a Git/digest lint check.

## Repository, component and flow boundaries

- A `repo.*` record describes an independently useful source boundary: a standalone Git repository, useful monorepo root, evidenced logical monorepo project, nested project, mirror, or classified alternative.
- A `comp.*` record describes an independently addressable runtime or reusable architectural unit.
- A `flow.*` record owns ordered participation and material handoffs.
- Repository/folder/domain/job-group containers are not automatically components.
- Stable IDs are never derived from repository names or paths. They may resemble a locator when the semantic name is also appropriate, but they do not change when that locator changes.
- `repository_root` is a mutable path relative to the physical Git root. Component paths are relative to their most-specific referenced `repo.*` boundary.

Architecture pages are grouped by one controlled primary domain. Secondary involvement is metadata, not duplicate pages. If the primary domain cannot be evidenced, curation asks the user.

## Relationship and map model

Pages author natural fields such as `depends_on`, `consumes`, `produces`, `reads_from`, `writes_to`, `steps` and `upstream_flows`. Architecture pages route `runbooks`, `standards` and `incident_learnings` directly. The containing field supplies the meaning; entries identify a stable local `id` or external `name` and do not repeat a generic relationship value.

The three committed generated maps are:

- [`flow-component-map.json`](_curated/maps/flow-component/flow-component-map.json)
- [`repository-component-map.json`](_curated/maps/repository-component/repository-component-map.json)
- [`infra-dependency-map.json`](_curated/maps/infra-dependency/infra-dependency-map.json)

They use stable-ID keys, readable named fields, sparse records and only three high-value reverse views: `downstream_flows`, compact repository/package containment IDs and a typed `used_by` list. They do not contain generic nodes/edges arrays, duplicate participant rosters or precomputed transitive impact. Maps connect; pages explain.

## Generation

After structured page, domain or lifecycle changes, rebuild every generated surface together:

```powershell
python scripts/rebuild_atlas.py
```

This writes maps, root/domain catalogues, staging queue indexes, structured body tables and opted-in flow diagrams. Managed blocks and generated JSON are never hand-edited.

Freshness-only mode exists for an explicitly authorised validation pass:

```powershell
python scripts/rebuild_atlas.py --check
```

## Querying

```powershell
python scripts/atlas_query.py resolve comp.example
python scripts/atlas_query.py context .
python scripts/atlas_query.py route orders
python scripts/atlas_query.py neighbors comp.example
python scripts/atlas_query.py impact comp.example --direction downstream
python scripts/atlas_query.py --format json impact comp.example --max-depth 4
```

The query tool loads map paths from `atlas-package.json`, preserves confidence/evidence, reports direct versus transitive paths and avoids cycles. It reports record lifecycle status but does not determine whether a change has been human-reviewed or merged. Outside `main` or `master` it emits an advisory warning and continues. Map traversal does not open narrative pages; an exact unmapped-ID fallback reads curated frontmatter only. Discovery/impact workflows open a map-provided page body only when narrative or evidence context is required. An unmapped starting schema/standard/runbook uses its exact stable ID or domain index; ambiguous title matches are never selected silently.

`context [path]` discovers the physical Git root/remote and returns logical repository and component candidates ordered by path specificity. It preserves ambiguity; the skill chooses context based on the question and discloses that selection.

Every substantive Atlas-assisted answer cites the curated page or repository source for its material claims and includes a compact route/file-hop disclosure when traversal matters. Generated/query output explains routes but is never cited as semantic authority.

## Folder responsibilities

| File/folder | Responsibility |
|---|---|
| `atlas-package.json` | Machine package/federation/compiler contract |
| `index.md` | Root human/agent routing |
| `_staging/` | Immutable-by-policy evidence queue |
| `_curated/*/README.md` | Semantic, evidence and review rules |
| `_curated/*/_template.md` | Authoring interface |
| `_curated/*/index.md` | Generated catalogue plus coverage notes |
| `_curated/maps/` | Generated direct routing interfaces |
| `taxonomy/` | Controlled author classifications |
| `contracts/` | Compiler-only map field and impact-direction rules |
| `scripts/atlas_query.py` | Supported routing/traversal CLI |
| `scripts/rebuild_atlas.py` | Unified deterministic generator |

Exact operational commands remain in source repositories or authorised operational systems; Atlas routes to them instead of copying them.
