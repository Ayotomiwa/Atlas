# Datalens Atlas

Datalens Atlas is a governed engineering context package for humans and AI agents. It stores attributable raw evidence in `_staging/`, reviewed reusable knowledge in `_curated/`, deterministic routing views in generated maps, and non-authoritative merged-source processing cursors in `_intake/`.

Claude workflows in `.claude/` are canonical and load from this live checkout with `claude --add-dir <ATLAS_ROOT>`. Codex adaptations live in `.agents/skills/` and `.codex/agents/`.

## Use Atlas conversationally

Engineers do not need to select Atlas skills or commands. Use four ordinary intents:

| Intent | Say things like | Atlas handles internally |
|---|---|---|
| Ask Atlas | “How does this publish data?” “What could this change affect?” | discovery, impact routing, links, maps and bounded source fallback |
| Teach Atlas | “Save this fact.” “What does Atlas still need to know?” | provenance, duplicate/conflict checks, bucket selection and one approved evidence write |
| Sync Atlas | “Onboard this repository.” “Update Atlas for this repo.” | full baseline onboarding, standards discovery or merged-change intake |
| Curate Atlas | “Curate pending evidence for payments.” | scoped reconciliation, generation and independent semantic review |

Atlas remains sophisticated behind the conversation: staging is still evidence, writes still require approval, uncertainty is preserved, curation still receives independent review, and publication remains human-controlled. Exact skills and commands are available in the [advanced reference](onboarding/advanced-reference.md).

## Start by question

- Source repository or monorepo orientation: [`_curated/repositories/index.md`](_curated/repositories/index.md)
- Component behavior/dependencies: [`_curated/components/index.md`](_curated/components/index.md)
- End-to-end flow: [`_curated/flows/index.md`](_curated/flows/index.md)
- Infrastructure usage/impact: [`_curated/infra/index.md`](_curated/infra/index.md)
- Data/interface contract: [`_curated/schema-info/index.md`](_curated/schema-info/index.md)
- Matching knowledge from an ordinary description: ask Claude; it uses deterministic candidate search and falls back to the relevant index.
- Direct or transitive routing: ask the dependency/impact question; Claude selects page links and maps internally.
- Open questions you can help answer: ask “What does Atlas still need to know about this path, repository, domain or topic?”
- Raw review queue: [`_staging/index.md`](_staging/index.md)
- Active or historical evidence across every staging bucket: ask Claude to show pending or completed evidence for the desired scope.
- Merged default-branch changes not yet considered: ask Claude to update Atlas for the repository.

Maintainers and power users can use the exact [skill and command reference](onboarding/advanced-reference.md).

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

**Registering the first domain is the first adoption step.** `domains` ships empty, and until an entry exists no repository, component, flow, infrastructure or schema page can be stored, because every architecture record must live under a registered domain folder that matches its `primary_domain`. Lint says so at the point of failure, but the edit belongs here rather than on the page being written.

The domain controls storage and routing, not identity. A stable ID such as `comp.sds-client` may remain unchanged when its repository, file path or primary domain moves; add further semantic segments only when they are needed to prevent ambiguity.

A future Atlas-core registry should store only:

```json
{
  "package_id": "package.datalens",
  "aliases": ["datalens", "data-lens", "clearwater"],
  "manifest_location": "<authorised Datalens Atlas location>/atlas-package.json",
  "status": "active"
}
```

The registry discovers packages. Once a package is known, direct access uses that package's maps and indexes.

## Trust and lifecycle

- `_staging/` is raw, attributable evidence and never authoritative.
- `_intake/` is shared mutable processing state. It records what Atlas observed and considered but is neither evidence nor authority.
- `_curated/` contains active authoritative or historical knowledge; every `status: curated` page is authoritative.
- Git does not change semantic authority. Query reports a compact checkout advisory for modified, untracked, detached or off-main pages so newly curated or possibly unmerged work remains visible.
- Agents stage and curate through evidence and independent review; they never merge or publish.
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

## Generated artifacts

After structured page, domain or lifecycle changes, Atlas rebuilds maps, curated catalogues, staging queue indexes, structured body tables and opted-in flow diagrams together. Managed blocks and generated JSON are never hand-edited. Deterministic lint covers frontmatter semantics and existing relative Markdown file targets; generation freshness and semantic prose review remain separate checks. Exact maintainer commands are in the [advanced reference](onboarding/advanced-reference.md).

