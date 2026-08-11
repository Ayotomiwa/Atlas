# Datalens Atlas V1 — Final Implementation Specification

**Audience:** implementation agent, default Claude Code  
**Repository:** `datalens-atlas`
**Pilot scope:** one Datalens Atlas package only
**Package slug:** `datalens`
**Status:** implementation-ready  
**Purpose:** build a complete, usable V1 scaffold that can onboard real datalens services without inventing datalens facts.

---

## 0. Implementation-agent directive

Build this repository in the phase order in §18. Do not reinterpret the architecture unless a literal technical blocker makes the specification impossible.

The implementation agent MUST:

1. create every file and folder required by §3;
2. implement all README, index, template, taxonomy, skill, agent, script, test and CI contracts in this specification;
3. build deterministic lint and map generation before creating example content;
4. keep all datalens engineering knowledge empty or explicitly marked as not covered unless evidence is supplied;
5. never invent repositories, owners, dependencies, infrastructure, flows, standards, business definitions or production facts;
6. run the full acceptance suite after every phase;
7. fix every deterministic failure before continuing;
8. never manually maintain generated map relationship data;
9. never let Claude self-approve curated knowledge;
10. return an implementation report listing files created, tests executed, results, and genuine external blockers.

Where this document conflicts with earlier Datalens Atlas design documents, this document wins for V1.

---

## 1. Locked V1 decisions

| Topic | V1 decision |
|---|---|
| Pilot | One datalens package only; no `atlas-core` or second team |
| Repository | `datalens-atlas` |
| Package | `datalens` |
| Knowledge layers | `_staging/` and `_curated/` |
| Maps | `_curated/maps/` |
| Map authority | Curated Markdown `relationships:` are source of truth; maps are generated projections |
| Curated IDs | Local stable IDs such as `atlas-comp.sds.sds-generic-client` are **not** derived from folder paths |
| Future global reference | Reserve `<package>::<local-id>`, e.g. `datalens::atlas-comp.sds.sds-generic-client` |
| Staging IDs | `STG-YYYYMMDD-<slug>` |
| Type identity | `type:` remains namespaced (`atlas.component`, `atlas.flow`, etc.) |
| Curated status | `draft`, `proposed`, `curated`, `deprecated`, `archived` |
| Confidence | Relationship-level only; no page-level confidence field |
| Staging immutability | Once a staging file is referenced by a curation proposal, its contents and path are immutable |
| Staging outcome | Promotion/rejection is tracked in review/status records, not by mutating consumed staging evidence |
| Curation | One generic `atlas-curate` skill; target folder README + template + index provide type-specific behaviour |
| Standards | Curated standards are grouped by category (`java`, `python`, `aws`, `infra`, `jira`, etc.) |
| Onboarding | V1 includes a deep service-onboarding workflow that scans a repo, follows supplied infra/context locations, asks for missing context, and stages into the correct buckets |
| Standards discovery | V1 includes a separate repo-scanning standards discovery skill |
| Product integration | V1 includes a skill that safely creates/updates an Atlas block in a product repo `CLAUDE.md` |
| `implement-jira` | Included as the example of a reusable engineering skill that resolves team standards rather than hard-coding them |
| Deterministic checks | Python 3.11+; model judgement does not replace validation |
| CI | GitHub Actions for this public prototype and a matching GitLab CI file for eventual internal use |
| Human authority | Claude stages/proposes; humans approve and merge |
| Root `CLAUDE.md` | Primarily governs Claude **maintaining Datalens Atlas**; it is not the cross-repo consumption contract |
| Cross-repo consumption | `--add-dir` exposes Atlas files/skills/agents; skills route via `package.md` and indexes |
| README | Local folder policy and semantic/granularity guidance |
| index.md | Navigation/catalogue, not procedural instructions or routine logs |
| `_template.md` | Authoring contract for a new page in that folder |
| `log.md` | Significant Atlas milestones only |

### 1.1 Important reconciliations

- A folder path may change without changing the page ID. Therefore lint MUST NOT require the ID slug or namespace to equal the physical path.
- `_staging/` is raw evidence. Do not create manually maintained per-bucket staging catalogues in V1; `_staging/index.md` routes by bucket and search/Git handles individual evidence discovery.
- Curated folders do have `index.md` because curated knowledge is deliberately routable.
- Curated maps are committed generated artefacts. They MUST be rebuilt from curated page relationships and checked in CI.
- The `atlas-curate` skill MUST read the target `README.md`, `_template.md`, and `index.md` before changing content. The README defines semantic and granularity rules; the template defines shape; the index defines existing routable content.

---

## 2. File responsibilities — do not blur these boundaries

| Artefact | Primary job |
|---|---|
| `CLAUDE.md` | Operational instructions for Claude while maintaining the Atlas repository |
| `package.md` | Machine-readable package identity, entrypoints, map locations and routing aliases |
| root `index.md` | Front door: route by layer/question |
| `_curated/index.md` | Route questions to trusted concept areas |
| curated folder `README.md` | Local curation policy: meaning, scope, granularity, evidence and reviewer rules |
| curated folder `index.md` | Catalogue/routing to current concept pages |
| curated folder `_template.md` | Exact authoring contract for a new concept page |
| staging folder `README.md` | What raw evidence belongs in that bucket and what does not |
| staging folder `_template.md` | Shape of evidence captured in that bucket |
| `SKILL.md` | A user-facing Claude workflow/procedure |
| `.claude/agents/*.md` | Isolated specialist roles delegated to by skills or Claude |
| curated page | Human-reviewed engineering knowledge |
| staging page | Raw evidence, uncertainty and missing-context record |
| maps | Generated machine-readable projections of curated relationships |
| `reviews/` | Curation reasoning and human-review record |
| `_curated/status/` | Routine operational curation state |
| `log.md` | Significant Atlas-level milestones only |

**Rule:** do not put a `CLAUDE.md` into every content folder. Local rules belong in that folder's README and task procedures belong in skills.

---

## 3. Canonical repository structure

Build this structure exactly. Empty grouping directories may use `.gitkeep`; generated map files must exist even when empty.