## Navigation mechanics

`find` is deterministic candidate retrieval over non-archived curated frontmatter, embedded data assets and promoted resources. It searches IDs, titles, descriptions, aliases, optional routing keywords, types, domains, conflict text and low-weight locators; it does not use embeddings, a vector store or an LLM. It returns three candidates by default with match reasons, matched conflict routes and index/page routes. Claude selects using the question and curated evidence or preserves ambiguity; search relevance is never factual confidence.

The query tool loads map paths from `atlas-package.json`, preserves confidence/evidence, reports direct versus transitive paths and avoids cycles. Lifecycle determines trust: `status: curated` is `authoritative`, while deprecated content is `historical`. Git is reported separately as `checkout_state` (`main-clean`, `off-main`, `modified`, `untracked`, `detached` or `git-unknown`) and never blocks or downgrades authority. Outside `main` or `master` it emits one short advisory and continues. A `not-verified` path match remains available but must be disclosed as routing rather than repository-identity proof. Maps are used after stable-ID selection for reverse or multi-hop traversal; curated pages and their generated direct links remain the semantic navigation surface.

Open-question discovery reads the common question table from curated pages, qualifies each question by its owning record and suppresses questions already referenced by active staging evidence. Claude decides what is useful to ask and never treats a candidate match as authority.

The cross-bucket staging view is deterministic and read-only. It can scope active or historical evidence by bucket, domain, date or suggested target. An empty result does not prove that no evidence or engineering context exists.

Incremental repository sync fetches the selected source's remote default branch, compares it with the shared `_intake/` cursor, interprets the bounded change range, previews plain-language outcomes plus exact persistence effects and writes `staging.change` evidence only after approval. It never curates or publishes. On first use the base must be explicit, locally proven by a merged-MR commit, or recovered from an approved full-onboarding snapshot's future intake anchor. It never guesses and does not advance the considered cursor when remote completeness, ancestry or assessment is unresolved.

Full repository onboarding selects one immutable source state with `scripts/atlas_source_snapshot.py`. A clean current `HEAD` is read in place; an explicit historical/unmerged commit or a dirty active checkout uses a protected detached temporary worktree. The helper never switches, resets, cleans or stashes the active checkout, never fetches, and never advances intake state.

Path context discovers the physical Git root/remote and returns logical repository/component candidates ordered by path specificity. It preserves ambiguity; Claude chooses context from the question and discloses that selection.

Every substantive Atlas-assisted answer cites the curated page or repository source for its material claims and includes a compact route/file-hop disclosure when traversal matters. Generated/query output explains routes but is never cited as semantic authority.

## Folder responsibilities

| File/folder | Responsibility |
|---|---|
| `atlas-package.json` | Machine package/federation/compiler contract |
| `index.md` | Root human/agent routing |
| `_staging/` | Immutable-by-policy evidence queue |
| `_intake/` | Mutable, non-authoritative merged-source observation and consideration checkpoints |
| `_curated/*/README.md` | Semantic, evidence and review rules |
| `_curated/*/_template.md` | Authoring interface |
| `_curated/*/index.md` | Generated catalogue plus coverage notes |
| `_curated/maps/` | Generated direct routing interfaces |
| `taxonomy/` | Controlled author classifications and allowed values |
| `contracts/` | Compiler-only map field and impact-direction rules |
| `scripts/atlas_query.py` | Supported candidate lookup and routing/traversal CLI |
| `scripts/atlas_intake.py` | Read and compare-and-swap shared merged-source checkpoints |
| `scripts/rebuild_atlas.py` | Unified deterministic generator |
| `scripts/atlas_review_snapshot.py` | Temporary review-input fingerprinting; manifests never enter Atlas |
| `scripts/atlas_source_snapshot.py` | Safe immutable source selection for full repository onboarding; manifests/worktrees stay temporary |
| `scripts/atlas_eval.py` | Reusable sealed-evaluation preparation, answer freezing, validation and scoring contract |
| `evaluation/` | Fixture-independent evaluation protocol and frozen rubric |

Exact operational commands remain in source repositories or authorised operational systems; Atlas routes to them instead of copying them.