```text
datalens-atlas/
├── README.md
├── CLAUDE.md
├── package.md
├── index.md
├── log.md
├── CODEOWNERS
├── .gitignore
├── pyproject.toml
├── .gitlab-ci.yml
├── .github/
│   └── workflows/
│       └── atlas-ci.yml
│
├── taxonomy/
│   ├── README.md
│   ├── types.yaml
│   ├── relationships.yaml
│   ├── statuses.yaml
│   └── standard-categories.yaml
│
├── _curated/
│   ├── README.md
│   ├── index.md
│   ├── components/
│   │   ├── README.md
│   │   ├── index.md
│   │   └── _template.md
│   ├── flows/
│   │   ├── README.md
│   │   ├── index.md
│   │   └── _template.md
│   ├── infra/
│   │   ├── README.md
│   │   ├── index.md
│   │   └── _template.md
│   ├── schema-info/
│   │   ├── README.md
│   │   ├── index.md
│   │   └── _template.md
│   ├── business-concepts/
│   │   ├── README.md
│   │   ├── index.md
│   │   └── _template.md
│   ├── standards/
│   │   ├── README.md
│   │   ├── index.md
│   │   ├── _template.md
│   │   ├── general/index.md
│   │   ├── java/index.md
│   │   ├── python/index.md
│   │   ├── aws/index.md
│   │   ├── infra/index.md
│   │   ├── jira/index.md
│   │   ├── data/index.md
│   │   ├── testing/index.md
│   │   └── git/index.md
│   ├── runbooks/
│   │   ├── README.md
│   │   ├── index.md
│   │   └── _template.md
│   ├── incidents/
│   │   ├── README.md
│   │   ├── index.md
│   │   └── _template.md
│   ├── maps/
│   │   ├── README.md
│   │   ├── index.md
│   │   ├── flow-component-map.json
│   │   ├── repo-dependency-map.json
│   │   └── infra-dependency-map.json
│   └── status/
│       ├── README.md
│       └── curation-status.md
│
├── _staging/
│   ├── README.md
│   ├── index.md
│   ├── changes/
│   │   ├── README.md
│   │   └── _template.md
│   ├── components/
│   │   ├── README.md
│   │   └── _template.md
│   ├── flows/
│   │   ├── README.md
│   │   └── _template.md
│   ├── infra/
│   │   ├── README.md
│   │   └── _template.md
│   ├── schema-info/
│   │   ├── README.md
│   │   └── _template.md
│   ├── business-concepts/
│   │   ├── README.md
│   │   └── _template.md
│   ├── incidents/
│   │   ├── README.md
│   │   └── _template.md
│   ├── runbooks/
│   │   ├── README.md
│   │   └── _template.md
│   └── standards/
│       ├── README.md
│       └── _template.md
│
├── reviews/
│   ├── README.md
│   └── _template.md
│
├── onboarding/
│   ├── README.md
│   ├── index.md
│   ├── service-questionnaire.md
│   ├── standards-questionnaire.md
│   └── local-CLAUDE.template.md
│
├── .claude/
│   ├── skills/
│   │   ├── atlas-discover/SKILL.md
│   │   ├── atlas-impact/SKILL.md
│   │   ├── atlas-stage/SKILL.md
│   │   ├── atlas-onboard-service/SKILL.md
│   │   ├── atlas-onboard-standards/SKILL.md
│   │   ├── atlas-setup-repo/SKILL.md
│   │   ├── atlas-curate/SKILL.md
│   │   └── implement-jira/SKILL.md
│   └── agents/
│       ├── atlas-repo-analyst.md
│       ├── atlas-curator.md
│       ├── atlas-impact-analyst.md
│       └── atlas-reviewer.md
│
├── scripts/
│   ├── atlas_lint.py
│   ├── rebuild_maps.py
│   ├── run_skill_evals.py
│   └── lib/
│       ├── __init__.py
│       ├── frontmatter.py
│       ├── taxonomy.py
│       ├── ids.py
│       ├── links.py
│       └── maps.py
│
└── tests/
    ├── README.md
    ├── unit/
    │   ├── test_frontmatter.py
    │   ├── test_ids.py
    │   ├── test_links.py
    │   ├── test_lint.py
    │   └── test_maps.py
    ├── fixtures/
    │   ├── valid/
    │   └── invalid/
    └── skill-evals/
        ├── atlas-discover.yaml
        ├── atlas-impact.yaml
        ├── atlas-stage.yaml
        ├── atlas-onboard-service.yaml
        ├── atlas-onboard-standards.yaml
        ├── atlas-setup-repo.yaml
        ├── atlas-curate.yaml
        └── implement-jira.yaml
```

### 3.1 Meaningful-folder rule

- Every curated concept folder: `README.md` + `index.md` + `_template.md`.
- Every staging bucket: `README.md` + `_template.md`; **no per-bucket index in V1**.
- `_staging/index.md` routes to buckets but does not catalogue every evidence file.
- Standards category folders are grouping folders: `index.md` only; they inherit policy/template from `_curated/standards/`.
- Maps/status are special folders and do not need templates.

---

## 4. Package and identity model

### 4.1 `package.md`

Create:

```markdown
---
id: atlas-package.datalens
type: atlas.package
package: datalens
schema_version: atlas/1.0
title: Datalens Atlas
description: Governed engineering context for datalens humans and AI agents.
status: active
owners:
  team: datalens-engineering
  maintainers: []
domains: []
entrypoints:
  root: index.md
  curated: _curated/index.md
  staging: _staging/index.md
  components: _curated/components/index.md
  flows: _curated/flows/index.md
  infra: _curated/infra/index.md
  schema_info: _curated/schema-info/index.md
  business_concepts: _curated/business-concepts/index.md
  standards: _curated/standards/index.md
  runbooks: _curated/runbooks/index.md
  incidents: _curated/incidents/index.md
  maps: _curated/maps/index.md
  status: _curated/status/curation-status.md
  onboarding: onboarding/index.md
maps:
  flow_component: _curated/maps/flow-component-map.json
  repo_dependency: _curated/maps/repo-dependency-map.json
  infra_dependency: _curated/maps/infra-dependency-map.json
taxonomy:
  types: taxonomy/types.yaml
  relationships: taxonomy/relationships.yaml
  statuses: taxonomy/statuses.yaml
  standard_categories: taxonomy/standard-categories.yaml
routing:
  aliases: [datalens, data-lens, clearwater]
  questions:
    - What does this datalens service do and depend on?
    - How does this datalens flow work end to end?
    - What could be affected by this infrastructure change?
    - Which datalens standard applies?
---

# Responsibility

Datalens Atlas stores governed engineering context. `_staging/` is evidence; `_curated/` is reviewed knowledge; maps are generated from curated relationships.
```

Do not invent a real team owner during the public prototype. Mark `datalens-engineering` as a placeholder in README/CODEOWNERS.

### 4.2 Curated local ID grammar

IDs are stable logical identities, **not paths**.

Each type declares an ID prefix:

| Type | ID prefix | Example |
|---|---|---|
| `atlas.component` | `atlas-comp` | `atlas-comp.sds.sds-generic-client` |
| `atlas.flow` | `atlas-flow` | `atlas-flow.sds-reference-data-pipeline` |
| `atlas.infra` | `atlas-infra` | `atlas-infra.sds-generic-client` |
| `atlas.schema-info` | `atlas-schema` | `atlas-schema.sds.reference-store` |
| `atlas.business-concept` | `atlas-concept` | `atlas-concept.reference-data.entity` |
| `atlas.standard` | `atlas-standard` | `atlas-standard.java.spring-boot` |
| `atlas.runbook` | `atlas-runbook` | `atlas-runbook.sds.recovery` |
| `atlas.incident-learning` | `atlas-incident` | `atlas-incident.sds.stale-reference-data` |

Rules:

- lowercase ASCII;
- prefix + dot-separated kebab-case segments;
- at least one segment after the prefix;
- ID MUST be unique inside the package;
- folder names do not automatically enter the ID;
- file moves/renames do not force ID changes;
- the namespace segment is semantic (domain/category), not a physical-path checksum;
- a replacement page uses `atlas.supersedes`; do not silently recycle an old ID;
- for future federation, reserve the globally addressable form `datalens::<local-id>`; do not implement cross-package resolution in V1.

This deliberately resolves the earlier contradiction between “filename slug must equal ID” and “renaming a file must not change ID”: **V1 does not enforce filename/ID equality.**

### 4.3 Staging IDs

```text
STG-YYYYMMDD-<slug>
```

Example:

```text
STG-20260807-sds-generic-client-onboarding
```

If a same-day slug already exists, append `-2`, `-3`, etc. Allocation is deterministic by scanning existing filenames/IDs.

---

## 5. Taxonomy contracts

### 5.1 `taxonomy/types.yaml`

Each active type must declare `name`, `folder`, `id_prefix`, and `status`. `grouped` controls storage guidance only and MUST NOT make the folder part of the ID.

```yaml
schema_version: atlas-taxonomy/1.0
types:
  - {name: atlas.package, folder: ".", file: package.md, id_prefix: atlas-package, status: active}
  - {name: atlas.index, folder: "**", id_prefix: atlas-index, status: active}

  - {name: atlas.component, folder: _curated/components, id_prefix: atlas-comp, grouped: true, status: active}
  - {name: atlas.flow, folder: _curated/flows, id_prefix: atlas-flow, grouped: false, status: active}
  - {name: atlas.infra, folder: _curated/infra, id_prefix: atlas-infra, grouped: false, status: active}
  - {name: atlas.schema-info, folder: _curated/schema-info, id_prefix: atlas-schema, grouped: true, status: active}
  - {name: atlas.business-concept, folder: _curated/business-concepts, id_prefix: atlas-concept, grouped: false, status: active}
  - {name: atlas.standard, folder: _curated/standards, id_prefix: atlas-standard, grouped: true, status: active}
  - {name: atlas.runbook, folder: _curated/runbooks, id_prefix: atlas-runbook, grouped: false, status: active}
  - {name: atlas.incident-learning, folder: _curated/incidents, id_prefix: atlas-incident, grouped: false, status: active}

  - {name: atlas.join-path, folder: _curated/join-paths, id_prefix: atlas-join, status: reserved}
  - {name: atlas.query-pattern, folder: _curated/query-patterns, id_prefix: atlas-query, status: reserved}
  - {name: atlas.decision, folder: _curated/decisions, id_prefix: atlas-decision, status: reserved}

  - {name: atlas.staging.change, folder: _staging/changes, status: active}
  - {name: atlas.staging.component, folder: _staging/components, status: active}
  - {name: atlas.staging.flow, folder: _staging/flows, status: active}
  - {name: atlas.staging.infra, folder: _staging/infra, status: active}
  - {name: atlas.staging.schema-info, folder: _staging/schema-info, status: active}
  - {name: atlas.staging.business-concept, folder: _staging/business-concepts, status: active}
  - {name: atlas.staging.incident, folder: _staging/incidents, status: active}
  - {name: atlas.staging.runbook, folder: _staging/runbooks, status: active}
  - {name: atlas.staging.standard, folder: _staging/standards, status: active}
```

### 5.2 `taxonomy/relationships.yaml`

V1 approved relationships:

```yaml
schema_version: atlas-taxonomy/1.0
relationships:
  - atlas.depends-on
  - atlas.consumes
  - atlas.produces
  - atlas.participates-in
  - atlas.deployed-by
  - atlas.must-follow
  - atlas.owned-by
  - atlas.implemented-by
  - atlas.derived-from
  - atlas.supersedes
  - atlas.operated-by
  - atlas.informed-by
  - atlas.extends
```

Each real implementation entry should also carry `meaning`, allowed source/target kinds where useful, and reciprocal display semantics. Reciprocal relationships are **derived views**, not duplicate authoring requirements.

Map routing rules:

- `atlas.participates-in` → flow-component map;
- component `atlas.consumes`, `atlas.produces`, `atlas.depends-on` → repo-dependency map;
- infra `atlas.depends-on`, `atlas.deployed-by`, infra/resource usage → infra-dependency map;
- flow-to-flow dependencies → flow-component map;
- runbook/incident/standard relationships may be surfaced as routing metadata but do not create a fourth map.

### 5.3 `taxonomy/statuses.yaml`

```yaml
schema_version: atlas-taxonomy/1.0
curated_status:
  - draft
  - proposed
  - curated
  - deprecated
  - archived

staging_status:
  - new
  - awaiting-evidence
  - ready-for-curation
  - archived

relationship_confidence:
  - reviewed
  - possible
  - unconfirmed
  - conflicting

map_coverage:
  - none
  - partial
  - good
  - stale
  - unknown
```

Promotion state does not live in consumed staging files; use `reviews/` and `_curated/status/curation-status.md`.

### 5.4 `taxonomy/standard-categories.yaml`

```yaml
schema_version: atlas-standard-categories/1.0
categories:
  - general
  - java
  - python
  - aws
  - infra
  - jira
  - data
  - testing
  - git
```

Categories are routing/organisation, not separate standard types. Add categories by reviewed taxonomy change rather than silently inventing a near-duplicate folder.

---

## 6. Common page contracts

### 6.1 Curated common envelope

Every curated concept page begins with:

```yaml
---
id: atlas-<type>.<namespace>.<slug>
type: atlas.<type>
package: datalens
schema_version: atlas/1.0
title: ""
description: ""
status: proposed
last_reviewed: YYYY-MM-DD
reviewed_by: []
owners: []
routing:
  aliases: []
  domains: []
relationships: []
evidence: []
coverage:
  level: unknown
  notes: []
---
```

Rules:

- `status: curated` requires non-empty `reviewed_by`, valid `last_reviewed`, and evidence unless the page declares a documented exemption;
- `atlas-curate` writes/updates pages as `proposed`, never `curated`;
- relationship certainty is stored on each edge, not the page;
- `routing.domains` must be declared in `package.md` before use;
- evidence must point to staging files, repository paths, external references, or reviewer-confirmed sources;
- no secrets, credentials, customer data, raw sensitive logs or unnecessary personal data.

### 6.2 Relationship object

```yaml
relationships:
  - type: atlas.consumes
    target: atlas-schema.sds.reference-store
    kind: table
    confidence: reviewed
    note: ""
    evidence:
      - _staging/components/STG-20260807-example.md
```

For `atlas.consumes`, `atlas.produces` and `atlas.depends-on`, `kind` is required. Allowed initial kinds:

```text
event api table file component shared-library schema-library config job-output infra other
```

A reviewed local target must resolve to a real curated ID. If the target is genuinely outside datalens and no Atlas package exists in V1, mark the relationship as external in `note`/evidence and do not pretend it resolves locally. Cross-package link syntax is reserved, not implemented.

### 6.3 Staging common envelope

```yaml
---
id: STG-YYYYMMDD-<slug>
type: atlas.staging.<bucket>
package: datalens
schema_version: atlas/1.0
timestamp: YYYY-MM-DD
title: ""
description: ""
status: new
captured_by: ""
source_type: ""
source_links: []
intended_curated_targets: []
---
```

Staging pages explicitly preserve unknowns, possible relationships and reviewer questions. They do not require every field to be known.

### 6.4 Not-covered marker

When a required body section genuinely has no evidence, use exactly:

```markdown
*Not covered — no evidence in current staging material.*
```

Do not invent plausible filler.

---

## 7. Root files

### 7.1 Root `CLAUDE.md`

This file governs Claude while **maintaining Datalens Atlas**. It is intentionally short and does not duplicate every folder's curation rules.

Create:

```markdown
# Datalens Atlas — Claude operating rules

This repository is the Datalens Atlas package (`datalens`). It is a governed engineering context layer, not a general document dump.

## Trust

- `_staging/` is raw evidence and is never authoritative.
- `_curated/` is reviewed knowledge; only `status: curated` is authoritative.
- Claude may stage and propose; Claude never self-approves or merges knowledge.
- Never invent missing engineering context.

## How repository rules are organised

- `package.md` defines package identity and entrypoints.
- `index.md` files route to existing knowledge.
- A target folder's `README.md` defines semantic, granularity, evidence and reviewer rules.
- A target folder's `_template.md` defines page shape.
- Skills in `.claude/skills/` define workflows.

## Editing Atlas

- Before curating into a folder, read that folder's `README.md`, `_template.md`, and `index.md`.
- Edit relationships only on curated Markdown pages.
- Never hand-edit generated relationship data in `_curated/maps/*.json`.
- After relationship changes run `python scripts/rebuild_maps.py`.
- Before proposing changes run `python scripts/atlas_lint.py .` and tests.
- Once staging evidence has been referenced by curation, do not alter or move it. Add new corrective evidence instead.

## Navigation

Do not read the entire Atlas repository. Start from `index.md` or the relevant skill and open the smallest useful set of files.

## Operational records

- routine curation state → `_curated/status/curation-status.md`
- detailed curation reasoning → `reviews/`
- significant Atlas milestones only → `log.md`
```

### 7.2 Root `index.md`

Must route by question/layer and link to:

- `_curated/index.md`
- `_staging/index.md`
- `_curated/maps/index.md`
- `_curated/status/curation-status.md`
- `onboarding/index.md`
- `taxonomy/README.md`
- root `README.md`

Do not list every concept page here.

### 7.3 Root `README.md`

Required headings:

```text
Purpose
Pilot scope
Repository structure
Trust model
File responsibilities
How to browse Atlas
How to use Atlas from another repository
Available Claude skills
Service onboarding
Standards discovery
Curation and review
Map generation
Validation and tests
CI
Security and sensitive data
Contribution triggers
What not to capture
Placeholder values to replace before internal adoption
```

Cross-repo example:

```bash
cd <product-repo>
claude --add-dir <path-to>/datalens-atlas
```

Explain that cross-repo consumption relies on discovered skills + `package.md`/indexes; it does not require the added directory's root `CLAUDE.md` to become the consumer contract.

### 7.4 `log.md`

```markdown
# Datalens Atlas Log

Significant Atlas-level milestones only. Routine curation belongs in `_curated/status/curation-status.md`; detailed reasoning belongs in `reviews/`.

| Date | Milestone | Evidence / PR/MR |
|---|---|---|
| YYYY-MM-DD | V1 repository scaffold created | |
```

### 7.5 `CODEOWNERS`

Use generic placeholders only:

```text
* @datalens-engineering
/_curated/ @datalens-engineering
/.claude/ @datalens-engineering
/taxonomy/ @datalens-engineering
/scripts/ @datalens-engineering
```

README must state that the placeholder must be replaced before enforcing protected-branch review.

---

## 8. Folder contracts and templates

### 8.1 Every curated concept README must contain

1. Purpose
2. Trust level
3. When to use this area
4. When not to use it
5. Granularity rule
6. Storage/filename convention
7. Required frontmatter/type-specific fields
8. Relationship guidance
9. Evidence expectations
10. `not covered` rule
11. Agent curation instructions
12. Reviewer checklist
13. Index maintenance rule
14. Security/sensitivity reminder

### 8.2 Every curated concept index must contain

- route-by-question section;
- catalogue table: `ID | Title | Status | Domain/category | Last reviewed | Page`;
- coverage notes;
- group/category indexes where applicable;
- no routine curation log entries.

Archived pages are excluded from normal routing/catalogue but remain in place and in Git history.

### 8.3 Components

Granularity: one page per meaningful repo, service, deployable unit, scheduled job group or reusable library. Do not split every handler/Lambda/script by default.

Type-specific frontmatter:

```yaml
component_type: unknown
component_scope: unknown
repository: ""
monorepo_path: ""
deployed_as: []
contains_internal_units: false
```

Required body headings:

```text
Summary
Responsibility
Location
Internal units
Consumes
Produces
Flows
Infrastructure
Local repository references
Operational notes
Runbooks
Standards
Incident learnings
Evidence
Possible relationships
Open questions / coverage limits
```

### 8.4 Flows

Granularity: one end-to-end operational/data path crossing meaningful steps/components.

Fields:

```yaml
flow_scope: ""
trigger: ""
schedule: ""
entry_component: ""
exit_component: ""
```

Body:

```text
Summary
Purpose and boundary
Entry point
End-to-end steps
Participating components
Inputs and outputs
Upstream dependencies
Downstream consumers
Jobs and schedules
Infrastructure
Failure modes
Runbooks
Incident learnings
Standards
Evidence
Possible relationships
Open questions / coverage limits
```

### 8.5 Infra

Granularity: normally one meaningful infra package/template. Lower-level resources remain internal unless shared, independently operated, incident-relevant, security-sensitive, deletion-sensitive, flow-critical, or a significant blast-radius node.

Fields:

```yaml
infra_package: ""
template_path: ""
resource_names: []
environments: []
promoted_resources: []
```

Body:

```text
Summary
Package location and structure
Environment notes
Internal resources
Promoted resources and promotion reason
Resource relationships
Components using resources
Flows using resources
Parameters/imports/exports
Schedules/triggers/events
Permissions and roles
Monitoring
Impact if changed or deleted
Evidence
Possible relationships
Open questions / coverage limits
```

### 8.6 Schema info

Fields:

```yaml
asset_kind: unknown
physical_name: ""
platform: ""
grain: ""
primary_keys: []
business_keys: []
temporal_model: unknown
latest_record_rule: ""
classification: unknown
```

Body:

```text
Summary
Business meaning
Physical identity
Grain
Keys
Temporal model
Important fields
Producers
Consumers
Approved/known joins
Quality issues
Classification and access notes
Evidence
Open questions / coverage limits
```

### 8.7 Business concepts

Fields:

```yaml
approved_definition: ""
inclusion_criteria: []
exclusion_criteria: []
approved_variants: []
```

Body: definition, boundaries, examples, non-examples, related data assets, standards, evidence, open questions.

### 8.8 Standards — grouped by category

Yes: group curated standards. This gives humans and skills a predictable route without creating new standard types.

Canonical paths:

```text
_curated/standards/java/<slug>.md
_curated/standards/python/<slug>.md
_curated/standards/aws/<slug>.md
_curated/standards/jira/<slug>.md
_curated/standards/infra/<slug>.md
...
```

A category is organisational. The page remains `type: atlas.standard`.

Fields:

```yaml
standard_category: java
applies_to: []
mandatory: false
scope: team
exceptions: []
```

Body:

```text
Standard
Scope
Rationale
Required behaviour
Recommended behaviour
Examples
Anti-patterns
Exceptions
Related standards
Evidence
Open questions / coverage limits
```

`standard_category` must be in `standard-categories.yaml`. The physical category folder SHOULD match it; lint emits ERROR on mismatch for new pages, but moving an existing page does not change its ID.

### 8.9 Runbooks

Fields: `covers: []`, `severity_scope`, `last_exercised`.

Body: purpose, trigger/symptom, prerequisites, safety, investigation, recovery, validation, rollback, escalation, monitoring, evidence.

### 8.10 Incident learnings

This is reusable operational learning, not a full incident-management record.

Fields: `incident_date`, `severity`, `resolved`.

Body: sanitised summary, impact, cause, detection, recovery, reusable learning, runbook/standard gaps, evidence, sensitive-data note.

### 8.11 Staging buckets

Every bucket README defines what belongs there and what does not. Every `_template.md` extends the staging envelope.

Buckets and purpose:

| Bucket | Purpose |
|---|---|
| `changes` | Reusable context discovered during a logical code/change investigation |
| `components` | Raw repo/service/component discovery |
| `flows` | Raw end-to-end flow evidence |
| `infra` | Raw IaC/package/resource evidence |
| `schema-info` | Raw table/event/file/API/data-contract evidence |
| `business-concepts` | Raw supplied business definitions/meaning |
| `incidents` | Sanitised reusable incident/near-miss learning |
| `runbooks` | Draft operational procedures |
| `standards` | Candidate reusable team standards/conventions |

Each template must include: summary, evidence, what is known, what is possible/unconfirmed, suggested curated targets, and open questions.

### 8.12 Reviews

`reviews/_template.md`:

```text
Staging evidence considered
Curated pages affected
Decision: CREATE / UPDATE / DEFER / REJECT / CONFLICT
Claims accepted
Claims not accepted
Relationship decisions
Open questions
Lint/map results
Human reviewer
Outcome
```

Recommended filename:

```text
reviews/STG-YYYYMMDD-<slug>-review.md
```

### 8.13 Curation status

`_curated/status/curation-status.md` is an operational ledger, not authoritative engineering knowledge.

Table:

```text
Area | Last run | Staging evidence | Proposed pages | Review state | Coverage note | PR/MR
```

Track promotion/rejection here rather than editing already-consumed staging evidence.

---

## 9. Map generation

### 9.1 Authority rule

```text
Curated Markdown pages explain and author relationships.
JSON maps are generated projections.
Lint verifies the projections.
```

No human or skill may directly author map relationships.

### 9.2 Required maps

```text
_curated/maps/flow-component-map.json
_curated/maps/repo-dependency-map.json
_curated/maps/infra-dependency-map.json
```

Every map metadata block contains:

```json
{
  "schema_version": "atlas-map/1.0",
  "generated": true,
  "generator": "scripts/rebuild_maps.py",
  "package": "datalens",
  "source_of_truth": ["_curated/**/*.md"]
}
```

Generated output must be deterministically sorted and byte-stable for the same inputs.

### 9.3 `scripts/rebuild_maps.py`

CLI:

```bash
python scripts/rebuild_maps.py
python scripts/rebuild_maps.py --check
```

Behaviour:

1. walk active/proposed/curated concept pages under `_curated/` excluding maps/status/templates/README/index;
2. parse frontmatter;
3. validate IDs and relationship vocabulary before generation;
4. ignore `archived` pages from normal maps;
5. project `atlas.participates-in` and flow dependencies into `flow-component-map.json`;
6. project component consumes/produces/depends-on into `repo-dependency-map.json`;
7. project infra/resource/deployment relationships into `infra-dependency-map.json`;
8. derive reverse views; never require authors to duplicate reciprocal edges;
9. carry confidence and evidence into projected edges;
10. sort keys/arrays deterministically;
11. write maps, or with `--check`, compare generated bytes to committed files and exit non-zero on drift.

A relationship that cannot be projected should remain valid on the page if it is in the taxonomy, but the generator must report why it was not included in a map.

---

## 10. Claude skills required for V1

Skills are procedures, not storage for datalens facts. Keep them package-agnostic where possible so they can later move to `atlas-core`.

### 10.1 `atlas-discover` — read-only consumer route

Frontmatter intent:

```yaml
name: atlas-discover
description: Use when answering a question about a datalens system, service, flow, infrastructure, schema, runbook or standard. Route through curated Atlas before broad code scanning and label fallback clearly.
allowed-tools: Read, Grep, Glob
```

Procedure:

1. locate the Atlas root from the skill location and read `package.md`;
2. read root/curated index relevant to the question;
3. route to the smallest concept/index/map set;
4. use only `status: curated` as authoritative;
5. cite page ID + path for Atlas-backed claims;
6. if not covered, say what is missing, then allow normal repo discovery outside the skill workflow if the active agent has access;
7. label scan-derived conclusions separately;
8. never write staging, curated, maps, status or review files.

### 10.2 `atlas-impact` — read-only blast-radius analysis

Use for “what breaks if X changes/deletes/fails?” questions.

Procedure: resolve starting concept → page relationships → relevant generated map → reverse edges → linked flows/components/infra → bucket results as **known affected / possibly affected / unknown or not covered** → cite evidence. Never claim “not affected” merely because an edge is absent.

Allowed tools: `Read, Grep, Glob` only.

### 10.3 `atlas-stage` — generic evidence capture

Use when a reusable fact is discovered during normal work and should enter Atlas without performing a full onboarding crawl.

Procedure: identify bucket → read bucket README + template → ask only blocking questions → allocate staging ID → capture source/evidence/uncertainty → write one staging entry → run staging lint. Never write curated content.

When knowledge came from a private conversation/external source, require explicit user approval before writing it.

### 10.4 `atlas-onboard-service` — V1 super onboarding workflow

This is the primary V1 onboarding skill. It is intentionally broader than `atlas-stage` and can delegate deep scanning to `atlas-repo-analyst`.

It MUST:

1. identify the active service/repository and Atlas root;
2. read `onboarding/README.md`, `service-questionnaire.md`, `_staging/components/README.md` and template;
3. perform a broad but bounded repository scan;
4. build an evidence matrix for component responsibility, inputs, outputs, interfaces, runtime/deployment, infra, flows, schedules/triggers, schema/data assets, runbooks/docs, operational signals and known owners;
5. discover likely infra references or external repo/path references without assuming they are correct;
6. ask the user one consolidated clarification round for important missing pieces (especially infra location, known upstream/downstream systems, flow boundary/name, ownership and inaccessible docs/repos);
7. if the user supplies an accessible path/additional directory, inspect it and update the evidence matrix;
8. ask a second targeted clarification only when a missing answer blocks correct staging; do not interrogate the user for optional details;
9. distinguish **observed**, **user-confirmed**, **possible**, and **not covered**;
10. stage only supported evidence into the necessary buckets:
   - always component if a service was successfully identified;
   - infra only when infra evidence exists;
   - flow only when an end-to-end boundary is evidenced or user-confirmed;
   - schema-info when durable interfaces/data assets are material;
   - runbook/incident evidence only when present;
11. do **not** create empty placeholder staging files just because a category is missing;
12. do not curate or generate authoritative relationships;
13. finish with an onboarding report: files staged, missing evidence, likely next curation targets, and optional recommendation to run `atlas-onboard-standards` and/or `atlas-setup-repo`.

Allowed tools: `Read, Grep, Glob, Bash, Write, Edit`. Bash is for bounded repo inspection commands; no destructive commands.

#### Required scan signals

At minimum inspect when present:

```text
README/CONTRIBUTING/docs
CLAUDE.md
pom.xml / build.gradle* / settings.gradle*
pyproject.toml / requirements*.txt
package.json
Dockerfile / docker-compose*
.gitlab-ci.yml / .github/workflows/*
CODEOWNERS
src/ and obvious config directories
application*.yml/properties
Terraform / CloudFormation / CDK / SAM / Serverless files
service catalogue / metadata files
API/OpenAPI/schema/event definitions
migration/DDL/SQL locations
schedulers/cron/EventBridge/Step Functions/workflow config
runbooks/operational docs
```

Do not recursively dump entire large/generated/vendor directories. Ignore `.git`, `node_modules`, `target`, `build`, `.venv`, binaries and generated outputs unless explicitly relevant.

### 10.5 `atlas-onboard-standards` — standards discovery crawler

Purpose: discover **candidate reusable team standards** from one or more repositories without confusing repo-local configuration or tool defaults with team policy.

It may reuse `atlas-repo-analyst` in `standards-discovery` mode.

Procedure:

1. read `_staging/standards/README.md`, template and `taxonomy/standard-categories.yaml`;
2. inspect policy/config evidence such as `CONTRIBUTING`, README guidance, CI templates, parent POMs, shared Gradle config, lint/format config, test config, PR templates, Jira conventions documented in repo, IaC conventions, security checks, common scripts and repeated patterns;
3. classify each finding as:
   - `team-standard-candidate`
   - `repo-local-convention`
   - `tool-default`
   - `unknown-scope`
4. never promote a tool default or one-repo habit to “team standard” without evidence/user confirmation;
5. compare candidates with existing curated standards/indexes;
6. ask the user to confirm scope/authority for ambiguous high-value candidates;
7. stage a standards discovery record containing candidate category, rule, source paths, scope evidence, exceptions/unknowns and suggested curated target;
8. one scan may contain multiple candidates; curation may later split them into separate curated standard pages;
9. do not write curated standards.

### 10.6 `atlas-setup-repo` — safely create/update local `CLAUDE.md`

Purpose: make a product repo Atlas-ready without replacing the repo's own instructions.

Rules:

- preserve all existing user content outside an Atlas-managed block;
- if no `CLAUDE.md` exists, create one with only a short repository heading plus the managed block;
- never copy Atlas knowledge into the local file;
- local repo remains owner of build/test/run commands;
- default to package + component logical identity, not an absolute Atlas filesystem path;
- if no curated component ID exists yet, write package-only routing and mark component identity unresolved; do not point Claude to staging as authoritative;
- show the diff before finishing.

Managed block markers:

```markdown
<!-- atlas:managed:start -->
## Atlas context

Home Atlas package: `datalens`
Atlas component: `<curated component id or unresolved>`

When Datalens Atlas is available (for example through `claude --add-dir <atlas-path>`):
1. use the `atlas-discover` skill before broad platform-context scanning;
2. use `atlas-impact` for blast-radius questions;
3. treat `_curated/` as authoritative only for pages with `status: curated`;
4. treat `_staging/` as evidence only;
5. if Atlas does not cover the question, continue with normal repository discovery and label the result as not Atlas-backed.

This repository owns its exact build, test, lint and local-development commands.
<!-- atlas:managed:end -->
```

On rerun, replace only the contents between those markers.

### 10.7 `atlas-curate` — generic curation workflow

This skill MUST use the target folder README; the template alone is insufficient.

Procedure:

1. read staging evidence;
2. read `taxonomy/types.yaml`, `relationships.yaml`, `statuses.yaml`;
3. resolve target curated area;
4. **read target `README.md`;**
5. **read target `_template.md`;**
6. **read target `index.md`;**
7. for standards, also read the category index and standards category taxonomy;
8. search for existing concept pages by ID, alias, repository path and semantic match;
9. decide `CREATE`, `UPDATE`, `DEFER`, `REJECT` or `CONFLICT`;
10. on material conflict, stop automatic reconciliation and surface the conflict for human resolution;
11. create/update the proposed page using the template and README's granularity rules;
12. preserve evidence and uncertainty; do not turn possible claims into reviewed edges;
13. propose typed relationships and resolve local targets to real IDs;
14. use the not-covered marker where evidence is absent;
15. set page status to `proposed`, never `curated`;
16. update the relevant curated index/category index;
17. run `python scripts/rebuild_maps.py`;
18. update `_curated/status/curation-status.md`;
19. create/update the review note in `reviews/`;
20. run `python scripts/atlas_lint.py .` and tests relevant to the change;
21. summarise pages changed, relationships proposed, confidence, open questions, map diff and validation results;
22. never merge or self-approve.

### 10.8 `implement-jira` — reusable software-principles example

Purpose: demonstrate an organisation-agnostic engineering skill whose procedure is reusable while standards remain Datalens knowledge.

Procedure:

1. resolve home package via local `CLAUDE.md`/Atlas `package.md`;
2. resolve the applicable Jira implementation standard starting from `_curated/standards/jira/index.md`;
3. follow `atlas.extends` if the standard specialises another standard;
4. resolve relevant component and flow context;
5. inspect the product repo's own build/test instructions;
6. implement in small steps;
7. run local required validation;
8. report the Atlas standards/pages used;
9. if reusable new context is discovered, **ask user approval** before invoking/staging via `atlas-stage`;
10. never change curated Atlas knowledge as a side effect of implementing a Jira item.

---

## 11. V1 subagents

### 11.1 `atlas-repo-analyst`

Read-only deep repository specialist used by onboarding and standards discovery.

Tools: `Read, Grep, Glob, Bash` (read-only commands only).  
Output: structured evidence matrix with source paths, findings, confidence, missing context and candidate relationships.  
Never writes Atlas or product files.

Modes supported in prompt/instructions:

- `service-onboarding`
- `standards-discovery`

### 11.2 `atlas-curator`

Specialist for reconciling staged evidence with existing curated knowledge. May write **proposed Atlas files only**. No merge/approval capability.

Must follow target README/template/index and return a proposed-change summary.

### 11.3 `atlas-impact-analyst`

Read-only specialist for systematic graph traversal. Produces known/possible/unknown impact buckets with evidence. Never modifies code or Atlas.

### 11.4 `atlas-reviewer`

Read-only independent reviewer of an Atlas proposal. Checks:

- evidence supports claims;
- relationship targets/types are sensible;
- uncertainty was not upgraded silently;
- granularity follows the target README;
- index/map/status changes are complete;
- sensitive information is not introduced;
- lint/tests passed.

It produces findings only; it does not “approve” on behalf of a human.

---

## 12. Onboarding operating model

### 12.1 Service onboarding state machine

```text
START
  ↓
identify active repo + Atlas root
  ↓
read onboarding + staging contracts
  ↓
repo-analyst broad scan
  ↓
build evidence matrix
  ↓
identify material gaps
  ↓
ask consolidated clarification
  ↓
follow user-supplied accessible locations
  ↓
second targeted clarification only if blocking
  ↓
stage supported component / infra / flow / schema / runbook evidence
  ↓
run lint on staging
  ↓
report staged files + missing pieces + next actions
END
```

### 12.2 Evidence matrix minimum fields

```text
Question
Finding
Source path/reference
State: observed | user-confirmed | possible | not-covered
Candidate Atlas target
Blocking for staging? yes/no
```

### 12.3 Clarification policy

Ask about high-value gaps, not every unknown. Prioritise:

- service responsibility if ambiguous;
- authoritative infra location if not in repo;
- known upstream/downstream systems that code cannot establish;
- flow boundary/name when multiple paths exist;
- owner/SME for review;
- external docs/repositories explicitly referenced by the service but not accessible.

When a user supplies a path that is not available to Claude, tell them exactly what needs to be added/provided. Do not invent what might be there.

### 12.4 Onboarding output rule

A successful onboarding run may create several staging files, but only where evidence exists. Example:

```text
_staging/components/STG-20260807-sds-generic-client.md
_staging/infra/STG-20260807-sds-generic-client-infra.md
_staging/flows/STG-20260807-sds-reference-flow.md
_staging/schema-info/STG-20260807-sds-reference-store.md
```

It MUST NOT directly create curated pages.

---

## 13. Standards operating model

### 13.1 Why group standards

Standards are a high-frequency routing surface. Grouping lets a human or skill answer “what Java/Jira/AWS rule applies?” without reading an unbounded flat list. Categories remain navigation only; `atlas.standard` remains the single semantic type.

### 13.2 Category semantics

- `general`: team-wide engineering/process rules not better classified;
- `java`: Java/JVM/Spring/build conventions;
- `python`: Python packaging/runtime/style/test conventions;
- `aws`: AWS-specific usage/deployment/security/operations conventions;
- `infra`: IaC/service-catalogue/environment/deployment conventions not specific to one cloud service;
- `jira`: story implementation, evidence, branch/PR/MR/process conventions;
- `data`: schema/data-quality/data-engineering conventions;
- `testing`: testing strategy, minimum validation and test organisation;
- `git`: branching/commit/review/source-control conventions.

Do not duplicate the same standard in multiple categories. Pick a primary category and link from related standards.

### 13.3 Standard resolution order

For V1:

```text
product-repo documented exception
        ↓
datalens curated standard(s)
        ↓
local repo implementation detail
```

When federation/core exists later, insert organisation/core standards above datalens and use `atlas.extends` for specialisation.

---

## 14. Lint contract

`scripts/atlas_lint.py <path> [--format text|json] [--warn-as-error]`

At minimum implement:

| Code | Level | Rule |
|---|---|---|
| ATLAS001 | ERROR | YAML frontmatter parses for governed page files |
| ATLAS002 | ERROR | `type` is active and file is under an allowed folder |
| ATLAS003 | ERROR | curated local `id` matches that type's `id_prefix` and is unique |
| ATLAS004 | ERROR | `package` equals `datalens` |
| ATLAS005 | ERROR | reserved types cannot have pages |
| ATLAS006 | ERROR | curated status is valid |
| ATLAS007 | ERROR | `status: curated` has reviewer/date/evidence |
| ATLAS008 | ERROR | relative Markdown links resolve |
| ATLAS009 | ERROR | relationship type is allowed |
| ATLAS010 | ERROR | reviewed local relationship target resolves to a real local ID |
| ATLAS011 | ERROR | required relationship `kind` is present and valid |
| ATLAS012 | ERROR | relationship confidence valid; non-reviewed edge has explanatory note |
| ATLAS013 | ERROR | non-archived curated page appears in correct folder/category index |
| ATLAS014 | ERROR | archived page excluded from normal index/catalogue |
| ATLAS015 | ERROR | evidence paths resolve when local |
| ATLAS016 | ERROR | required body sections are not silently empty: content or not-covered marker |
| ATLAS017 | ERROR | standard category is allowed and matches storage category |
| ATLAS018 | ERROR | generated maps match `rebuild_maps.py --check` |
| ATLAS019 | ERROR | obvious secret patterns absent |
| ATLAS020 | WARN | curated page exceeds default review age (180 days, configurable) |
| ATLAS021 | ERROR | consumed staging evidence has not been moved/modified within the proposed change when detectable from Git diff/metadata |
| ATLAS022 | WARN | component `deployed_as` values have no corresponding infra evidence/resource name |

Exempt README, `_template.md`, generated maps, review docs, root operational docs and skill/agent markdown from governed-page frontmatter rules unless separately validated.

Lint never decides semantic truth.

---

## 15. Testing and skill evaluation

### 15.1 Unit tests

Test:

- frontmatter parsing;
- ID prefix/uniqueness;
- folder/type validation;
- links;
- standard category validation;
- relationship target validation;
- deterministic map generation;
- map `--check` drift detection;
- not-covered rule;
- secret detection.

### 15.2 Fixtures

`tests/fixtures/valid/`: at least one passing example for every active curated type.  
`tests/fixtures/invalid/`: at least one single-purpose failure for every ERROR lint rule where practical.

Fixtures use package `fixtures` or an explicit lint-fixture mode so they do not collide with real datalens IDs/maps/indexes.

### 15.3 Skill eval files

Every skill eval YAML must contain:

- `should_trigger` prompts;
- `should_not_trigger` prompts;
- expected files to read/write;
- forbidden writes/actions;
- outcome assertions.

Minimum outcome assertions:

**atlas-discover:** no write; routes to curated; labels fallback.  
**atlas-impact:** reports known/possible/unknown; no “not affected” from absence.  
**atlas-stage:** writes one correct staging bucket; no curated write.  
**atlas-onboard-service:** can produce multiple correct staging buckets; asks targeted gaps; no fabricated infra/flows.  
**atlas-onboard-standards:** separates repo-local/tool-default from team-standard candidates.  
**atlas-setup-repo:** preserves non-Atlas CLAUDE content and replaces only managed block.  
**atlas-curate:** reads README + template + index; status stays proposed; maps regenerated; no self-approval.  
**implement-jira:** resolves Jira standard before implementation and does not mutate curated Atlas as a side effect.

`run_skill_evals.py` may implement deterministic fixture assertions first; model-trigger evaluations may remain a documented/manual harness if the local environment cannot invoke isolated Claude sessions.

---

## 16. CI

### 16.1 GitHub Actions — `.github/workflows/atlas-ci.yml`

Run on push and pull request:

```text
checkout
setup Python 3.11
pip install -e .[dev]
python scripts/atlas_lint.py .
python scripts/rebuild_maps.py --check
pytest
python scripts/run_skill_evals.py --deterministic
```

A scheduled weekly job runs freshness lint. Do not automatically modify page status.

### 16.2 `.gitlab-ci.yml`

Provide equivalent `validate`, `graph`, `test`, `freshness` stages using the same scripts. Do not duplicate validation logic in CI YAML; CI only invokes repository scripts.

GitHub/GitLab CI are gates, not semantic approvers.

---

## 17. `pyproject.toml`

Use Python 3.11+. Runtime dependency: `PyYAML`. Dev dependency: `pytest`.

Expose no network requirement. All lint/map/test operations must work offline against the repository tree.

---

## 18. Build phases and phase acceptance

### Phase 1 — skeleton + root contracts

Create canonical tree, root files, taxonomy files, CI placeholders and Python packaging.

**Pass when:** required paths exist; taxonomy YAML parses; root links resolve.

### Phase 2 — deterministic tooling first

Implement `scripts/lib/*`, `atlas_lint.py`, `rebuild_maps.py`, unit-test harness and initial fixtures.

**Pass when:** unit tests for parser/IDs/links/maps pass; empty repo lint has zero errors.

### Phase 3 — curated folder contracts

Create all curated README/index/template files, including standards category indexes and maps/status docs.

**Pass when:** every curated concept folder has README/index/template; standard categories match taxonomy; links resolve.

### Phase 4 — staging/review/onboarding contracts

Create staging README/templates, review template and onboarding docs/questionnaires/template.

**Pass when:** every staging bucket has README/template; no unnecessary staging bucket index exists; onboarding docs reference real paths only.

### Phase 5 — generated maps

Generate the three initial empty maps with `rebuild_maps.py`; never hand-author them.

**Pass when:** all parse; `generated: true`; `--check` is clean; second generation produces byte-identical files.

### Phase 6 — skills

Implement all eight V1 skills exactly to §10 contracts.

**Pass when:** skill frontmatter parses; read-only skills have no write tools; every referenced Atlas path exists; deterministic skill evals pass.

### Phase 7 — agents

Implement the four subagents.

**Pass when:** permissions match §11; reviewer/impact/repo-analyst are non-authoritative; no agent has autonomous merge instructions.

### Phase 8 — full CI + acceptance

Finish GitHub and GitLab CI, README quick-start, fixtures and full tests.

**Pass when:** local CI-equivalent commands all pass from a clean checkout.

---

## 19. Final V1 acceptance criteria

V1 is complete only when all are true:

1. repository tree satisfies §3;
2. every curated concept folder has its local policy README, navigation index and template;
3. every staging bucket has README + template and no unnecessary per-bucket catalogue;
4. root `CLAUDE.md` governs Atlas maintenance rather than acting as the only cross-repo consumption mechanism;
5. `atlas-curate` explicitly reads target README + template + index before curation;
6. standards are grouped under approved categories and searchable from the parent/category indexes;
7. `atlas-onboard-service` can scan a fixture service, ask/record missing context, follow a supplied fixture infra location, and stage component + supported linked evidence into correct buckets;
8. the onboarding skill does not create unsupported flow/infra placeholder evidence;
9. `atlas-onboard-standards` distinguishes team-standard candidates from repo-local/tool-default configuration;
10. `atlas-setup-repo` safely creates/updates an Atlas-managed block without deleting existing `CLAUDE.md` content;
11. `atlas-discover` and `atlas-impact` are read-only;
12. `implement-jira` resolves datalens Jira standards rather than embedding them in the skill;
13. maps are reproducibly generated from curated page relationships;
14. direct map drift is detected;
15. indexes contain all non-archived curated pages and no archived pages;
16. consumed staging evidence is not rewritten as part of curation;
17. lint, map check, pytest and deterministic skill evals pass;
18. GitHub Actions invokes the same deterministic checks;
19. GitLab CI equivalent exists for later transfer;
20. no datalens production facts were fabricated to make the scaffold look complete.

### 19.1 Required demonstration fixtures

Build fake fixtures only, clearly labelled fixtures, to demonstrate:

- one service repo with Java or Python build metadata;
- a separate fixture infra directory referenced by that service;
- one evidenced flow relation and one intentionally missing flow fact;
- candidate standards including one genuine repeated/team-like candidate and one obvious tool default;
- an existing local `CLAUDE.md` containing non-Atlas instructions;
- a curated fixture relationship that regenerates each of the three map types.

These are tests, not datalens knowledge.

---

## 20. Security and safety rules

- No credentials, API keys, tokens, private keys, connection strings, customer data, raw sensitive query output or unnecessary personal data.
- Onboarding crawls only repositories/directories available to the active user/session.
- Do not bypass repository permissions.
- Do not treat inaccessible context as absent context.
- Do not autonomously follow external links or private systems unless the user/session provides an approved accessible tool/path.
- A skill that learns reusable context from a private conversation must ask before persisting it.
- Claude proposes; humans approve.

---

## 21. V1 non-goals

Do not build:

- `atlas-core`;
- second-team federation;
- package registry;
- cross-package traversal engine;
- UI/catalogue application;
- vector database/search service;
- Backstage integration;
- automatic Confluence/Teams/Jira ingestion;
- autonomous PR/MR approval or merge;
- `join-paths`, `query-patterns`, `decisions`, `data-lineage-map.json` or `external-dependency-map.json` as active V1 features;
- a general-purpose enterprise crawler.

The onboarding crawler is deliberately bounded to the active service plus locations the user explicitly supplies or already exposed to the Claude session.

---

## 22. Implementation completion report

At the end, the implementation agent must report:

```text
Repository structure: PASS/FAIL
Required files: <count>
Skills: 8/8
Agents: 4/4
Curated concept contracts: <count>/expected
Staging bucket contracts: <count>/expected
Maps generated: 3/3
Lint: PASS/FAIL + warning count
Map check: PASS/FAIL
Pytest: PASS/FAIL + test count
Deterministic skill evals: PASS/FAIL
GitHub Actions config: PASS/FAIL
GitLab CI config: PASS/FAIL
Unresolved external blockers: ...
Fabricated datalens knowledge: MUST BE 0
```

Do not declare completion if a required deterministic check is failing.

---

# Appendix A — Design rationale for the V1 skill/agent split

The split intentionally avoids both extremes: one enormous prompt that does everything, and dozens of near-duplicate skills.

- **Skills** represent user-recognisable workflows.
- **Agents** isolate deep specialist work and permission boundaries.
- **Folder READMEs** provide concept-local curation policy.
- **Templates** provide page shape.
- **Taxonomy/scripts** provide deterministic contracts.

This is why `atlas-onboard-service` can be a “super skill” without becoming an unmaintainable monolith: it orchestrates the read-only `atlas-repo-analyst`, asks the user for context only where needed, then stages evidence according to existing bucket contracts. Curation remains a separate workflow and human review remains the authority boundary.

# Appendix B — First real adoption sequence after the scaffold

Once V1 exists and is transferred into an authorised datalens environment:

```text
1. Attach datalens-atlas to a real service repo with --add-dir.
2. Run atlas-onboard-service.
3. Answer the targeted missing-context questions and expose the infra repo/path if required.
4. Review the generated staging evidence.
5. Optionally run atlas-onboard-standards for reusable team-standard candidates.
6. Run atlas-curate on selected staging evidence.
7. Human reviews/merges the Atlas proposal.
8. Run atlas-setup-repo to add/update the product repo's Atlas CLAUDE.md block using the curated component ID.
9. Use atlas-discover / atlas-impact during normal engineering work.
10. Use atlas-stage when new reusable context is discovered.
```

