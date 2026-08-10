# DataLens Atlas — Complete Documentation

Consolidated transcription of the Atlas repository's governing documents, curated-layer
guides and templates, dependency-map documentation, status tracking and staging rules.

## Contents

**Part 1 — Governance**
1. [CLAUDE.md — Operating Rules for DataLens Atlas](#1-claudemd--operating-rules-for-datalens-atlas)

**Part 2 — Curated knowledge layer**
2. [`_curated/index.md` — DataLens Atlas](#2-_curatedindexmd--datalens-atlas)
3. [`_curated/flows/README.md`](#3-_curatedflowsreadmemd)
4. [`_curated/flows/` page template](#4-_curatedflows-page-template)
5. [`_curated/components/README.md`](#5-_curatedcomponentsreadmemd)
6. [`_curated/components/` page template](#6-_curatedcomponents-page-template)
7. [`_curated/infra/README.md`](#7-_curatedinfrareadmemd)
8. [`_curated/infra/` page template](#8-_curatedinfra-page-template)

**Part 3 — Dependency maps**
9. [`_curated/maps/README.md` — Curated Maps](#9-_curatedmapsreadmemd--curated-maps)
10. [`flow-component-map.json` — partial capture](#10-flow-component-mapjson--partial-capture)
11. [`repo_dependency_map_README.md`](#11-repo_dependency_map_readmemd)
12. [`infra_dependency_map_README.md`](#12-infra_dependency_map_readmemd)

**Part 4 — Operational status**
13. [`_curated/status/curation-status.md`](#13-_curatedstatuscuration-statusmd)

**Part 5 — Staging layer**
14. [`_staging/README.md`](#14-_stagingreadmemd)
15. [`_staging/runbooks/template.md`](#15-_stagingrunbookstemplatemd)
16. [`_staging/standards/template.md`](#16-_stagingstandardstemplatemd)
17. [Appendix — Staging sub-folder READMEs and templates](#17-appendix--staging-sub-folder-readmes-and-templates)

---


# Part 1 — Governance

# 1. CLAUDE.md — Operating Rules for DataLens Atlas

## Purpose

This repository is the central Clearwater Atlas repository.

Atlas is a governed engineering context layer for DataLens. It captures raw engineering knowledge in `_staging/`, turns reviewed knowledge into `_curated/`, and gives humans, Claude Code, GitLab Duo and future Copilot Agents a clean, routable source of engineering context.

Atlas is not a Confluence replacement, not a service catalogue replacement and not a general document dump.

---

## Repository layers

```
_staging/          Raw evidence and proposed knowledge. Not trusted.
_curated/          Reviewed source-of-truth engineering context.
.claude/skills/    Approved executable Claude workflows.
claude-assets/     Reusable Claude assets, guides and catalogues.
reviews/           Detailed curation review notes and evidence summaries.
log.md             Significant Atlas milestones and governance-level history.
CLAUDE.md          Operating rules for this repository.
```

If older folders named `staging/` or `curated/` exist, prefer `_staging/` and `_curated/` for new work.

---

## Core trust model

`_staging/` is raw and untrusted.

`_curated/` is trusted only after GitLab review and lead approval.

Claude can propose changes. Claude is not the final authority.

The normal knowledge flow is:

```
Raw source or engineer knowledge
-> _staging/ entry using a template
-> Claude-assisted curation proposal
-> GitLab MR
-> knowledgeable reviewer checks correctness
-> lead approval
-> merge into _curated/
```

Do not write new knowledge directly into `_curated/` unless it is part of a reviewed curation MR.

---

## Atlas knowledge model

Atlas is flow-first, component-accessible and map-backed.

### Flows

`_curated/flows/` explains end-to-end DataLens behaviour:

- flow purpose;
- entry point and output;
- ordered steps;
- components involved;
- upstream and downstream dependencies;
- jobs and schedules;
- infrastructure involved;
- runbooks;
- incident learnings;
- coverage limits.

Flows are the primary route for understanding behaviour, incidents and blast radius.

### Components

`_curated/components/` explains meaningful repos/components:

- responsibility;
- monorepo path;
- component type;
- internal units where useful;
- consumes and produces relationships;
- related flows;
- related infrastructure;
- runbooks, standards and incident learnings.

A component page usually represents one meaningful repo, submodule, deployable unit, scheduled job group, service, library or operationally relevant component.

Do not create one component page per Lambda, Glue job, SQL file, handler, script or config file by default. Capture these as `Internal units` unless they are independently deployable, independently scheduled, independently operated, incident-relevant, flow-critical or reused across multiple components.

### Infrastructure

`_curated/infra/` explains meaningful infra packages or important shared infrastructure resources.

A curated infra page usually represents one infra package/folder, especially where the folder contains:

- `product.template.yaml`;
- `metadata.yaml`;
- `preconfig.sh`;
- `dev/`;
- `uat/`;
- `prod/`;
- `src/`.

Do not create one infra page per environment folder, script, YAML resource or cloud resource by default. Capture resources inside the parent infra page unless the resource is shared, operationally critical, independently operated, incident-relevant or a major blast-radius node.

---

## Folder structure

Expected structure:

```
_staging/
  README.md
  changes/
  flows/
  components/
  infra/
  incidents/
  runbooks/
  standards/
  archive/

_curated/
  index.md
  flows/
    index.md
  components/
    index.md
  infra/
    index.md
  maps/
    README.md
    flow-component-map.json
    repo-dependency-map.json
    infra-dependency-map.json
  runbooks/
    index.md
  standards/
    index.md
  incidents/
    learnings/
      index.md
  status/
    README.md
    curation-status.md

claude-assets/
  README.md
```

---

## Staging rules

All new knowledge lands in `_staging/` first.

Every staging entry should:

- use the relevant `template.md`;
- include YAML frontmatter;
- include `type`, `title`, `description`, `resource`, `tags` and `timestamp` where possible;
- identify source type and source link where available;
- preserve raw wording where useful;
- separate evidence from interpretation;
- mark uncertainty explicitly;
- list possible `_curated/` targets;
- avoid secrets, credentials, tokens, unnecessary production data and unnecessary personal data.

Do not rewrite staging files to make them look curated. If clarification is needed, add review notes, create a follow-up entry or capture the decision in the curation MR.

---

## Staging folders

Use the correct staging folder:

| Folder | Use for |
|---|---|
| `_staging/changes/` | Logical changes, MRs, release bundles, code changes and Claude-discovered local repo context |
| `_staging/flows/` | End-to-end DataLens flows or pipelines |
| `_staging/components/` | Repo/component/service/job/API/Lambda/library context |
| `_staging/infra/` | Infra packages, service catalogue templates, resources and environment configuration |
| `_staging/incidents/` | Real incidents, mock incidents, near misses and operational learnings |
| `_staging/runbooks/` | Draft or updated operational procedures |
| `_staging/standards/` | Reusable engineering standards, conventions and guidance |

### Changes folder rule

`_staging/changes/` is organised around a logical change, not necessarily one MR.

A logical change may involve:

- one MR in one repo;
- multiple MRs across multiple repos;
- a release bundle;
- a local Claude Code investigation that discovers reusable Atlas context.

Every production-bound MR should be considered for Atlas. Not every MR requires a curated update.

---

## Curated rules

`_curated/` contains reviewed source-of-truth engineering context.

When updating curated knowledge:

1. Prefer updating an existing page over creating a duplicate.
2. Link related pages using normal Markdown links.
3. Keep pages short, evidence-backed and routable.
4. Do not mirror Confluence verbatim.
5. Do not copy full incident records into Atlas unless explicitly allowed.
6. Include evidence links for material claims.
7. Make coverage limits explicit.
8. Use "possible", "unconfirmed", "no known dependency found" or "not covered" instead of unsupported certainty.
9. Avoid saying "not affected" unless Atlas explicitly supports that claim.

---

## Index maintenance rule

`index.md` files are folder catalogues and navigation aids.

They should help humans and agents discover what a folder contains. They are not routine curation logs and should not be used to track every curation run.

When a curation skill creates, renames, archives or materially changes a curated page, it must update the relevant folder `index.md` if the page should be discoverable from that folder.

Examples:

- creating `_curated/components/trade-processing/trade-loader.md` should update `_curated/components/index.md` or `_curated/components/trade-processing/index.md` if that group index exists;
- creating `_curated/flows/trade-ingestion.md` should update `_curated/flows/index.md`;
- creating `_curated/infra/tradedata-api-monthly-flow.md` should update `_curated/infra/index.md`;
- creating `_curated/runbooks/trade-ingestion-failure.md` should update `_curated/runbooks/index.md`.

Archiving or renaming a curated page should update the relevant index only.

Do not write routine curation run status to `index.md`.

Routine curation status belongs in:

```
_curated/status/curation-status.md
```

Detailed curation reasoning belongs in:

```
reviews/STG-YYYY-NNNN-review.md
```

Root `log.md` is reserved for significant Atlas milestones only.

---

## Curation status and log policy

Routine curation run tracking belongs in:

```
_curated/status/curation-status.md
```

Use this file to track, by area, when curation last ran, which staging item was considered, the related branch or MR, coverage status and notes.

Detailed curation reasoning belongs in `reviews/`.

Use a review file when a curation proposal needs to record:

- files consulted;
- evidence used;
- map updates;
- index updates;
- skipped paths and why;
- reviewer questions.

Use root `log.md` only for significant Atlas-level milestones, such as:

- major flow onboarding;
- major component or domain onboarding;
- major infra model updates;
- dependency-map schema changes;
- important incident learnings;
- governance or review-process changes;
- publishing-model changes.

Do not log every staging file, minor curation run, small component edit or routine map consistency fix in root `log.md`.

---

## Dependency maps

Atlas uses three separate maps.

```
_curated/maps/flow-component-map.json
_curated/maps/repo-dependency-map.json
_curated/maps/infra-dependency-map.json
```

Do not recreate a single all-purpose `dependency-map.json`.

### `flow-component-map.json`

Flow-centred routing map.

Use it for:

- flow entry points;
- ordered flow steps;
- participating components;
- high-level outputs;
- direct upstream flows;
- direct downstream flows;
- relevant runbooks;
- relevant incident learnings;
- coverage notes.

It is a routing helper, not the full dependency graph.

Do not put detailed infra resource relationships, IAM/KMS/secrets, service catalogue package details, full API/event/table dependency detail, shared-library chains or resource deletion impact in this map.

### `repo-dependency-map.json`

Component-centred repo/application/data dependency map.

Use it for:

- components;
- events;
- APIs;
- tables;
- files;
- job outputs;
- shared libraries;
- config dependencies;
- component-to-component relationships.

This map is nested under components. Do not introduce a separate abstract `contracts` section unless the team explicitly adopts that as a map design.

### `infra-dependency-map.json`

Infra-package-centred infrastructure dependency map with a selective promoted resource index.

Use it for:

- infra packages;
- service catalogue templates;
- promoted resources;
- resource relationships;
- environment configuration;
- schedules, triggers and events;
- roles and permissions;
- monitoring and alarms;
- component usage of infra resources;
- flow usage of infra resources;
- impact of infra package/resource deletion or change.

Only promote a resource into the map-level `resources` index when it is important for impact analysis: shared, data-bearing, data-routing, orchestration-critical, security-sensitive, deletion-sensitive, incident-relevant, monitored, used by multiple components/flows/packages, or likely to be searched directly during incident triage or impact analysis.

---

## Map consistency

If a curated page says a relationship exists, the relevant map should reflect it.

- Flow page participant -> `flow-component-map.json`
- Component consumes/produces relationship -> `repo-dependency-map.json`
- Infra package/resource relationship -> `infra-dependency-map.json`

Lint checks are a safety net, not a substitute for updating the relevant map in the same MR.

---

## Routing behaviour for Claude

Do not read the whole Atlas before answering.

Use targeted routing:

1. If the user asks about a flow, start in `_curated/maps/flow-component-map.json`, then read the relevant `_curated/flows/` page and participating component pages.
2. If the user asks about a component/repo, start in `_curated/components/` and `_curated/maps/repo-dependency-map.json`.
3. If the user asks about infrastructure, shared AWS resources, service catalogue templates or product deletion impact, start in `_curated/infra/` and `_curated/maps/infra-dependency-map.json`.
4. If the user asks about operational recovery, read relevant `_curated/runbooks/` and incident learnings.
5. If the user asks about standards, read `_curated/standards/`.
6. If the required context is not found after targeted reads, say what is missing and do not guess.

`index.md` files are for navigation and folder catalogues, but do not rely on them as the only routing path.

---

## Local repo usage

Atlas is normally attached while Claude is working inside a local repo:

```
cd <working-repo-or-component>
claude --add-dir <path-to-atlas>
```

The local repo `CLAUDE.md` should instruct Claude to read relevant Atlas files, for example:

```
## Atlas context
Path: ~/atlas
Component page: _curated/components/<group>/<component>.md
Related flow pages:
- _curated/flows/<flow>.md
Maps:
- _curated/maps/flow-component-map.json
- _curated/maps/repo-dependency-map.json
- _curated/maps/infra-dependency-map.json
```

For repository-specific automatic discovery, local repos may also declare:

```
atlas-component: <group>/<component>
atlas-root: ~/atlas
```

The local repo owns exact build/test commands and repo-specific development quirks. Atlas may link to local README or local `CLAUDE.md`, but should avoid duplicating command details that are likely to drift.

---

## Central vs local `CLAUDE.md`

### Central Atlas `CLAUDE.md`

This file owns:

- Atlas operating rules;
- staging and curated workflow;
- map rules;
- index maintenance rules;
- curation status and log policy;
- curation behaviour;
- cross-repo routing principles;
- team skill guidance.

### Local repo `CLAUDE.md`

A local repo `CLAUDE.md` should own:

- local build/test/lint commands;
- local development setup;
- repo-specific quirks;
- pointer to the Atlas component page;
- pointer to related Atlas flows/maps;
- local usage notes that belong near code.

Local `CLAUDE.md` should usually stay short. If it becomes a platform explanation, move that knowledge into Atlas staging.

---

## Skills

Approved skills live under:

```
.claude/skills/<skill-name>/SKILL.md
```

Skills are invoked as:

```
/<skill-name>
```

When a user asks which skills are available, read:

```
claude-assets/skills-catalog.md
```

Important current skills may include:

```
/atlas-discover
/atlas-onboard-flow
/atlas-curate-component
/atlas-curate-flow
/atlas-curate-infra
/atlas-curate-linked-context
/atlas-lint
```

Skill proposals should be staged and reviewed before promotion to `.claude/skills/`.

### `atlas-discover`

Use `/atlas-discover` when Claude needs reusable engineering context before scanning or searching the codebase.

The skill should:

- check Atlas first for questions about repos, flows, infra, standards, runbooks, incidents, dependencies and component connections;
- read only the minimum relevant Atlas files;
- use `index.md` as navigation, not as complete source-of-truth;
- use the three maps for routing and relationship lookup;
- label answer provenance as Atlas-backed, scan/code-backed, not covered or possible/unconfirmed;
- fall back to normal discovery when Atlas does not cover the question;
- suggest a staging entry if fallback discovery reveals reusable context.

The skill must not:

- curate staging into curated;
- create or modify staging entries;
- update maps;
- update status files;
- create reports;
- run lint;
- create diagrams;
- decide approval status;
- replace human review.

### `atlas-onboard-flow`

Use `/atlas-onboard-flow` when the user wants to capture a new or existing flow into Atlas staging from a working repo.

The skill should:

- be callable from a local repo with Atlas added via `--add-dir`;
- capture one flow staging entry under `_staging/flows/`;
- capture component staging entries under `_staging/components/` where useful;
- capture or suggest infra staging entries under `_staging/infra/` where useful;
- ask targeted questions only for context it cannot infer;
- accept pasted notes;
- avoid writing to `_curated/`.

Use this skill for flow onboarding. Do not use repo-only onboarding patterns unless the task is truly only about a single component.

---

## Curation workflow

When curating staging material:

1. Read the staging entry.
2. Identify the intended durable target.
3. Read existing relevant curated pages and maps.
4. Decide whether to update, create, defer or reject.
5. Preserve evidence links.
6. Mark uncertainty explicitly.
7. Update pages and maps together where needed.
8. Update relevant `index.md` files when pages are created, renamed, archived or materially changed.
9. Update `_curated/status/curation-status.md` for routine curation status where appropriate.
10. Create or update a review note in `reviews/` for non-trivial curation decisions.
11. Add a root `log.md` entry only for significant Atlas-level milestones.
12. Create a reviewable MR.
13. Leave the raw staging entry intact.

If the source contradicts existing curated content, do not silently overwrite. Add an explicit contradiction note in the proposed curated update or MR description and ask for reviewer decision.

---

## Capturing learnings after a task

Create a staging entry if a task reveals:

- a non-obvious cross-repo connection;
- a new or changed event/API/table/file/job dependency;
- infra behaviour that affects a component or flow;
- a recurring failure pattern;
- a runbook gap;
- a standard or convention worth reusing;
- context Claude needed but could not find in Atlas.

Choose the correct `_staging/` subfolder.

---

## Review and approval

A curated update should be approved by:

- at least one knowledgeable reviewer; and
- a lead where required by GitLab rules or local team process.

The MR should include enough evidence and explanation for reviewers to understand what is being trusted.

Reviewer options:

```
APPROVE
REQUEST_CHANGES
REJECT
DEFER_FOR_EVIDENCE
```

If evidence is missing, do not force the knowledge into `_curated/`. Keep it staged and mark the gap.

---

## Linting and validation

`/atlas-lint` or equivalent scripts should check:

- JSON validity;
- broken links;
- missing evidence;
- duplicate IDs;
- component page and repo map consistency;
- infra page and infra map consistency;
- flow page and flow map consistency;
- curated pages missing from relevant `index.md` files;
- `index.md` links that point to missing or archived pages;
- routine curation run status being written to `index.md` instead of `_curated/status/curation-status.md`;
- promoted infra resources without a promotion reason;
- internal units over-split into component pages without justification;
- invalid paths;
- obvious secret patterns.

Linting does not decide truth. It only detects structural issues.

---

## Secrets and sensitive data policy

Do not stage or curate:

- API keys;
- credentials;
- tokens;
- secrets;
- unnecessary account identifiers;
- unnecessary personal data;
- raw sensitive logs;
- customer data;
- production data extracts.

Redact sensitive material before saving:

```
[REDACTED]
```

If sensitive context is necessary, link to the authorised source instead of copying it into Atlas.

---

## Optional publishing principle

Future SharePoint/OneDrive/Copilot publication is a projection, not a second source of truth.

Correct direction:

```
_curated/ Git content
-> generated publication snapshot
-> SharePoint/OneDrive/Copilot consumption
```

Never allow free-form edits in SharePoint to become a competing source of truth.

Do not publish `_staging/` content.

---

## Do not

- Do not treat `_staging/` as trusted.
- Do not update `_curated/` without a staging source and review path.
- Do not recreate a single `dependency-map.json` for everything.
- Do not duplicate flow detail inside component pages.
- Do not duplicate component implementation detail inside flow pages.
- Do not create one page per internal file by default.
- Do not mirror Confluence verbatim.
- Do not copy full incident records unless explicitly allowed.
- Do not claim "not affected" unless explicitly supported.
- Do not read the entire Atlas repo before answering.
- Do not invent repo, flow, infra or owner facts.
- Do not overwrite contradictions silently.
- Do not put secrets or sensitive raw data in Atlas.
- Do not use `index.md` as a routine curation run tracker.


---

# Part 2 — Curated knowledge layer

# 2. `_curated/index.md` — DataLens Atlas

## Purpose

Atlas is the governed engineering context layer for DataLens. It captures raw engineering knowledge in `_staging/`, turns reviewed knowledge into `_curated/`, and gives humans, Claude Code, GitLab Duo and future Copilot Agents a clean, routable source of engineering context.

## Repository layers

| Layer | Purpose | Trust level |
|---|---|---|
| `_curated/` | Reviewed source-of-truth engineering context | Trusted after GitLab review |
| `_staging/` | Raw evidence and proposed knowledge | Untrusted — evidence only |
| `.claude/skills/` | Approved executable Claude workflows | Trusted after review |
| `claude-assets/` | Reusable Claude assets, guides and catalogues | Reference |
| `reviews/` | Detailed curation review notes and evidence summaries | Review artefacts |

## Quick navigation

### Curated knowledge (trusted)

- **Flows** — `_curated/flows/index.md` — end-to-end DataLens behaviour
- **Components** — `_curated/components/index.md` — repos, services, jobs, APIs
- **Infrastructure** — `_curated/infra/index.md` — infra packages and shared resources
- **Maps** — `_curated/maps/` — dependency maps for routing and impact analysis
- **Standards** — `_curated/standards/` — engineering conventions

### Operational

- **Curation status** — `_curated/status/curation-status.md` — routine tracking
- **Atlas log** — `log.md` — significant milestones only
- **Skills catalogue** — `claude-assets/skills-catalog.md` — available Claude skills

### Staging (raw evidence)

- **Staging root** — `_staging/README.md` — staging rules and folder guide

## For AI agents

Use targeted routing, not full reads:

1. Flow questions → `_curated/maps/flow-component-map.json` → `_curated/flows/`
2. Component questions → `_curated/components/index.md` → `_curated/maps/repo-dependency-map.json`
3. Infrastructure questions → `_curated/infra/index.md` → `_curated/maps/infra-dependency-map.json`
4. Operational recovery → `_curated/runbooks/` and incident learnings
5. Standards → `_curated/standards/`

## Governance

- Operating rules: `CLAUDE.md`


---

# 3. `_curated/flows/README.md`

## _curated/flows/

### Purpose

`_curated/flows/` contains reviewed, trusted Atlas flow pages.

A flow page explains how a DataLens flow or pipeline behaves end to end, which components and infrastructure participate, what dependencies are known, which runbooks apply, and what incident learnings should be remembered.

A curated flow page should help answer:

> How does this flow work, what does it depend on, what depends on it,
> and what might be affected if it fails or changes?

### Trust rule

Files in `_curated/flows/` are trusted Atlas knowledge only after GitLab review and lead approval.

Do not copy raw staging notes into a flow page without filtering them into reviewed, evidence-backed statements.

If a statement is useful but not confirmed, keep it in one of these sections:

- `Open questions / coverage limits`
- `Possible relationships`
- `Unconfirmed dependencies`

Do not present possible or unconfirmed knowledge as fact.

### What belongs in a flow page

A flow page should include:

- the purpose of the flow;
- the flow boundary;
- the entry point and end point;
- end-to-end steps;
- components involved;
- upstream dependencies;
- downstream consumers;
- jobs, schedules and orchestration points;
- related infrastructure packages/resources;
- known contracts and data outputs;
- relevant runbooks;
- relevant incident learnings;
- evidence links;
- coverage limits and open questions.

### What does not belong in a flow page

Do not use a flow page for:

- detailed implementation notes that belong in a component page;
- full incident records;
- one-off MR summaries;
- raw staging evidence;
- every internal SQL file, Lambda handler or Glue script;
- service catalogue metadata that is not needed for understanding the flow;
- unsupported impact claims.

### Flow granularity rule

A flow page should represent a meaningful end-to-end behaviour or pipeline, not every small internal step.

Create a flow page when the flow:

- crosses multiple components or repos;
- has operational or incident relevance;
- has upstream/downstream dependency impact;
- has runbooks or known failure modes;
- produces or moves data used by others;
- is useful for Claude Code, GitLab Duo, Copilot or human lookup.

Do not create a separate flow page for every job, Lambda or SQL script unless that unit is independently meaningful as a flow.

### Relationship to components

Flow pages should link to component pages, but should not duplicate component detail.

Use component pages for:

- component responsibility;
- monorepo path;
- internal units;
- consumes/produces relationships;
- local development guidance;
- component-specific runbooks or incident learnings.

Use flow pages for:

- end-to-end behaviour;
- ordering of steps;
- flow-level blast radius;
- upstream/downstream view;
- operational story.

### Relationship to dependency maps

Flow pages should stay consistent with:

```text
_curated/maps/flow-component-map.json
_curated/maps/repo-dependency-map.json
_curated/maps/infra-dependency-map.json
```

Use each map for the right type of relationship:

| Map | Use for |
|---|---|
| `_curated/maps/flow-component-map.json` | Which components and infra resources participate in a flow |
| `_curated/maps/repo-dependency-map.json` | Repo/component/job/API/event/table/data contract relationships |
| `_curated/maps/infra-dependency-map.json` | Infra package/template/resource relationships |

If a flow page says a component participates in the flow, `flow-component-map.json` should reflect that.

If a flow page says a component consumes or produces a contract, `repo-dependency-map.json` should reflect that.

If a flow page says a resource supports the flow, `infra-dependency-map.json` or `flow-component-map.json` should reflect that.

### Required filename format

Use a stable, readable slug:

```text
<flow-name>.md
```

Examples:

```text
trade-ingestion-to-warehouse.md
pricing-refresh.md
reference-data-publication.md
tradedata-api-monthly-flow.md
```

Do not include dates in curated filenames unless the date is part of the concept name. Dates belong in frontmatter and evidence, not the canonical file path.

### Required frontmatter

Each curated flow page must use YAML frontmatter.

Required fields:

```yaml
type: atlas.flow
title: ""
description: ""
resource: ""
tags: []
timestamp: YYYY-MM-DD
atlas_id: FLOW-XXXX
status: curated
confidence: reviewed
last_reviewed: YYYY-MM-DD
reviewed_by: ""
source_staging_ids: []
related_flows: []
related_components: []
related_repo_dependencies: []
related_infra_dependencies: []
related_runbooks: []
related_incident_learnings: []
related_standards: []
map_refs:
  flow_component_map: "_curated/maps/flow-component-map.json"
  repo_dependency_map: "_curated/maps/repo-dependency-map.json"
  infra_dependency_map: "_curated/maps/infra-dependency-map.json"
```

### Evidence expectations

Every material claim in a flow page should have evidence or be marked as a coverage limit.

Evidence may include:

- staging entry;
- component page;
- repo path;
- config path;
- schema or contract path;
- infra package/template path;
- runbook;
- incident learning;
- Jira/Confluence/SharePoint link;
- reviewer-confirmed statement.

### Status and confidence

A curated flow page should normally use:

```yaml
status: curated
confidence: reviewed
```

If the page is being built but not fully confirmed, use:

```yaml
status: draft-curated
confidence: partial
```

and make coverage limits explicit.

### Claude instructions

When using a curated flow page, Claude should:

1. read the flow page before making flow-level claims;
2. follow component links for local implementation detail;
3. inspect dependency maps for structured relationships;
4. inspect runbooks for operational guidance;
5. inspect incident learnings for known failure modes;
6. distinguish confirmed, possible and unknown relationships;
7. avoid saying "not affected" unless the page or maps explicitly support that claim;
8. prefer "no known dependency found" or "not covered" where evidence is incomplete.

### Reviewer checklist

Before approving a flow page update, check:

- Is the flow boundary clear?
- Are entry point and output clear?
- Are steps accurate and evidence-backed?
- Are components linked to component pages?
- Are infra resources linked or mapped correctly?
- Are upstream and downstream dependencies supported?
- Are contracts/data outputs represented correctly?
- Are runbooks and incident learnings relevant?
- Are dependency-map updates consistent with the page?
- Are unconfirmed claims clearly marked?
- Is the page useful to both humans and Claude?


---

# 4. `_curated/flows/` page template

```yaml
type: atlas.flow
title: ""
description: ""
resource: ""
tags: []
timestamp: YYYY-MM-DD
atlas_id: FLOW-XXXX
status: curated
confidence: reviewed
last_reviewed: YYYY-MM-DD
reviewed_by: ""

source_staging_ids: []
related_flows: []
related_components: []
related_repo_dependencies: []
related_infra_dependencies: []
related_runbooks: []
related_incident_learnings: []
related_standards: []

map_refs:
  flow_component_map: "_curated/maps/flow-component-map.json"
  repo_dependency_map: "_curated/maps/repo-dependency-map.json"
  infra_dependency_map: "_curated/maps/infra-dependency-map.json"
```

## Flow: <flow name>

### Summary

Briefly describe the flow in plain language.

Example:

> This flow ingests trade data, processes it through DataLens components,
> stores the curated output and exposes it to downstream consumers.

### Purpose

Explain the business or technical purpose of the flow.

### Flow boundary

Define what is inside and outside this flow.

- Starts at:
- Ends at:
- In scope:
- Out of scope:

### Entry point

Describe what starts the flow.

Examples:

- schedule;
- event;
- API request;
- file arrival;
- manual trigger;
- upstream job completion.

### End-to-end steps

List the reviewed flow steps.

| Step | Description | Component/job/resource | Evidence |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |

### Components involved

Link to curated component pages where available.

| Component | Role in flow | Monorepo path | Evidence |
|---|---|---|---|
| | | | |

### Internal units involved

Use this only when lower-level units matter to understanding the flow. Do not list every file by default.

| Parent component | Internal unit | Type | Role in flow | Evidence |
|---|---|---|---|---|
| | | lambda/glue-job/sql/script/handler/other | | |

### Upstream dependencies

List confirmed upstream dependencies.

| Dependency | Type | Required by | Evidence |
|---|---|---|---|
| | event/api/table/file/job/config/system | | |

### Downstream consumers

List confirmed downstream consumers.

| Consumer | Type | Consumes/depends on | Evidence |
|---|---|---|---|
| | component/job/api/report/table/system | | |

### Contracts and data outputs

List reviewed APIs, events, schemas, tables, files or job outputs that matter to this flow.

| Contract/output | Type | Produced by | Consumed by | Evidence |
|---|---|---|---|---|
| | api/event/schema/table/file/job-output | | | |

### Jobs and schedules

List relevant jobs, batches, schedules or orchestration points.

| Job/schedule | Role | Trigger/frequency | Evidence |
|---|---|---|---|
| | | | |

### Infrastructure involved

Link to curated infra pages or infra map entries where available.

| Infra package/resource | Role in flow | Evidence |
|---|---|---|
| | | |

### Known failure modes

List reviewed failure modes.

| Failure mode | Symptom | Likely affected area | Evidence |
|---|---|---|---|
| | | | |

### Runbooks

List runbooks relevant to this flow.

- `_curated/runbooks/...`

### Incident learnings

List incident learnings relevant to this flow.

- `_curated/incidents/learnings/...`

### Standards

List standards relevant to this flow.

- `_curated/standards/...`

### Evidence

List the key evidence used to curate this page.

- Staging entry:
- Component page:
- Repo path:
- Config path:
- Schema/contract path:
- Infra package/template:
- Runbook:
- Incident learning:
- Jira/Confluence/SharePoint reference:
- Reviewer-confirmed statement:

### Possible relationships

Relationships that may be true but are not yet confirmed.

| Relationship | Why it is possible | Evidence gap |
|---|---|---|
| | | |

### Open questions / coverage limits

Be explicit about what Atlas does not yet know.

- Unknown consumers:
- Unknown upstream dependencies:
- Unknown infra relationships:
- Unverified compatibility:
- Areas not covered by this page:

### Change history

| Date | Change | Source/review |
|---|---|---|
| YYYY-MM-DD | Initial curated page | |


---

# 5. `_curated/components/README.md`

## _curated/components/

### Purpose

`_curated/components/` contains reviewed, trusted Atlas component pages.

A component page explains what a DataLens repo, service, job, API, Lambda, library, batch, consumer, producer or other meaningful implementation component does, where it lives, what it consumes and produces, which flows it participates in, and which runbooks, standards, incident learnings and infrastructure dependencies are relevant.

A curated component page should help answer:

> What is this component, where does it live, what does it do, what depends on it,
> what does it depend on, and which flows or operations does it affect?

### Trust rule

Files in `_curated/components/` are trusted Atlas knowledge only after GitLab review and lead approval.

Do not copy raw staging notes into a component page without filtering them into reviewed, evidence-backed statements.

If a statement is useful but not confirmed, keep it in one of these sections:

- `Possible relationships`
- `Open questions / coverage limits`
- `Unconfirmed dependencies`

Do not present possible or unconfirmed knowledge as fact.

### Recommended folder structure

Component folders should normally mirror the top-level monorepo grouping where that helps Claude and humans map local paths to Atlas.

Example:

```text
_curated/components/
  index.md
  trade-processing/
    index.md
    trade-loader.md
    settlement-batch.md
  data-ingestion/
    index.md
    source-consumer.md
  warehouse-core/
    index.md
    trade-core-loader.md
  shared-libraries/
    index.md
    pricing-utils.md
...
```

The top-level folder is a routing and navigation aid. It is not necessarily a business domain or the source of truth for behaviour. Flow pages remain the primary operational story.

### Component granularity rule

A component page should usually represent one meaningful repo, monorepo submodule, deployable unit, scheduled job group, service, API, library or operationally relevant component.

Do not create a separate component page for every Lambda, Glue job, SQL file, handler, script or config file by default.

Instead, capture lower-level artefacts inside the parent component page under `Internal units`.

Create a separate component page for an internal unit only if it is:

- independently deployable;
- independently scheduled;
- independently operated or monitored;
- attached to its own runbook;
- used by multiple flows;
- has its own consumers or downstream dependencies;
- has blast-radius impact on its own;
- changed often enough to need a stable Atlas page.

### Component context and granularity rule

A component page should usually represent one meaningful repo, monorepo submodule, deployable unit, scheduled job group, service, API, library or operationally relevant component.

Atlas should use the monorepo/domain folder as context, the repo/component as the main page, and lower-level artefacts as internal units.

Example:

```text
DataLens
-> trade-processing
-> trade-loader
-> internal units: Lambdas, Glue jobs, SQL files, handlers, scripts
```

### What belongs in a component page

A component page should include:

- component responsibility;
- monorepo path;
- component type;
- domain/group folder;
- local repository or package context;
- internal units where useful;
- consumes relationships;
- produces relationships;
- related flows;
- related infrastructure;
- relevant runbooks;
- relevant standards;
- relevant incident learnings;
- evidence links;
- coverage limits and open questions.

### What does not belong in a component page

Do not use a component page for:

- a full flow narrative that belongs in `_curated/flows/`;
- raw MR history;
- full incident records;
- service catalogue metadata that is not useful for engineering context;
- every internal file in the repo;
- every implementation detail from source code;
- unsupported dependency or ownership claims.

### Relationship to flows

Component pages should link to flow pages, but should not duplicate the full flow narrative.

Use component pages for:

- what the component does;
- where it lives;
- what it consumes and produces;
- internal units;
- local development and operational context;
- component-specific runbooks and incident learnings.

Use flow pages for:

- end-to-end behaviour;
- ordering of steps;
- flow-level blast radius;
- upstream/downstream operational story;
- flow-level runbooks and failure modes.

### Relationship to dependency maps

Component pages should stay consistent with:

```text
_curated/maps/repo-dependency-map.json
_curated/maps/infra-dependency-map.json
_curated/maps/flow-component-map.json
```

Use each map for the right type of relationship:

| Map | Use for |
|---|---|
| `_curated/maps/repo-dependency-map.json` | Repo/component/job/API/event/table/data contract relationships |
| `_curated/maps/infra-dependency-map.json` | Infra package/template/resource relationships |
| `_curated/maps/flow-component-map.json` | Which components and infra resources participate in a flow |

If a component page says the component consumes or produces a contract, `repo-dependency-map.json` should reflect that.

If a component page says the component uses infrastructure resources, `infra-dependency-map.json` should reflect the resource relationship where appropriate.

If a component page says the component participates in a flow, `flow-component-map.json` should reflect that.

### Required filename format

Use a stable, readable slug:

```text
<component-name>.md
```

Place it under the relevant top-level monorepo group or component grouping:

```text
_curated/components/<group>/<component-name>.md
```

Examples:

```text
_curated/components/trade-processing/trade-loader.md
_curated/components/data-ingestion/source-consumer.md
_curated/components/warehouse-core/trade-core-loader.md
_curated/components/shared-libraries/pricing-utils.md
```

Do not include dates in curated filenames unless the date is part of the concept name. Dates belong in frontmatter and evidence, not the canonical file path.

### Required frontmatter

Each curated component page must use YAML frontmatter.

Required fields:

```yaml
type: atlas.component
title: ""
description: ""
resource: ""
tags: []
timestamp: YYYY-MM-DD
atlas_id: COMP-XXXX
status: curated
confidence: reviewed
last_reviewed: YYYY-MM-DD
reviewed_by: ""
source_staging_ids: []
component_name: ""
component_type: service | job | etl-job | kafka-consumer | kafka-producer | lambda | api | shared-library
  | infra-module | batch | other | unknown
component_scope: repo | submodule | deployable-unit | job-group | service | library | api | other | unknown
domain_group: ""
monorepo_path: ""
repository: ""
contains_internal_units: false
related_flows: []
related_components: []
related_repo_dependencies: []
related_infra_dependencies: []
related_runbooks: []
related_standards: []
related_incident_learnings: []
map_refs:
  repo_dependency_map: "_curated/maps/repo-dependency-map.json"
  infra_dependency_map: "_curated/maps/infra-dependency-map.json"
  flow_component_map: "_curated/maps/flow-component-map.json"
```

### Evidence expectations

Every material claim in a component page should have evidence or be marked as a coverage limit.

Evidence may include:

- staging entry;
- repo or monorepo path;
- source code path;
- config path;
- schema or contract path;
- build/dependency file;
- infra package/template path;
- flow page;
- runbook;
- incident learning;
- Jira/Confluence/SharePoint link;
- reviewer-confirmed statement.

### Status and confidence

A curated component page should normally use:

```yaml
status: curated
confidence: reviewed
```

If the page is being built but not fully confirmed, use:

```yaml
status: draft-curated
confidence: partial
```

and make coverage limits explicit.

### Claude instructions

When using a curated component page, Claude should:

1. read the component page before making component-level claims;
2. follow related flow links for end-to-end context;
3. inspect `repo-dependency-map.json` for structured repo/component/data/contract relationships;
4. inspect `infra-dependency-map.json` for infra/template/resource relationships;
5. inspect `flow-component-map.json` for flow participation;
6. inspect related runbooks, standards and incident learnings;
7. distinguish confirmed, possible and unknown relationships;
8. avoid saying "not affected" unless the page or maps explicitly support that claim;
9. prefer "no known dependency found" or "not covered" where evidence is incomplete.

### Reviewer checklist

Before approving a component page update, check:

- Is the component clearly identified?
- Is the monorepo path or repo location clear?
- Is the component type correct or explicitly unknown?
- Is the component granularity appropriate?
- Are internal units captured without over-splitting?
- Are responsibilities evidence-backed?
- Are consumes/produces relationships supported?
- Are related flows linked and evidence-backed?
- Are infra relationships separated from repo/component relationships?
- Are dependency-map updates consistent with the page?
- Are runbooks, standards and incident learnings relevant?
- Are unconfirmed claims clearly marked?
- Is the page useful to both humans and Claude?


---

# 6. `_curated/components/` page template

```yaml
type: atlas.component
title: ""
description: ""
resource: ""
tags: []
timestamp: YYYY-MM-DD
atlas_id: COMP-XXXX
status: curated
confidence: reviewed
last_reviewed: YYYY-MM-DD
reviewed_by: ""

source_staging_ids: []
component_name: ""
component_type: service | job | etl-job | kafka-consumer | kafka-producer | lambda | api | shared-library
  | infra-module | batch | other | unknown
component_scope: repo | submodule | deployable-unit | job-group | service | library | api | other | unknown
domain_group: ""
monorepo_path: ""
repository: ""
contains_internal_units: false

related_flows: []
related_components: []
related_repo_dependencies: []
related_infra_dependencies: []
related_runbooks: []
related_standards: []
related_incident_learnings: []
map_refs:
  repo_dependency_map: "_curated/maps/repo-dependency-map.json"
  infra_dependency_map: "_curated/maps/infra-dependency-map.json"
  flow_component_map: "_curated/maps/flow-component-map.json"
```

## Component: <component name>

### Summary

Briefly describe the component in plain language.

Example:

> `trade-loader` is a DataLens component in `trade-processing`
> that loads trade data, produces curated trade outputs and participates in the trade ingestion flow.

### Component context

Use this section to place the component in the Atlas hierarchy without introducing C4 naming into Atlas.

- Platform: DataLens
- Domain/group folder:
- Component:
- Component scope:
- Monorepo path:
- Repository/package:

### Responsibility

Describe what this component is reviewed and known to do.

### Location

- Domain/group folder:
- Repository:
- Monorepo path:
- Main README:
- Key source/config paths:

### Component type and scope

Choose the most accurate values.

```text
component_type: service | job | etl-job | kafka-consumer | kafka-producer | lambda | api
  | shared-library | infra-module | batch | other | unknown
component_scope: repo | submodule | deployable-unit | job-group | service | library | api | other | unknown
```

### Internal units

Use this section for Lambdas, Glue jobs, SQL files, handlers, scripts or other lower-level artefacts that belong inside this component.

Do not split these into separate component pages unless they are independently deployable, independently scheduled, independently operated, incident-relevant, flow-critical or reused across multiple components.

| Unit | Type | Purpose | Path | Evidence | Confidence |
|---|---|---|---|---|---|
| | lambda/glue-job/sql/handler/script/config/other | | | | |

### Participates in flows

Link to curated flow pages where available.

| Flow | Role in flow | Evidence |
|---|---|---|
| | | |

### Consumes

List confirmed inputs consumed by this component.

| Kind | Name | From | Relationship | Evidence |
|---|---|---|---|---|
| event/api/table/file/config/library/job-output | | | consumes_event / calls_api / reads_table / uses_library / depends_on_config | |

### Produces

List confirmed outputs produced by this component.

| Kind | Name | Used by | Relationship | Evidence |
|---|---|---|---|---|
| event/api/table/file/log/alert/job-output | | | produces_event / exposes_api / writes_table / publishes_file | |

### Repo/component dependencies

Summarise important component-level relationships from `_curated/maps/repo-dependency-map.json`.

| Relationship | Target/source | Evidence |
|---|---|---|
| | | |

### Infrastructure dependencies

Summarise important infra relationships. Detailed infra relationships belong in `_curated/maps/infra-dependency-map.json` and `_curated/infra/` pages.

| Infra package/resource | Relationship | Evidence |
|---|---|---|
| | | |

### Local development guidance

Prefer linking to the local README if exact commands may drift.

- Build:
- Test:
- Run locally:
- Local README:

### Operational notes

List reviewed operational notes, dashboards, alerts, failure modes or support concerns.

-

### Runbooks

List runbooks relevant to this component.

- `_curated/runbooks/...`

### Standards

List standards relevant to this component.

- `_curated/standards/...`

### Incident learnings

List incident learnings relevant to this component.

- `_curated/incidents/learnings/...`

### Evidence

List the key evidence used to curate this page.

- Staging entry:
- Repo path:
- README:
- Code path:
- Config path:
- Schema/contract path:
- Build/dependency file:
- Infra package/template:
- Flow page:
- Runbook:
- Incident learning:
- Jira/Confluence/SharePoint reference:
- Reviewer-confirmed statement:

### Possible relationships

Relationships that may be true but are not yet confirmed.

| Relationship | Why it is possible | Evidence gap |
|---|---|---|
| | | |

### Open questions / coverage limits

Be explicit about what Atlas does not yet know.

- Unknown consumers:
- Unknown producers:
- Unknown infra dependencies:
- Unverified contracts:
- Areas not covered by this page:

### Change history

| Date | Change | Source/review |
|---|---|---|
| YYYY-MM-DD | Initial curated page | |


---

# 7. `_curated/infra/README.md`

## _curated/infra/

### Purpose

`_curated/infra/` contains reviewed, trusted Atlas infrastructure pages.

An infra page explains what an infrastructure package or important shared infrastructure resource does, where it lives, which templates/configuration files define it,
which resources it creates or connects, which components and flows use it,
and what operational context matters.

A curated infra page should help answer:

> What infra package or resource is this, what does it create or configure,
> what depends on it, and what could be affected if it changes or fails?

### Trust rule

Files in `_curated/infra/` are trusted Atlas knowledge only after GitLab review and lead approval.

Do not copy raw staging notes into an infra page without filtering them into reviewed, evidence-backed statements.

If a statement is useful but not confirmed, keep it in one of these sections:

- `Possible relationships`
- `Open questions / coverage limits`
- `Unconfirmed resource relationships`

Do not present possible or unconfirmed infrastructure knowledge as fact.

### Recommended folder structure

Curated infra pages should normally mirror meaningful infra package folders from the infra repo.

Example:

```text
_curated/infra/
  index.md
  tradedata-api-monthly-flow.md
  tradedata-api-mcp.md
  tradedata-api-mcp-service.md
  94-lambda-generate-tiaa-token.md
  98-lambda-snaptrade-microbatch.md
  marketmind-knowledgebase.md
  marketmind-postgres-db.md
  clearwater-chartapi-application.md
  clearwater-s3-shared-artf.md
```

Do not create separate curated pages for every environment folder, script, YAML resource or individual cloud resource by default.

### Infra granularity rule

A curated infra page should usually represent one meaningful infra package/folder, especially where the folder contains files such as:

- `product.template.yaml`;
- `metadata.yaml`;
- `preconfig.sh`;
- `dev/`;
- `uat/`;
- `prod/`;
- `src/`.

Lower-level artefacts should usually be captured inside the parent infra page under:

- `Infra package structure`;
- `Environment notes`;
- `Internal resources`;
- `Resource relationships`.

Create a separate infra page for an internal resource only if it is:

- shared by multiple infra packages;
- used by multiple flows;
- operationally critical;
- independently operated or monitored;
- independently changed or deployed;
- attached to its own runbook;
- repeatedly incident-relevant;
- a major blast-radius node, such as a shared bucket, shared queue, shared IAM policy,
- shared database, shared cluster or shared networking layer.

### What belongs in an infra page

An infra page should include:

- infra package name;
- infra package path;
- service catalogue template path;
- metadata file path;
- environment folders;
- supporting scripts;
- internal resources;
- resource relationships;
- components using the resources;
- flows using the resources;
- parameters, exports and imports;
- schedules, triggers and events;
- permissions and roles;
- monitoring and operational relevance;
- related runbooks;
- related incident learnings;
- evidence links;
- coverage limits and open questions.

### What does not belong in an infra page

Do not use an infra page for:

- full application/component implementation notes;
- every line or resource in a large template;
- unreviewed raw template dumps;
- full service catalogue ownership metadata unless it is needed for engineering context;
- full incident records;
- every environment-specific detail unless it affects behaviour, risk or operation;
- unsupported blast-radius claims.

### Relationship to components

Infra pages should link to component pages when a component uses or depends on the infra package/resource.

Use component pages for:

- what the component does;
- component-local consumes/produces relationships;
- local development notes;
- component-specific operational context.

Use infra pages for:

- what the infra package creates or configures;
- template/resource relationships;
- environment variation;
- permissions, triggers, schedules and monitoring;
- infrastructure-level blast-radius context.

### Relationship to flows

Infra pages should list related flows where the infrastructure supports a flow.

Flow pages remain the operational story. Infra pages explain the supporting infrastructure.

### Relationship to dependency maps

`infra-dependency-map.json` has two main concepts:

- `packages`: meaningful infra packages/folders/service catalogue templates.
- `resources`: promoted resources that are important for impact analysis.

Infra pages should identify both:
- the package-level context;
- which internal resources, if any, should be promoted into the map-level `resources` index.

Infra pages should stay consistent with:

```text
_curated/maps/infra-dependency-map.json
_curated/maps/flow-component-map.json
_curated/maps/repo-dependency-map.json
```

Use each map for the right type of relationship:

| Map | Use for |
|---|---|
| `_curated/maps/infra-dependency-map.json` | Infra package/template/resource relationships |
| `_curated/maps/flow-component-map.json` | Which components and infra resources participate in a flow |
| `_curated/maps/repo-dependency-map.json` | Repo/component/job/API/event/table/data contract relationships |

If an infra page says a package creates or connects resources, `infra-dependency-map.json` should reflect that.

If an infra page says a resource supports a flow, `flow-component-map.json` should reflect that where useful.

Only update `repo-dependency-map.json` when the relationship is specifically a component using an infra output or when application-level dependency context is required.

### Required filename format

Use a stable, readable slug based on the infra package or shared resource name:

```text
<infra-package-or-resource>.md
```

Examples:

```text
tradedata-api-monthly-flow.md
tradedata-api-mcp-service.md
94-lambda-generate-tiaa-token.md
marketmind-knowledgebase.md
clearwater-s3-shared-artf.md
```

Do not include dates in curated filenames unless the date is part of the concept name. Dates belong in frontmatter and evidence, not the canonical file path.

### Required frontmatter

Each curated infra page must use YAML frontmatter.

Required fields:

```yaml
type: atlas.infra
title: ""
description: ""
resource: ""
tags: []
timestamp: YYYY-MM-DD
atlas_id: INFRA-XXXX
status: curated
confidence: reviewed
last_reviewed: YYYY-MM-DD
reviewed_by: ""
source_staging_ids: []
infra_package: ""
infra_package_path: ""
service_catalogue_template: ""
metadata_path: ""
preconfig_path: ""
environments: []
contains_internal_resources: true
resource_names: []
related_flows: []
related_components: []
related_infra_dependencies: []
related_runbooks: []
related_incident_learnings: []
coverage: unknown
defines_resources: []
promoted_resources: []
used_by_components: []
used_by_flows: []
depends_on_packages: []
depends_on_resources: []
map_refs:
  infra_dependency_map: "_curated/maps/infra-dependency-map.json"
  flow_component_map: "_curated/maps/flow-component-map.json"
  repo_dependency_map: "_curated/maps/repo-dependency-map.json"
```

### Evidence expectations

Every material claim in an infra page should have evidence or be marked as a coverage limit.

Evidence may include:

- staging entry;
- infra package path;
- `product.template.yaml`;
- `metadata.yaml`;
- environment folder;
- supporting script;
- resource definition;
- parameter/export/import;
- schedule/trigger;
- IAM/permission reference;
- component page;
- flow page;
- runbook;
- incident learning;
- Jira/Confluence/SharePoint link;
- reviewer-confirmed statement.

### Status and confidence

A curated infra page should normally use:

```yaml
status: curated
confidence: reviewed
```

If the page is being built but not fully confirmed, use:

```yaml
status: draft-curated
confidence: partial
```

and make coverage limits explicit.

### Claude instructions

When using a curated infra page, Claude should:

1. read the infra page before making infrastructure-level claims;
2. distinguish infra package, internal resources, environment config and scripts;
3. inspect `infra-dependency-map.json` for structured resource relationships;
4. inspect `flow-component-map.json` for flow participation;
5. inspect component pages for component-level usage;
6. inspect runbooks and incident learnings for operational context;
7. distinguish confirmed, possible and unknown relationships;
8. avoid saying "not affected" unless the page or maps explicitly support that claim;
9. prefer "no known dependency found" or "not covered" where evidence is incomplete.

#### Resource promotion rule

Not every infrastructure resource belongs in the top-level `resources` index of `_curated/maps/infra-dependency-map.json`.

Promote a resource into the map-level `resources` index only when it is shared, data-bearing, data-routing, orchestration-critical, security-sensitive, deletion-sensitive, incident-relevant, monitored, used by multiple components/flows/packages, or likely to be searched directly during impact analysis or incident triage.

Resources that are only internal implementation details of one infra package should remain inside the parent infra page under `Internal resources`.

### Reviewer checklist

Before approving an infra page update, check:

- Is the infra package or resource clearly identified?
- Is the infra package path correct?
- Is the service catalogue template path clear?
- Are environment folders and supporting files represented accurately?
- Are internal resources captured without over-splitting?
- Are resource relationships evidence-backed?
- Are component-to-resource relationships supported?
- Are flow-to-resource relationships supported?
- Are permissions, triggers, schedules and monitoring relationships separated clearly?
- Are dependency-map updates consistent with the page?
- Are unconfirmed claims clearly marked?
- Is the page useful to both humans and Claude?


---

# 8. `_curated/infra/` page template

```yaml
type: atlas.infra
title: ""
description: ""
resource: ""
tags: []
timestamp: YYYY-MM-DD
atlas_id: INFRA-XXXX
status: curated
confidence: reviewed
last_reviewed: YYYY-MM-DD
reviewed_by: ""

source_staging_ids: []
infra_package: ""
infra_package_path: ""
service_catalogue_template: ""
metadata_path: ""
preconfig_path: ""
environments:
  - dev
  - uat
  - prod
contains_internal_resources: true
resource_names: []

related_flows: []
related_components: []
related_infra_dependencies: []
related_runbooks: []
related_incident_learnings: []
coverage: unknown
defines_resources: []
promoted_resources: []
used_by_components: []
used_by_flows: []
depends_on_packages: []
depends_on_resources: []

map_refs:
  infra_dependency_map: "_curated/maps/infra-dependency-map.json"
  flow_component_map: "_curated/maps/flow-component-map.json"
  repo_dependency_map: "_curated/maps/repo-dependency-map.json"
```

## Infra: <infra package or resource name>

### Summary

Briefly describe the infra package or resource in plain language.

Example:

> `tradedata-api-monthly-flow` is an infra package that defines service
> catalogue template infrastructure and environment configuration used
> by the monthly trade data API flow.

### Purpose

[Note: a short stretch of the template between "## Purpose" and "## Infra package structure" wasn't captured in the photos — there may be a section here, e.g. package location fields, that isn't reflected below.]

### Infra package structure

Capture the package layout. Do not list every file unless it matters to engineering context.

| Path | Type | Purpose | Evidence |
|---|---|---|---|
| metadata.yaml | metadata | | |
| product.template.yaml | service-catalogue-template | | |
| preconfig.sh | script | | |
| dev/ | environment-config | | |
| uat/ | environment-config | | |
| prod/ | environment-config | | |
| src/ | source | | |

### Environment notes

Capture reviewed environment differences only where they affect behaviour, operation, deployment or risk.

| Environment | Path | Difference or note | Evidence |
|---|---|---|---|
| dev | | | |
| uat | | | |
| prod | | | |

### Internal resources

Use this section for resources defined inside the package.

Do not split these into separate infra pages unless they are shared, independently operated, incident-relevant, flow-critical or reused across multiple components.

| Resource name/logical ID | Resource type | Defined in | Purpose | Promote to map resources? | Reason | Evidence |
|---|---|---|---|---|---|---|
| | lambda/queue/topic/bucket/database/role/policy/scheduler/alarm/ecs/other | | | | | |

### Resource relationships

List reviewed relationships between resources.

| From resource | Relationship | To resource | Evidence |
|---|---|---|---|
| | depends_on_resource / triggers / reads_from / writes_to / exports_value<br/>/ imports_value / permission_allows / alarms_on | | |

### Components using these resources

List confirmed components that use or depend on these resources.

| Component | Resource | Relationship | Evidence |
|---|---|---|---|
| | | uses_resource / reads_from / writes_to / triggered_by / scheduled_by | |

### Flows using these resources

List confirmed flows that rely on these resources.

| Flow | Resource | Role in flow | Evidence |
|---|---|---|---|
| | | | |

### Parameters, exports and imports

List reviewed parameters, exports, imports or shared values.

| Name | Kind | Producer | Consumer | Evidence |
|---|---|---|---|---|
| | parameter/export/import | | | |

### Schedules, triggers and events

List reviewed scheduled or event-based triggers.

| Trigger | Target | Schedule/event | Evidence |
|---|---|---|---|
| | | | |

### Permissions and roles

List reviewed permissions, roles or access relationships.

| Role/permission | Allows | Used by | Evidence |
|---|---|---|---|
| | | | |

### Monitoring and operational relevance

List reviewed alarms, dashboards, logs, monitors or operational notes.

-

### Related runbooks

List runbooks relevant to this infra package/resource.

- `_curated/runbooks/...`

### Incident learnings

List incident learnings relevant to this infra package/resource.

- `_curated/incidents/learnings/...`

### Evidence

List the key evidence used to curate this page.

- Staging entry:
- Infra package path:
- Service catalogue template:
- Metadata file:
- Environment folder:
- Script:
- Resource definition:
- Parameter/export/import:
- Schedule/trigger:
- IAM/permission reference:
- Component page:
- Flow page:
- Runbook:
- Incident learning:
- Jira/Confluence/SharePoint reference:
- Reviewer-confirmed statement:

### Possible relationships

Relationships that may be true but are not yet confirmed.

| Relationship | Why it is possible | Evidence gap |
|---|---|---|
| | | |

#### Impact if deleted or changed

Use this section for package-level or promoted-resource blast-radius notes.

| Item | Change/delete scenario | Known impact | Possible impact | Unknowns | Evidence |
|---|---|---|---|---|---|
| | | | | | |

### Open questions / coverage limits

Be explicit about what Atlas does not yet know.

- Unknown resources:
- Unknown component users:
- Unknown flow usage:
- Unknown permissions:
- Unknown environment differences:
- Areas not covered by this page:

### Change history

| Date | Change | Source/review |
|---|---|---|
| YYYY-MM-DD | Initial curated page | |


---

# Part 3 — Dependency maps

# 9. `_curated/maps/README.md` — Curated Maps

## Purpose

`_curated/maps/` contains machine-readable dependency maps that provide structured routing and impact-analysis data for Atlas.

Maps connect concepts. Pages explain them. Lint checks consistency between the two.

## Available maps

| Map | Purpose | Primary key | Documentation |
|---|---|---|---|
| [flow-component-map.json](...) | Flow → component participation and routing | Flow ID | [README](...) |
| [repo-dependency-map.json](...) | Component → component, API, event, table, data relationships | Component key | [README](...) |
| [infra-dependency-map.json](...) | Infra package → resource, component/flow usage, impact | Package key | [README](...) |

## Which map to use

| Question | Start with |
|---|---|
| "Which components participate in flow X?" | `flow-component-map.json` |
| "What does component Y consume/produce?" | `repo-dependency-map.json` |
| "What infra resources support flow X?" | `infra-dependency-map.json` |
| "What would break if infra resource Z changes?" | `infra-dependency-map.json` |
| "What downstream consumers depend on component Y?" | `repo-dependency-map.json` |
| "Which flows are affected if component Y fails?" | `flow-component-map.json` |

## Navigation guidance

### For engineers

- Maps are JSON for tooling and AI consumption — read the per-map README for schema and usage.
- Maps are kept consistent with curated pages via the lint process.
- Maps are updated alongside curated page changes in the same MR.

### For AI agents

1. Use maps for routing queries, not for narrative answers.
2. Follow map references to curated pages for explanation.
3. Maps declare relationships; pages provide evidence and context.
4. Distinguish confirmed, possible, and unknown relationships in map entries.

## Consistency rules

- If a flow page names a component participant → `flow-component-map.json` should reflect it.
- If a component page declares consumes/produces → `repo-dependency-map.json` should reflect it.
- If an infra page declares resource relationships → `infra-dependency-map.json` should reflect it.
- Atlas lint checks this consistency.

## Do not

- Do not create a single `dependency-map.json` combining all three.
- Do not put detailed infra resource relationships into `flow-component-map.json`.
- Do not put flow narrative into maps — that belongs in pages.


---

# 10. `flow-component-map.json` — partial capture

> **Incomplete.** Only the `metadata` block and the opening of the first flow entry
> were legible in the source captures. The remaining entry points, steps, outputs
> and further flows are not recorded here.

```jsonc
{
  "metadata": {
    "version": "1.0",
    "last_updated": "2026-07-31",
    "description": "Reduced flow-to-component routing map for DataLens flows, ordered...",
    "map_type": "flow-component-routing-map",
    "source_of_truth": [
      "_curated/flows/**/*.md",
      "_curated/components/**/*.md"
    ],
    "related_maps": {
      "repo_dependency_map": "_curated/maps/repo-dependency-map.json",
      "infra_dependency_map": "_curated/maps/infra-dependency-map.json"
    },
    "relationship_types": [
      "uses_component",
      "starts_with",
      "produces_output",
      "feeds_flow",
      "depends_on_flow",
      "runs_before_flow",
      "runs_after_flow",
      "has_runbook",
      "has_incident_learning"
    ],
    "entry_point_kinds": [
      "event",
      "schedule",
      "file",
      "api",
      "manual",
      "other"
    ],
    "output_kinds": [
      "table",
      "file",
      "event",
      "api",
      "report",
      "other"
    ],
    "confidence_values": [
      "reviewed",
      "possible",
      "unconfirmed",
      "conflicting-evidence"
    ],
    "coverage_values": [
      "none",
      "partial",
      "good",
      "stale",
      "unknown"
    ],
    "maintenance_rule": "Flow pages explain the operational story. Component pages explain co[...text cut off in photo...]"
  },
  "flows": {
    "sds-reference-data-pipeline": {
      "flow_page": "_curated/flows/sds-reference-data-pipeline.md",
      "flow_name": "SDS Reference Data Pipeline",
      "purpose": "Extracts 85 SDS reference data entities from the Barclays SDS REST API, load[...text cut off in photo...]",
      "coverage": "partial",
      "entry_points": [
        {
          "kind": "schedule",
          "name": "SDSEventRuleScheduler (cron 0 18 * * ? *)",
          "evidence": [
            "_curated/flows/sds-reference-data-pipeline.md",
            "_curated/infra/130-lambda-sds-generic-client.md"
          ],
          "confidence": "reviewed"
        },
        {
          "kind": "schedule",
          "name": "SDSCounterPartyEntityScheduleRule (cron 35 1 * * ? *)"
          /* --- capture ends here; remaining fields of this entry_point,
             any further entry_points, and the rest of the "flows" object
             were not visible in the photos provided --- */
```


---

# 11. `repo_dependency_map_README.md`

# `repo-dependency-map.json`

## Purpose

`repo-dependency-map.json` is the component-level dependency map for DataLens code, data, API, event, schema, file, job and shared-library relationships.

It is intended to answer questions such as:

- What does this component consume?
- What does this component produce?
- Which components use this output?
- Which shared libraries does this component depend on?
- What evidence supports the relationship?
- Is the relationship reviewed, possible or unconfirmed?

This map is not a replacement for component pages or flow pages.

Use this rule:

```text
Markdown pages explain.
JSON maps connect.
Lint checks consistency.
```

## Source of truth model

For Atlas V1, `repo-dependency-map.json` is component-centric.

That means the top-level map is organised by component key:

```text
<domain-group>/<component-name>
```

Example:

```text
trade-processing/trade-loader
warehouse-core/trade-core-loader
shared-libraries/pricing-utils
```

This mirrors the curated component folder structure:

```text
_curated/components/<domain-group>/<component-name>.md
```

## Why component-centric for V1?

The component-centric model is chosen because it is:

- easy for humans to read;
- easy to search with Ctrl+F;
- aligned with `_curated/components/`;
- useful when Claude starts from a local repo path;
- simple enough to maintain manually in early Atlas;
- flexible enough to include events, APIs, tables, files, jobs, libraries and config dependencies.

A relationship-centric or generated graph view can be added later if reverse impact queries become painful.

## What belongs in this map

Use this map for repo/component-level relationships such as:

- event production and consumption;
- HTTP/API calls and exposed APIs;
- table reads and writes;
- file publishing and consumption;
- shared-library usage;
- schema-library usage;
- job output dependencies;
- component-to-component dependencies;
- config dependencies;
- job ordering where it is component-level.

## What does not belong in this map

Do not use this map for raw infrastructure resource relationships.

Infra package, template and resource relationships belong in:

```text
_curated/maps/infra-dependency-map.json
```

Flow membership belongs primarily in:

```text
_curated/maps/flow-component-map.json
```

A component-to-infra relationship may be referenced here only when it is specifically about a component depending on an infra output or resource. The infra resource relationship itself should remain in `infra-dependency-map.json`.

## Required top-level structure

```json
{
  "metadata": {},
  "components": {}
}
```

## Metadata fields

```json
{
  "version": "1.0",
  "last_updated": "2026-07-31",
  "description": "Component-level dependency map for DataLens code, data, API, event, schema, file, job and shared-library relationships",
  "map_type": "component-centric-source-map",
  "source_of_truth": [
    "_curated/components/**/*.md",
    "_curated/flows/**/*.md"
  ],
  "related_maps": {
    "infra_dependency_map": "_curated/maps/infra-dependency-map.json",
    "flow_component_map": "_curated/maps/flow-component-map.json"
  },
  "relationship_types": [],
  "relationship_kinds": [],
  "confidence_values": [],
  "coverage_values": [],
  "maintenance_rule": "Markdown pages explain. JSON maps connect. Lint checks consistency. Do not manually maintain multiple source-of-truth maps for the same relationship."
}
```

## Component entry shape

Each component should use this shape:

```json
{
  "component_page": "_curated/components/<domain-group>/<component-name>.md",
  "domain_group": "",
  "component_type": "unknown",
  "component_scope": "unknown",
  "monorepo_path": "",
  "coverage": "unknown",
  "consumes": [],
  "produces": [],
  "uses_libraries": [],
  "depends_on_components": [],
  "used_by_components": [],
  "possible_relationships": [],
  "open_questions": []
}
```

Example populated entry:

```json
"components": {
  "sds/dl-lambda-sds-generic-client": {
    "component_page": "_curated/components/sds/dl-lambda-sds-generic-client.md",
    "domain_group": "sds",
    "component_type": "lambda",
    "component_scope": "deployable-unit",
    "monorepo_path": "datalens/sds/libs/dl-lambda-sds-generic-client",
    "coverage": "partial",
    "consumes": []
  }
}
```

## Relationship object shape

Use this common shape inside `consumes`, `produces`, `uses_libraries`, `depends_on_components` and `used_by_components` where applicable:

```json
{
  "kind": "event | api | table | file | shared-library | schema-library | component | config | job-output | other",
  "name": "",
  "relationship": "",
  "from": "",
  "to": "",
  "used_by": [],
  "evidence": [],
  "confidence": "reviewed | possible | unconfirmed",
  "notes": ""
}
```

Use only the fields that make sense for that relationship.

## Recommended relationship types

Use these values where possible:

```text
consumes_event
produces_event
calls_api
exposes_api
reads_table
writes_table
consumes_file
publishes_file
uses_shared_library
uses_schema_library
depends_on_component
used_by_component
runs_before
runs_after
depends_on_config
consumes_job_output
produces_job_output
```

Avoid vague relationship names such as:

```text
event
api
data
uses
related
```

They do not encode direction or impact clearly enough.

## Confidence values

Use:

```text
reviewed
possible
unconfirmed
conflicting-evidence
```

`reviewed` means the relationship is supported by curated evidence.

`possible` means Atlas has a plausible relationship but it is not confirmed.

`unconfirmed` means a human or additional evidence is needed.

`conflicting-evidence` means Atlas has evidence that does not agree.

## Coverage values

Use:

```text
none
partial
good
stale
unknown
```

Coverage describes how complete Atlas believes the dependency knowledge is for a component.

Do not use coverage to imply safety. A component with `good` coverage can still have undocumented dependencies.

## Evidence rules

Every reviewed relationship should include evidence.

Evidence may point to:

- a curated component page;
- a curated flow page;
- a staging entry;
- a source code path;
- a schema path;
- a build/dependency file;
- a runbook;
- an incident learning;
- a reviewer-confirmed statement.

Example:

```json
"evidence": [
  "_curated/components/trade-processing/trade-loader.md",
  "_staging/changes/2026-07-30-change-trade-status-schema.md"
]
```

## Shared-library impact

Shared-library relationships may be recorded in `uses_libraries`.

Do not turn the main repo dependency map into a shared-library impact report.

If Atlas later needs a specialised library blast-radius view, generate or maintain a separate derived file such as:

```text
_curated/maps/derived/shared-library-impact-map.json
```

That derived file should reference `repo-dependency-map.json` as its source map.

## Lint expectations

A linter should check:

- JSON is valid;
- every component key has a matching component page where expected;
- relationship types use the approved vocabulary;
- evidence paths resolve or are marked external;
- confidence values are allowed;
- coverage values are allowed;
- component page consumes/produces sections do not contradict the map;
- flow-component-map entries do not contradict component flow references;
- infra relationships are not incorrectly stored as repo relationships.

## Maintenance rule

Do not manually maintain multiple source-of-truth maps for the same relationship.

For V1:

```text
repo-dependency-map.json = component-centric source map
```

Later, if needed:

```text
relationship index = generated from repo-dependency-map.json
shared-library impact map = generated or specialised view from repo-dependency-map.json
```

## Human usage

It is acceptable for engineers to use Ctrl+F to find a component, event, API, table, file or library name.

If reverse lookup becomes painful, generate a derived reverse index rather than redesigning the source map too early.


---

# 12. `infra_dependency_map_README.md`

# `infra-dependency-map.json`

## Purpose

`infra-dependency-map.json` is the infrastructure dependency map for DataLens infra packages, service catalogue templates, AWS resources and usage relationships.

It is intended to answer impact questions such as:

- What uses this shared resource?
- What components or flows might be affected if this resource is deleted?
- What happens if this infra package/product is removed?
- Which package defines a resource?
- Which resources are shared, data-bearing, orchestration-critical, security-sensitive or incident-relevant?
- What evidence supports each relationship?

This map is not a replacement for infra pages, component pages or flow pages.

Use this rule:

```text
Markdown pages explain.
JSON maps connect.
Lint checks consistency.
```

## Source of truth model

For Atlas V1, `infra-dependency-map.json` is package-centric with a selective resource index.

That means the map has two main sections:

```json
{
  "metadata": {},
  "packages": {},
  "resources": {}
}
```

Use:

- `packages` for meaningful infra products, packages, folders or service catalogue templates.
- `resources` only for promoted resources that are important for impact analysis.

## Why package-centric plus resource index?

Your infra repo is mostly organised around infra packages and service catalogue templates. That means package-level modelling is the natural starting point.

However, the main impact question is often resource-level:

> What uses this shared bucket, queue, IAM role, table, database, topic,
> scheduler or data lake artefact?

So Atlas needs both:

```text
package -> resources -> components/flows
resource -> packages/components/flows
```

## What belongs in `packages`

Add an entry under `packages` for meaningful infra packages/folders, especially where the folder contains files such as:

- `product.template.yaml`;
- `metadata.yaml`;
- `preconfig.sh`;
- `dev/`;
- `uat/`;
- `prod/`;
- `src/`.

A package entry should describe:

- infra page;
- package path;
- service catalogue template;
- metadata file;
- environments;
- resources defined by the package;
- components using the package;
- flows using the package;
- evidence;
- confidence;
- coverage.

## What belongs in `resources`

Not every infrastructure resource belongs in the top-level `resources` index.

Promote a resource into `resources` only when it is important for impact analysis.

A resource should be promoted if it is any of the following:

- shared across more than one package, component or flow;
- data-bearing or data-routing;
- orchestration-critical;
- security-sensitive;
- deletion-sensitive;
- incident-relevant;
- monitored or operationally important;
- used by multiple components, flows or infra packages;
- likely to be searched directly during impact analysis or incident triage.

## Data engineering promotion examples

For a DataLens-style AWS data engineering platform, promote resources such as:

- S3 data lake buckets or important prefixes;
- Glue databases, tables, jobs, crawlers, workflows or triggers;
- Redshift databases, schemas, tables, views or clusters;
- Athena databases or tables;
- DynamoDB tables used by pipelines;
- SQS queues carrying pipeline data;
- SNS topics or EventBridge buses/rules used for orchestration;
- Step Functions or workflow orchestrators;
- Scheduler resources that trigger ETL or pipeline products;
- shared IAM roles, IAM policies or cross-account roles;
- KMS keys, Secrets Manager secrets or SSM parameters used by multiple jobs;
- Lake Formation permissions or shared data access controls;
- CloudWatch alarms, dashboards or operational monitors tied to important flows.

## What should stay inside an infra page only

Do not promote every low-level resource into the top-level `resources` index.

Keep these inside the parent infra page unless they meet the promotion rule:

- every Lambda logical ID;
- every environment config file;
- every minor IAM statement;
- every generated CloudWatch log group;
- every helper script;
- every internal-only resource used by one package with no wider blast-radius concern.

## Required top-level structure

```json
{
  "metadata": {},
  "packages": {},
  "resources": {}
}
```

## Package entry shape

Each package should use this shape:

```json
{
  "infra_page": "_curated/infra/<package-name>.md",
  "infra_package_path": "",
  "service_catalogue_template": "",
  "metadata_path": "",
  "environments": [],
  "defines_resources": [],
  "used_by_components": [],
  "used_by_flows": [],
  "depends_on_packages": [],
  "depends_on_resources": [],
  "evidence": [],
  "confidence": "reviewed | possible | unconfirmed",
  "coverage": "none | partial | good | stale | unknown",
  "open_questions": []
}
```

## Resource entry shape

Each promoted resource should use this shape:

```json
{
  "resource_name": "",
  "resource_type": "",
  "defined_in_package": "",
  "defined_in_path": "",
  "environments": [],
  "used_by_components": [],
  "used_by_flows": [],
  "used_by_packages": [],
  "depends_on_resources": [],
  "permissions_or_access": [],
  "monitoring": [],
  "impact_if_deleted": {
    "known_impact": [],
    "possible_impact": [],
    "unknowns": []
  },
  "evidence": [],
  "confidence": "reviewed | possible | unconfirmed",
  "coverage": "none | partial | good | stale | unknown",
  "open_questions": []
}
```

## Recommended resource types

Use these values where possible:

```text
s3-bucket
s3-prefix
glue-database
glue-table
glue-job
glue-crawler
glue-workflow
glue-trigger
redshift-cluster
redshift-database
redshift-schema
redshift-table
redshift-view
athena-database
athena-table
dynamodb-table
sqs-queue
sns-topic
eventbridge-rule
eventbridge-bus
step-function
lambda
iam-role
iam-policy
kms-key
secret
ssm-parameter
lake-formation-permission
security-group
cloudwatch-alarm
dashboard
service-catalogue-template
other
```

## Recommended relationship types

Use these values where possible:

```text
defines_resource
uses_resource
depends_on_resource
depends_on_package
exports_value
imports_value
triggers
scheduled_by
reads_from
writes_to
permission_allows
monitored_by
deployed_to_environment
uses_secret
uses_kms_key
uses_iam_role
uses_data_catalog
uses_data_lake_location
```

Avoid vague relationship names such as:

```text
uses
related
connected_to
resource
```

They do not encode direction or impact clearly enough.

## Confidence values

Use:

```text
reviewed
possible
unconfirmed
conflicting-evidence
```

`reviewed` means the relationship is supported by curated evidence.

`possible` means Atlas has a plausible relationship but it is not confirmed.

`unconfirmed` means a human or additional evidence is needed.

`conflicting-evidence` means Atlas has evidence that does not agree.

## Coverage values

Use:

```text
none
partial
good
stale
unknown
```

Coverage describes how complete Atlas believes the infra knowledge is for a package or resource.

Do not use coverage to imply safety. A resource with `good` coverage can still have undocumented external/manual consumers.

## Evidence rules

Every reviewed package or resource relationship should include evidence.

Evidence may point to:

- a curated infra page;
- a curated component page;
- a curated flow page;
- a staging entry;
- `product.template.yaml`;
- `metadata.yaml`;
- environment folders;
- source/config paths;
- runbooks;
- incident learnings;
- a reviewer-confirmed statement.

Example:

```json
"evidence": [
  "_curated/infra/tradedata-api-monthly-flow.md",
  "tradedata-api-monthly-flow/product.template.yaml"
]
```

## Impact language

Impact analysis should return:

```text
known affected
possibly affected
unknown / not covered
relevant evidence
reviewer questions
```

Avoid saying:

```text
not affected
```

unless Atlas explicitly proves that claim.

## Lint expectations

A linter should check:

- JSON is valid;
- every package key has a matching infra page where expected;
- resource types use the approved vocabulary;
- relationship types use the approved vocabulary;
- evidence paths resolve or are marked external;
- confidence values are allowed;
- coverage values are allowed;
- infra page content does not contradict the map;
- promoted resources include a promotion reason;
- repo/component relationships are not incorrectly stored as infra relationships.

## Maintenance rule

Do not manually maintain multiple source-of-truth maps for the same relationship.

For V1:

```text
infra-dependency-map.json = package-centric source map with selective promoted resources
```

Do not manually maintain a separate resource graph as a second source of truth.

If reverse lookup or specialised views become necessary, generate derived files from this map.

Possible future derived views:

```text
_curated/maps/derived/shared-resource-impact-map.json
_curated/maps/derived/data-platform-resource-index.json
_curated/maps/derived/security-sensitive-resource-index.json
```

## Human usage

It is acceptable for engineers to use Ctrl+F to find package names, resource names, buckets, queues, tables, roles, schemas or topics.

If reverse lookup becomes painful, generate a derived reverse index rather than redesigning the source map too early.

## Example metadata block

```json
{
  "metadata": {
    "version": "1.0",
    "last_updated": "2026-07-31",
    "description": "Infrastructure dependency map for DataLens infra packages, service catalogue templates, AWS resources and usage relationships",
    "map_type": "package-centric-source-map-with-selective-resource-index",
    "source_of_truth": [
      "_curated/infra/**/*.md",
      "_curated/components/**/*.md",
      "_curated/flows/**/*.md"
    ],
    "related_maps": {
      "repo_dependency_map": "_curated/maps/repo-dependency-map.json",
      "flow_component_map": "_curated/maps/flow-component-map.json"
    },
    "resource_promotion_rule": "Promote a resource into resources only when it is shared, data-bearing, data-routing, orchestration-critical, security-sensitive, deletion-sensitive, incident-relevant or monitored",
    "relationship_types": [],
    "resource_types": [],
    "confidence_values": [],
    "coverage_values": [],
    "maintenance_rule": "Markdown pages explain. JSON maps connect. Lint checks consistency."
  },
  "packages": {},
  "resources": {}
}
```

### Example package entry

```json
"packages": {
  "130-lambda-sds-generic-client": {
    "infra_page": "_curated/infra/130-lambda-sds-generic-client.md",
    "infra_package_path": "aws-infra-core-product/130-lambda-sds-generic-client",
    "service_catalogue_template": "aws-infra-core-product/130-lambda-sds-generic-client/product.template.yaml",
    "metadata_path": null,
    "environments": ["dev", "uat", "prod"],
    "defines_resources": [
      "resource:dl-lambda-sds-generic-client",
      "resource:dl-lambda-sds-scheduler",
      "resource:dl-lambda-sds-api-trigger",
      "resource:dl-lambda-sds-job-audit-query",
      "resource:dl-sf-sm-tradesmart-sds-api-p-job",
      "resource:dl-glu-tradesmart-sds-api-p-job",
      "resource:dl-glu-sds-extract-redshift-to-s3-p-job",
      "resource:dl-cat-tradesmart-referencestore",
      "resource:sds-api-consumer-ecs-task",
      "resource:SDSEventRuleScheduler",
      "resource:SDSCounterPartyEntityScheduleRule",
      "resource:SDSClientAccountEntityScheduleRule",
      "resource:SDSRegionScheduleRule"
    ],
    "used_by_components": [
      "sds/dl-lambda-sds-generic-client"
    ]
  }
}
```

### Example promoted resource entry

```json
"resources": {
  "resource:dl-sf-sm-tradesmart-sds-api-p-job": {
    "resource_name": "dl-sf-sm-tradesmart-sds-api-p-job",
    "resource_type": "step-function",
    "defined_in_package": "130-lambda-sds-generic-client",
    "defined_in_path": "aws-infra-core-product/130-lambda-sds-generic-client/product.template.yaml",
    "environments": ["dev", "uat", "prod"],
    "used_by_components": ["sds/dl-lambda-sds-generic-client"],
    "used_by_flows": ["sds-reference-data-pipeline"],
    "used_by_packages": [],
    "depends_on_resources": [
      "resource:dl-lambda-sds-generic-client",
      "resource:sds-api-consumer-ecs-task",
      "resource:dl-glu-tradesmart-sds-api-p-job",
      "resource:dl-glu-sds-extract-redshift-to-s3-p-job"
    ],
    "permissions_or_access": [
      {
        "role": "DataLensLambdaETLIamRole",
        "allows": "states:StartExecution"
      }
    ]
  }
}
```


---

# Part 4 — Operational status

# 13. `_curated/status/curation-status.md`

# Curation Status

Routine curation run tracking for Atlas. Updated after each linked curation proposal.

## Status table

| Area | Last curation run | Last staging item considered | Last proposed change | Coverage status | Notes |
|---|---|---|---|---|---|
| components | 2026-07-31 | STG-20260730-dl-lambda-sds-generic-client | Hackathon-Atlas branch | partial | First real component page: sds/dl-lambda-sds-generic-client |
| flows | 2026-07-31 | STG-20260730-sds-reference-data-pipeline | Hackathon-Atlas branch | partial | First real flow page: sds-reference-data-pipeline |
| infra | 2026-07-31 | STG-20260730-infra-130-lambda-sds-generic-client | Hackathon-Atlas branch | partial | First real infra page: 130-lambda-sds-generic-client |

## Run history

### 2026-07-31 — SDS Reference Data Pipeline linked curation

- **Staging items**: 3 (flow, component, infra)
- **Decision**: All three paths applied (APPLY)
- **Output**: 3 curated pages + 3 map updates
- **Coverage**: Partial — open questions remain about downstream consumers, monitoring, Glue script locations, deployment pipelines
- **Reviewer status**: Pending human review


---

# Part 5 — Staging layer

# 14. `_staging/README.md`

# `_staging/`

## Purpose

`_staging/` is the raw evidence layer for DataLens Atlas.

It captures useful engineering knowledge before it becomes trusted Atlas knowledge. The purpose is not to create polished documentation. The purpose is to preserve evidence, context, uncertainty and reviewer questions so Claude and humans can decide whether `_curated/` needs to change.

`_staging/` represents:

> What we found, who supplied it, where it came from, and what it might affect.

`_curated/` represents:

> What Atlas currently trusts after review and approval.

## Core rule

Staging is not trusted.

A file in `_staging/` can be used as evidence for a curated update, but it does not become source-of-truth Atlas knowledge until a related `_curated/` change is reviewed and approved through GitLab.

## Folder structure

```text
_staging/
  README.md
  changes/
    README.md
    template.md
  flows/
    README.md
    template.md
  components/
    README.md
    template.md
  infra/
    README.md
    template.md
  incidents/
    README.md
    template.md
  runbooks/
    README.md
    template.md
  standards/
    README.md
    template.md
  archive/
    README.md
```

## Folder usage

| Folder | Use when the raw knowledge is about |
|---|---|
| `_staging/changes/` | A logical change, MR, release bundle, code change or Claude-discovered local repo context |
| `_staging/flows/` | An end-to-end DataLens flow or pipeline across multiple components |
| `_staging/components/` | A repo, component, service, job, API, Lambda, library or operationally meaningful implementation unit |
| `_staging/infra/` | Infra packages, service catalogue templates, resources, deployment config, environment folders and infrastructure behaviour |
| `_staging/incidents/` | Real incidents, mock incidents, near misses and operational learnings |
| `_staging/runbooks/` | Draft or updated operational procedures |
| `_staging/standards/` | Reusable engineering standards, conventions or guidance |
| `_staging/archive/` | Old raw entries retained for history but no longer active |

## Naming convention

Use readable, dated file names.

```text
YYYY-MM-DD-<type>-<short-topic>.md
```

Examples:

```text
2026-07-30-change-trade-status-schema.md
2026-07-30-flow-trade-ingestion-to-warehouse.md
2026-07-30-component-trade-loader.md
2026-07-30-infra-tradedata-api-monthly-flow.md
2026-07-30-incident-mock-stale-trade-data.md
2026-07-30-runbook-kafka-lag-investigation.md
2026-07-30-standard-event-contract-change.md
```

## Required metadata convention

Every staging file must use YAML frontmatter.

Atlas uses an OKF-inspired style: Markdown files with structured YAML frontmatter, human-readable body sections and links between concepts.

Minimum required fields:

```yaml
type: atlas.staging.<bucket>
title: ""
description: ""
resource: ""
tags: []
timestamp: YYYY-MM-DD
atlas_id: STG-YYYY-NNNN
status: new
confidence: raw-unreviewed
source_type: ""
source_link: ""
intended_curated_targets: []
```

Allowed staging `type` values:

```text
atlas.staging.change
atlas.staging.flow
atlas.staging.component
atlas.staging.infra
atlas.staging.incident
atlas.staging.runbook
atlas.staging.standard
```

## Status values

Use one of:

```text
new
awaiting-evidence
ready-for-curation
curation-proposed
curated
rejected
archived
```

## Confidence values

Use one of:

```text
raw-unreviewed
developer-supplied
possible
unconfirmed
conflicting-evidence
reviewed
```

`reviewed` should normally only appear in `_curated/`, not in new staging entries.

## Evidence expectations

Every staging entry should include evidence or say what evidence is missing.

Useful evidence may include:

- MR or commit reference;
- repo path;
- monorepo path;
- source code path;
- config path;
- schema or contract path;
- infra template path;
- runbook link;
- incident or Jira reference;
- Confluence or SharePoint link;
- Teams/email summary where appropriate;
- engineer-supplied statement clearly marked as such.

## What not to put in staging

Do not stage:

- secrets, credentials, tokens or keys;
- unnecessary production-sensitive data;
- unnecessary personal data;
- raw logs containing sensitive information;
- full major incident records unless explicitly allowed;
- unsupported claims presented as fact;
- duplicate notes when an existing staging entry should be updated by review status or linked instead.

## Claude rules

When using staging, Claude should:

1. treat staging as raw and untrusted;
2. preserve the original evidence trail;
3. distinguish confirmed, possible, unconfirmed and contradictory statements;
4. propose updates only to relevant `_curated/` artefacts;
5. add evidence links to proposed curated changes;
6. avoid unsupported "not affected" claims;
7. prefer "no known dependency found" or "not covered" where evidence is incomplete;
8. avoid creating duplicate curated pages where an existing page can be updated;
9. keep repo/component dependencies separate from infra/template dependencies;
10. create reviewer questions where evidence is incomplete.

## Reviewer rules

Reviewers should check:

- Is the staging type correct?
- Is the source clear?
- Is evidence present or is missing evidence explicit?
- Are raw claims separated from interpretation?
- Are uncertain claims marked as uncertain?
- Are proposed `_curated/` targets reasonable?
- Are sensitive details excluded?
- Does the proposed curated change preserve the right trust boundary?

## Curated targets

Staging entries may propose updates to:

```text
_curated/flows/
_curated/components/
_curated/infra/
_curated/maps/repo-dependency-map.json
_curated/maps/infra-dependency-map.json
_curated/maps/flow-component-map.json
_curated/runbooks/
_curated/standards/
_curated/incidents/learnings/
```

## Final rule

If a staging entry is useful but not proven, keep it in staging and mark the missing evidence.

Do not force uncertain knowledge into `_curated/` just to make Atlas look complete.


---

# 15. `_staging/runbooks/template.md`

```yaml
type: atlas.staging.runbook
title: ""
description: ""
resource: ""
tags: []
timestamp: YYYY-MM-DD
atlas_id: STG-YYYY-NNNN
status: new
confidence: raw-unreviewed

source_type: engineer-note
source_link: ""
runbook_type: investigation

related_flows: []
related_components: []
related_infra_templates: []
related_incident_learnings: []

intended_curated_targets:
  - "_curated/runbooks/"
  - "_curated/flows/"
  - "_curated/components/"
  - "_curated/infra/"
  - "_curated/incidents/learnings/"

captured_by: ""
review_notes: ""
```

## Summary

Briefly describe the runbook candidate or update.

## Problem or symptom

What symptom or condition should cause someone to use this runbook?

## When to use this runbook

Use this runbook when:

-

Do not use this runbook when:

-

## Affected flows, components and infra

### Flows

-

### Components

-

### Infra

-

## Investigation steps

List investigation steps. Mark unconfirmed steps clearly.

| Step | Action/check | Expected result | Evidence | Confidence |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

## Recovery steps

Only include recovery steps that are safe and evidence-backed.

| Step | Action | Risk/caution | Evidence | Confidence |
|---|---|---|---|---|
| 1 | | | | |

## Validation steps

How should the engineer confirm the issue is resolved?

-

## Useful logs, dashboards or checks

- Log/query/check:
- Dashboard:
- Evidence:

## Escalation

- Escalate when:
- Escalation link/contact group:
- Related owner/service page:

## Known failure modes

-

## Related incident learnings

-

## Evidence

- Existing runbook:
- Incident/Jira/Confluence reference:
- Repo/config path:
- Infra template:
- Dashboard/log reference:
- Engineer-supplied statement:
- Other:

## Suggested Atlas updates

Claude should consider whether this staging entry should update:

- `_curated/runbooks/...`
- `_curated/flows/...`
- `_curated/components/...`
- `_curated/infra/...`
- `_curated/incidents/learnings/...`

## Open questions

- Which steps need operational approval?
- Which checks are unconfirmed?
- Which escalation route needs confirmation?
- Does an existing runbook already cover this?

## Do not curate as fact unless reviewed

List claims that are plausible but not confirmed.

-


---

# 16. `_staging/standards/template.md`

```yaml
type: atlas.staging.standard
title: ""
description: ""
resource: ""
tags: []
timestamp: YYYY-MM-DD
atlas_id: STG-YYYY-NNNN
status: new
confidence: raw-unreviewed

source_type: engineer-note
source_link: ""
standard_type: unknown
applies_to: []

related_flows: []
related_components: []
related_runbooks: []
related_incident_learnings: []

intended_curated_targets:
  - "_curated/standards/"
  - "_curated/components/"
  - "_curated/flows/"
  - "_curated/runbooks/"
  - "_curated/incidents/learnings/"

captured_by: ""
review_notes: ""
```

## Summary

Briefly describe the proposed standard.

## Proposed standard

State the rule or guidance clearly.

## Standard type

Choose one:

```text
coding
api
event
data
etl
infra
runbook
testing
naming
operational
unknown
```

## Applies to

List where this standard applies.

- Component type:
- Flow type:
- Repo/group:
- Infra package type:
- Other:

## Rationale

Why should this standard exist?

-

## Examples

Provide examples of the standard applied correctly.

```text
Example here
```

## Non-examples or anti-patterns

Provide examples of what should be avoided.

```text
Example here
```

## Exceptions

When does this standard not apply?

-

## Related components, flows or runbooks

### Components

-

### Flows

-

### Runbooks

-

## Related incident learnings

List incidents or mock incidents that justify this standard.

-

## Evidence

- Code path:
- Existing documentation:
- Incident/Jira/Confluence reference:
- Review/MR reference:
- Runbook:
- Engineer-supplied statement:
- Other:

## Suggested Atlas updates

Claude should consider whether this staging entry should update:

- `_curated/standards/...`
- `_curated/components/...`
- `_curated/flows/...`
- `_curated/runbooks/...`
- `_curated/incidents/learnings/...`

## Open questions

- Is this agreed or only proposed?
- Who needs to approve it?
- Is the scope too broad?
- Are there valid exceptions?
- Does it contradict an existing standard?

## Do not curate as fact unless reviewed

List claims that are plausible but not confirmed.

-


---

# 17. Appendix — Staging sub-folder READMEs and templates

Previously extracted `_staging/` sub-folder documentation for changes, components,
flows, incidents, infrastructure and runbooks.

## Changes README

<!-- Source: atlas_changes_extracted.md -->

## `changes/README.md`

## `_staging/changes/`

### Purpose

`_staging/changes/` captures Atlas-relevant knowledge discovered during a code change, merge request, release candidate, production-bound change, or Claude Code investigation in a local repo.

This folder is mainly MR-driven, but it can be used at any point during the week when a change reveals reusable engineering context.

### When to use this folder

Use `_staging/changes/` when a change may affect or reveal:

- repo/component behaviour;
- API contracts;
- event schemas;
- table/data outputs;
- job schedules or job dependencies;
- shared library dependencies;
- infrastructure references;
- runbook gaps;
- standards or conventions;
- incident learnings;
- upstream/downstream relationships;
- Claude-discovered context that should not be lost.

### When not to use this folder

Do not use this folder for:

- a full end-to-end flow description; use `_staging/flows/`;
- onboarding a whole repo/component; use `_staging/components/`;
- raw infrastructure template discovery; use `_staging/infra/`;
- incident or mock incident learning; use `_staging/incidents/`;
- reusable operational procedure drafts; use `_staging/runbooks/`;
- reusable engineering rules; use `_staging/standards/`.

If the knowledge was discovered because of an MR/change, start here. Claude can propose updates to the correct `_curated` artefacts later.

### Operating rule

Every production-bound MR should be considered for Atlas.

### Operating rule

`_staging/changes/` entries are organised around a logical change, not necessarily a single MR.

A logical change may involve:

- one MR in one repo;
- multiple MRs across multiple repos;
- a production-bound release bundle;
- a local Claude Code investigation that discovers reusable Atlas context.

Every production-bound MR should be considered for Atlas, but related MRs may be captured together in one staging entry if they form one logical change.

Not every staged change needs a curated Atlas update.

A staged change may result in:

1. no Atlas update needed;
2. update to a component/repo page;
3. update to a flow page;
4. update to `_curated/maps/repo-dependency-map.json`;
5. update to `_curated/maps/infra-dependency-map.json`;
6. update to `_curated/maps/flow-component-map.json`;
7. update to a runbook;
8. update to a standard;
9. update to an incident learning;
10. reviewer decision that more evidence is needed.

### Trust rule

Files in `_staging/changes/` are raw evidence, not trusted Atlas knowledge.

Claude may use these files to propose changes, but trusted knowledge only exists after the relevant `_curated/` update is reviewed and approved through GitLab.

### Required filename format

Use:

```text
YYYY-MM-DD-mr-<mr-id>-<short-topic>.md
```

If there is no MR ID yet, use:

```text
YYYY-MM-DD-change-<short-topic>.md
```

Examples:

```text
2026-07-30-mr-1842-trade-status-schema.md
2026-07-30-change-trade-loader-output-table.md
2026-07-30-mr-2191-reference-data-api-contract.md
```

### Required frontmatter

Each file must use YAML frontmatter.

Required fields:

```yaml
type: atlas.staging.change
title: ""
description: ""
resource: ""
tags: []
timestamp: YYYY-MM-DD
atlas_id: STG-YYYY-NNNN
status: new
confidence: raw-unreviewed
source_type: mr | repo | claude-investigation | engineer-note
source_link: ""
repository: ""
local_path: ""
mr_id: ""
commit: ""
change_type: []
related_flows: []
related_components: []
related_infra_templates: []
related_runbooks: []
intended_curated_targets: []
```

### Allowed `change_type` values

Use one or more:

```text
api
event
schema
table
job
infra
library
config
behaviour
runbook
standard
incident-fix
documentation
unknown
```

### Evidence expectations

A useful staging change should include at least one evidence reference, such as:

- MR link or ID;
- commit SHA;
- changed file path;
- schema path;
- API definition;
- build/dependency file;
- infra template path;
- test evidence;
- runbook link;
- incident or Jira reference;
- developer-supplied statement clearly marked as such.

If evidence is missing, state what evidence is needed.

### Claude instructions

When curating from this folder, Claude should:

1. read the staged change;
2. identify the changed repo/component;
3. inspect relevant `_curated/components/` pages if they exist;
4. inspect related flow pages if named or discoverable;
5. inspect `_curated/maps/repo-dependency-map.json` for repo/component/data/contract relationships;
6. inspect `_curated/maps/infra-dependency-map.json` if infra/templates/resources are involved;
7. inspect `_curated/maps/flow-component-map.json` if a flow relationship may change;
8. propose only evidence-backed updates;
9. mark uncertainty explicitly;
10. avoid saying anything is "not affected" unless Atlas explicitly supports that claim.

### Reviewer checklist

Before approving a curated update based on a staged change, check:

- Is the MR/change clearly identified?
- Is the affected repo/component clear?
- Are changed files or evidence paths listed?
- Are contract, dependency or infra changes clearly described?
- Are unsupported claims marked as unconfirmed?
- Are proposed `_curated` targets reasonable?
- Do map updates match page updates?
- Is there anything that should remain in staging until more evidence is available?

---

## `changes/_template.md` — visible excerpt

List any changed APIs, events, schemas, tables, files or job outputs.

### Possible downstream effects

List possible downstream consumers or affected systems.

Mark anything uncertain as `possible` or `unconfirmed`.

## Suggested Atlas updates

Claude should consider whether this staging entry should update:

- `_curated/components/...`
- `_curated/flows/...`
- `_curated/maps/repo-dependency-map.json`
- `_curated/maps/infra-dependency-map.json`
- `_curated/maps/flow-component-map.json`
- `_curated/runbooks/...`
- `_curated/standards/...`
- `_curated/incidents/learnings/...`

## Open questions

- What needs reviewer confirmation?
- What evidence is missing?
- Which consumers, flows or infra dependencies are uncertain?
- Are tests or compatibility checks still outstanding?

## Do not curate as fact unless reviewed

List claims that are plausible but not confirmed.

---

## Changes Template

<!-- Source: changes_template_extracted.md -->

---
type: atlas.staging.change
title: ""
description: ""
resource: ""
tags: []
timestamp: YYYY-MM-DD
atlas_id: STG-YYYY-NNNN
status: new
confidence: raw-unreviewed

source_type: mr
source_link: ""
repositories: []
local_paths: []
mrs:
- id: ""
  repo: ""
  link: ""
  status: ""

commits: []

change_scope: single-repo | multi-repo | release-bundle | unknown

change_type:
- unknown

related_flows: []
related_components: []
related_infra_templates: []
related_runbooks: []

intended_curated_targets:
- "_curated/components/"
- "_curated/flows/"
- "_curated/maps/repo-dependency-map.json"
- "_curated/maps/infra-dependency-map.json"
- "_curated/maps/flow-component-map.json"

captured_by: ""
review_notes: ""
---

## Summary

Briefly describe the change.

Example:

> MR 1842 updates the `trade.status.updated` event schema by adding `settlementMethod`.

## Change context

### What changed?

Describe the actual change.

### Why was the change made?

Describe the reason or problem being solved.

### Where did the change happen?

- Repositories:
- Local paths:
- MRs:
- Commits:
- Changed files:

## Evidence

List evidence for the change.

- MR:
- Commit:
- Code path:
- Schema path:
- API definition:
- Build/dependency file:
- Infra template:
- Test evidence:
- Jira/change reference:
- Incident reference:
- Other:

## Atlas relevance

### Does this affect Atlas?

Choose one:

```text
yes
no
unknown
```

### Why?

Explain whether this affects flows, components, dependencies, infra, runbooks, standards or incident learnings.

## Change classification

Select all that apply:

```text
[ ] API changed
[ ] Event/schema changed
[ ] Table/data output changed
[ ] Job schedule/dependency changed
[ ] Shared library dependency changed
[ ] Infra/template/resource reference changed
[ ] Runtime behaviour changed
[ ] Runbook or recovery process changed
[ ] Standard/convention changed
[ ] Incident fix or operational learning
[ ] Documentation-only change
[ ] Unknown
```

## Dependency impact

### New dependencies

List any new known dependencies.

### Removed dependencies

List any removed dependencies.

### Changed contracts

List any changed APIs, events, schemas, tables, files or job outputs.

### Possible downstream effects

List possible downstream consumers or affected systems.

Mark anything uncertain as `possible` or `unconfirmed`.

## Suggested Atlas updates

Claude should consider whether this staging entry should update:

- `_curated/components/...`
- `_curated/flows/...`
- `_curated/maps/repo-dependency-map.json`
- `_curated/maps/infra-dependency-map.json`
- `_curated/maps/flow-component-map.json`
- `_curated/runbooks/...`
- `_curated/standards/...`
- `_curated/incidents/learnings/...`

## Open questions

- What needs reviewer confirmation?
- What evidence is missing?
- Which consumers, flows or infra dependencies are uncertain?
- Are tests or compatibility checks still outstanding?

## Do not curate as fact unless reviewed

List claims that are plausible but not confirmed.

---

## Components README

<!-- Source: components_readme_extracted.md -->

## `_staging/components/`

### Purpose

`_staging/components/` captures raw, untrusted knowledge about a DataLens repo, service, job, library, API, consumer, producer, Lambda or other implementation component.

Use this folder when the knowledge is mainly about one component and how it fits into flows, dependencies, infrastructure, runbooks and standards.

A component entry should help answer:

> What is this component, where does it live, what does it do, and which flows or dependencies does it participate in?

### When to use this folder

Use `_staging/components/` when capturing or updating knowledge about:

- a repo or monorepo submodule;
- a Java service;
- an ETL job;
- a Kafka consumer or producer;
- a Lambda;
- an API component;
- a shared library;
- a batch job;
- a data publisher or data consumer;
- a component's responsibilities;
- what the component consumes or produces;
- which flows the component participates in;
- which infrastructure templates or resources support the component;
- relevant runbooks, standards or incident learnings.

### When not to use this folder

Do not use this folder for:

- a single MR or code change; use `_staging/changes/`;
- an end-to-end process across multiple components; use `_staging/flows/`;
- raw infrastructure template/resource discovery; use `_staging/infra/`;
- a specific incident or mock incident learning; use `_staging/incidents/`;
- a reusable operational procedure draft; use `_staging/runbooks/`;
- a reusable engineering rule; use `_staging/standards/`.

If a component entry reveals flow, dependency-map, infra, runbook or incident-learning updates, Claude can propose changes to the relevant `_curated` artefacts later.

### Operating rule

A staged component entry should describe observed or supplied component knowledge.

It should not invent ownership, dependencies, consumers or runtime behaviour.

It is acceptable for a component entry to be incomplete if the gaps are explicit.

A staged component may result in:

1. creation or update of a `_curated/components/` page;
2. updates to `_curated/maps/repo-dependency-map.json`;
3. updates to `_curated/maps/infra-dependency-map.json`;
4. updates to `_curated/maps/flow-component-map.json`;
5. links from one or more `_curated/flows/` pages;
6. links to runbooks, standards or incident learnings;
7. reviewer decision that more evidence is needed.

### Component granularity rule

A component page should usually represent a meaningful repo, monorepo submodule, deployable unit, scheduled job group, service, API, library or operationally relevant component.

Do not create a separate component page for every Lambda, Glue job, SQL file, handler or script by default.

Instead, capture lower-level artefacts inside the parent component page under `Internal units`.

Create a separate component page for an internal unit only if it is:

- independently deployable;
- independently scheduled;
- independently operated or monitored;
- has its own runbook;
- has its own consumers or downstream dependencies;
- appears in multiple flows;
- has blast-radius impact on its own;
- changes often enough to need a stable Atlas page.

### Trust rule

Files in `_staging/components/` are raw evidence, not trusted Atlas knowledge.

Claude may use these files to propose curated component updates, but trusted component knowledge only exists after the relevant `_curated/` update is reviewed and approved through GitLab.

### Required filename format

Use:

```text
YYYY-MM-DD-component-<component-name>.md
```

Examples:

```text
2026-07-30-component-trade-loader.md
2026-07-30-component-settlement-batch.md
2026-07-30-component-reference-data-api.md
```

### Required frontmatter

Each file must use YAML frontmatter.

Required fields:

```yaml
type: atlas.staging.component
title: ""
description: ""
resource: ""
tags: []
timestamp: YYYY-MM-DD
atlas_id: STG-YYYY-NNNN
status: new
confidence: raw-unreviewed
source_type: repo | mr | confluence | jira | teams | email | sharepoint | engineer-note
  | incident | mock-incident | claude-investigation
source_link: ""
component_name: ""
component_type: service | job | etl-job | kafka-consumer | kafka-producer | lambda
  | api | shared-library | infra-module | batch | other | unknown
monorepo_path: ""
repository: ""
related_flows: []
related_components: []
related_infra_templates: []
related_runbooks: []
related_standards: []
related_incident_learnings: []
intended_curated_targets: []
```

### Allowed `component_type` values

Use one:

```text
service
job
etl-job
kafka-consumer
kafka-producer
lambda
api
shared-library
infra-module
batch
other
unknown
```

### Evidence expectations

A useful staged component should include evidence such as:

- repo or monorepo path;
- README or local documentation;
- build/dependency file;
- source code path;
- config path;
- schema or contract path;
- infra template path;
- runbook link;
- incident reference;
- Confluence/Jira reference;
- developer supplied statement clearly marked as such.

If a responsibility, dependency, producer/consumer relationship or flow membership is inferred, mark it as `possible` or `unconfirmed`.

### Claude instructions

When curating from this folder, Claude should:

1. read the staged component entry;
2. identify the component name, type and monorepo path;
3. inspect any existing `_curated/components/` page for the component;
4. inspect `_curated/maps/repo-dependency-map.json` for existing repo/component/data/contract relationships;
5. inspect `_curated/maps/infra-dependency-map.json` if infra templates or resources are named;
6. inspect `_curated/maps/flow-component-map.json` if related flows are named;
7. inspect related `_curated/flows/`, `_curated/runbooks/`, `_curated/standards/` and `_curated/incidents/learnings/` pages where relevant;
8. propose only evidence-backed updates;
9. mark unknown responsibilities, consumers or dependencies explicitly;
10. avoid creating duplicate component pages if an existing page can be updated.

### Reviewer checklist

Before approving a curated update based on a staged component, check:

- Is the component clearly identified?
- Is the monorepo path or repo location clear?
- Is the component type correct or explicitly unknown?
- Are responsibilities supported by evidence?
- Are consumes/produces relationships supported by evidence?
- Are related flows supported or marked as unconfirmed?
- Are infra dependencies separated from repo/component dependencies?
- Are runbooks, standards and incident learnings linked only when relevant?
- Do map updates match the component page?
- Is anything being overstated as fact?

---

## Components Template

<!-- Source: components_template_extracted.md -->

---
type: atlas.staging.component
title: ""
description: ""
resource: ""
tags: []
timestamp: YYYY-MM-DD
atlas_id: STG-YYYY-NNNN
status: new
confidence: raw-unreviewed

source_type: claude-investigation
source_link: ""
component_name: ""
component_type: unknown
monorepo_path: ""
repository: ""

related_flows: []
related_components: []
related_infra_templates: []
related_runbooks: []
related_standards: []
related_incident_learnings: []

intended_curated_targets:
- "_curated/components/"
- "_curated/maps/repo-dependency-map.json"
- "_curated/maps/infra-dependency-map.json"
- "_curated/maps/flow-component-map.json"
- "_curated/flows/"
- "_curated/runbooks/"
- "_curated/standards/"
- "_curated/incidents/learnings/"

captured_by: ""
review_notes: ""
---

## Summary

Briefly describe the component and why this staging entry exists.

Example:

> This entry captures initial knowledge about `trade-processing/trade-loader`,
> including its responsibility, inputs, outputs and related trade ingestion flow.

## Component identity

### Component name

Name the component.

### Component type

Choose one:

```text
service
job
etl-job
kafka-consumer
kafka-producer
lambda
api
shared-library
infra-module
batch
other
unknown
```

### Location

- Repository:
- Monorepo path:
- Main README:
- Key source/config paths:

## Responsibility

Describe what this component is known to do.

Mark uncertain responsibilities as `possible` or `unconfirmed`.

## Internal units

Use this section for Lambdas, Glue jobs, SQL files, handlers, scripts or other lower-level artefacts that belong inside this component.

Do not split these into separate component pages unless they are independently meaningful. If you do, maintain a link.

| Unit | Type | Purpose | Path | Evidence | Confidence |
|---|---|---|---|---|---|
|  | lambda/glue-job/sql/handler/script/other |  |  |  |  |

## Consumes

List known inputs consumed by this component.

| Kind | Name | From | Evidence | Confidence |
|---|---|---|---|---|
| event/api/table/file/config/library/job-output |  |  |  |  |

## Produces

List known outputs produced by this component.

| Kind | Name | Used by | Evidence | Confidence |
|---|---|---|---|---|
| event/api/table/file/log/alert/job-output |  |  |  |  |

## Related flows

List flows this component participates in.

| Flow | Role in flow | Evidence | Confidence |
|---|---|---|---|
|  |  |  |  |

## Related infrastructure

List infra templates/resources known to support this component.

| Template/Resource | Relationship | Evidence | Confidence |
|---|---|---|---|
|  |  |  |  |

## Local development guidance

Prefer linking to the local README if exact commands may drift.

- Build:
- Test:
- Run locally:
- Local README:

## Operational notes

List known operational notes, alerts, dashboards, common failure modes or support concerns.

-

## Runbooks

List related runbooks.

-

## Standards

List relevant standards or conventions.

-

## Incident learnings

List related incident learnings.

-

## Evidence

List all supporting evidence.

- Repo path:
- README:
- Code path:
- Config path:
- Schema/contract path:
- Build/dependency file:
- Infra template:
- Runbook:
- Incident/Jira/Confluence reference:
- Engineer-supplied statement:
- Other:

## Suggested Atlas updates

Claude should consider whether this staging entry should update:

- `_curated/components/...`
- `_curated/flows/...`
- `_curated/maps/repo-dependency-map.json`
- `_curated/maps/infra-dependency-map.json`
- `_curated/maps/flow-component-map.json`
- `_curated/runbooks/...`
- `_curated/standards/...`
- `_curated/incidents/learnings/...`

## Open questions

- What responsibility is unclear?
- Which inputs or outputs need confirmation?
- Which consumers or producers are uncertain?
- Which flows need confirmation?
- Which infra relationships are known versus suspected?

## Do not curate as fact unless reviewed

List claims that are plausible but not confirmed.

-

---

## Flows README

<!-- Source: flows_readme_extracted.md -->

## `_staging/flows/`

### Purpose

`_staging/flows/` captures raw, untrusted knowledge about an end-to-end DataLens flow or pipeline.

Use this folder when the knowledge is mainly about how multiple components, jobs, data outputs, infrastructure resources, runbooks and dependencies work together across a path of execution or data movement.

A flow entry should help answer:

> How does this flow behave end to end, and what might break if it fails or changes?

### When to use this folder

Use `_staging/flows/` when capturing or updating knowledge about:

- an end-to-end data flow;
- a pipeline across multiple repos/components;
- a business or technical process that crosses components;
- upstream and downstream dependencies across a path;
- jobs, schedules or data movement across multiple steps;
- infrastructure resources used by a flow;
- runbooks or incident learnings tied to a flow;
- mock incident flow walkthroughs;
- Claude-discovered flow context that should not be lost.

Examples:

```text
trade ingestion to warehouse
pricing refresh
reference data publication
API consumption flow
ETL pipeline flow
Kafka event processing flow
```

### When not to use this folder

Do not use this folder for:

- a single MR or code change; use `_staging/changes/`;
- onboarding a single repo/component; use `_staging/components/`;
- raw infrastructure template discovery; use `_staging/infra/`;
- a specific incident learning; use `_staging/incidents/`;
- a reusable operational procedure draft; use `_staging/runbooks/`;
- a reusable engineering rule; use `_staging/standards/`.

If a flow entry reveals component, repo, infra, runbook or incident-learning updates, Claude can propose changes to the relevant `_curated` artefacts later.

### Operating rule

A staged flow should describe observed or supplied knowledge, not invent missing steps.

It is acceptable for a flow entry to be incomplete if the gaps are explicit.

A staged flow may result in:

1. creation or update of a `_curated/flows/` page;
2. updates to `_curated/maps/flow-component-map.json`;
3. updates to `_curated/maps/repo-dependency-map.json`;
4. updates to `_curated/maps/infra-dependency-map.json`;
5. links to component pages;
6. links to runbooks;
7. links to incident learnings;
8. reviewer decision that more evidence is needed.

### Trust rule

Files in `_staging/flows/` are raw evidence, not trusted Atlas knowledge.

Claude may use these files to propose curated flow updates, but trusted flow knowledge only exists after the relevant `_curated/` update is reviewed and approved through GitLab.

### Required filename format

Use:

```text
YYYY-MM-DD-flow-<short-flow-name>.md
```

Examples:

```text
2026-07-30-flow-trade-ingestion-to-warehouse.md
2026-07-30-flow-pricing-refresh.md
2026-07-30-flow-reference-data-publication.md
```

### Required frontmatter

Each file must use YAML frontmatter.

Required fields:

```yaml
type: atlas.staging.flow
title: ""
description: ""
resource: ""
tags: []
timestamp: YYYY-MM-DD
atlas_id: STG-YYYY-NNNN
status: new
confidence: raw-unreviewed
source_type: repo | confluence | jira | teams | email | sharepoint | engineer-note | incident
  | mock-incident | claude-investigation
source_link: ""
flow_name: ""
flow_status: draft | partial | candidate | update
entry_point: ""
end_point: ""
related_flows: []
related_components: []
related_infra_templates: []
related_runbooks: []
related_incident_learnings: []
intended_curated_targets: []
```

### Evidence expectations

A useful staged flow should include evidence such as:

- repo paths;
- component names;
- job names;
- schema or contract paths;
- infra template paths;
- runbook links;
- incident references;
- Confluence/Jira links;
- developer supplied statements clearly marked as such.

If the flow is based on a walkthrough or engineer explanation, say so clearly.

If a step is inferred, mark it as `possible` or `unconfirmed`.

### Claude instructions

When curating from this folder, Claude should:

1. read the staged flow entry;
2. identify the proposed flow boundary;
3. identify the entry point, output and main steps;
4. inspect relevant `_curated/components/` pages if they exist;
5. inspect `_curated/maps/flow-component-map.json` for existing flow links;
6. inspect `_curated/maps/repo-dependency-map.json` for repo/component/data/contract relationships;
7. inspect `_curated/maps/infra-dependency-map.json` for template/resource relationships;
8. propose only evidence-backed updates;
9. keep unknown or unconfirmed steps explicit;
10. avoid creating duplicate flow pages if an existing flow can be updated.

### Reviewer checklist

Before approving a curated update based on a staged flow, check:

- Is the flow boundary clear?
- Are entry point and output clear?
- Are components and jobs identified with evidence?
- Are upstream and downstream dependencies supported?
- Are infra resources separated from repo/component dependencies?
- Are unknown steps or consumers clearly marked?
- Does the flow page link to related component pages, maps, runbooks and incident learnings?
- Do map updates match the curated flow page?
- Is anything being overstated as fact?

---

## Flows Template

<!-- Source: flows_template_extracted.md -->

---
type: atlas.staging.flow
title: ""
description: ""
resource: ""
tags: []
timestamp: YYYY-MM-DD
atlas_id: STG-YYYY-NNNN
status: new
confidence: raw-unreviewed

source_type: engineer-note
source_link: ""
flow_name: ""
flow_status: draft
entry_point: ""
end_point: ""

related_flows: []
related_components: []
related_infra_templates: []
related_runbooks: []
related_incident_learnings: []

intended_curated_targets:
- "_curated/flows/"
- "_curated/maps/flow-component-map.json"
- "_curated/maps/repo-dependency-map.json"
- "_curated/maps/infra-dependency-map.json"
- "_curated/components/"
- "_curated/runbooks/"
- "_curated/incidents/learnings/"

captured_by: ""
review_notes: ""
---

## Summary

Briefly describe the flow or pipeline.

Example:

> This entry captures the known steps for the trade ingestion to warehouse flow,
> including input source, processing components, warehouse output and downstream consumers.

## Flow context

### Flow name

Name the flow.

### Purpose

What business or technical purpose does this flow support?

### Flow boundary

Define what is inside and outside this flow.

- Starts at:
- Ends at:
- Out of scope:

## End-to-end steps

List the known steps. Mark uncertain steps as `possible` or `unconfirmed`.

| Step | Description | Component/job/resource | Evidence | Confidence |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |

## Components involved

List known repos/components/services/jobs/libraries involved in the flow.

| Component | Role in flow | Monorepo path | Evidence | Confidence |
|---|---|---|---|---|
|  |  |  |  |  |

## Upstream dependencies

List data, jobs, events, APIs, files, schedules, tables or systems that must exist before this flow can run.

-

## Downstream consumers

List known consumers affected by this flow.

-

## Jobs and schedules

List relevant jobs, batches, schedules or orchestration points.

-

## Infrastructure involved

List infra templates/resources involved in this flow.

- Template/resource:
- Relationship:
- Evidence:
- Confidence:

## Contracts and data outputs

List known APIs, events, schemas, tables, files or data outputs.

- Contract/output:
- Produced by:
- Consumed by:
- Evidence:
- Confidence:

## Runbooks

List runbooks or operational guidance related to this flow.

-

## Incident learnings

List related real, mock or near-miss incident learnings.

-

## Evidence

List all supporting evidence.

- Repo path:
- Config path:
- Schema/contract path:
- Infra template:
- Runbook:
- Incident/Jira/Confluence reference:
- Engineer-supplied statement:
- Other:

## Suggested Atlas updates

Claude should consider whether this staging entry should update:

- `_curated/flows/...`
- `_curated/components/...`
- `_curated/maps/flow-component-map.json`
- `_curated/maps/repo-dependency-map.json`
- `_curated/maps/infra-dependency-map.json`
- `_curated/runbooks/...`
- `_curated/incidents/learnings/...`

## Open questions

- Which steps are unknown?
- Which components need confirmation?
- Which upstream/downstream dependencies are uncertain?
- Which infra resources are known versus suspected?
- Are any consumers missing?

## Do not curate as fact unless reviewed

List claims that are plausible but not confirmed.

-

---

## Incidents README

<!-- Source: incidents_readme_extracted.md -->

## `_staging/incidents/`

### Purpose

`_staging/incidents/` captures raw, untrusted incident learnings, mock incident notes, near misses and operational scenarios that may improve Atlas flows, runbooks, dependency maps or component context.

This folder is not an incident management system. It should not replace full incident records.

It captures reusable operational memory:

> What happened, what was hard to diagnose, what Atlas should remember,
> and which curated artefacts may need updating.

### When to use this folder

Use `_staging/incidents/` for:

- real incident learnings;
- mock incident learnings;
- near misses;
- operational learning notes;
- post-incident observations;
- repeated failure patterns;
- runbook gaps discovered during an incident;
- missing dependency knowledge discovered during triage;
- flow or infra context that was hard to find during investigation.

### When not to use this folder

Do not use this folder for:

- a full major incident record; link to the full record instead;
- a general flow description; use `_staging/flows/`;
- a single code change or MR fix; use `_staging/changes/`;
- a component onboarding note; use `_staging/components/`;
- a full runbook draft; use `_staging/runbooks/`;
- a general standard; use `_staging/standards/`.

If an incident reveals a missing flow, component, runbook or infra relationship, capture the learning here and let Claude propose the correct `_curated/` updates.

### Operating rule

Incident staging entries should focus on reusable learning, not exhaustive incident history.

A staged incident may result in:

1. creation or update of an incident learning in `_curated/incidents/learnings/`;
2. updates to a flow page;
3. updates to a component page;
4. updates to a runbook;
5. updates to `_curated/maps/repo-dependency-map.json`;
6. updates to `_curated/maps/infra-dependency-map.json`;
7. reviewer decision that more evidence is needed.

### Trust rule

Files in `_staging/incidents/` are raw evidence, not trusted Atlas knowledge.

A staged incident learning only becomes trusted when the relevant `_curated/` update is reviewed and approved through GitLab.

### Required filename format

Use:

```text
YYYY-MM-DD-incident-<short-topic>.md
```

For mock incidents, use:

```text
YYYY-MM-DD-mock-incident-<short-topic>.md
```

Examples:

```text
2026-07-30-incident-schema-mismatch-settlement.md
2026-07-30-mock-incident-stale-trade-data.md
2026-07-30-incident-pricing-refresh-delay.md
```

### Required frontmatter

```yaml
type: atlas.staging.incident
title: ""
description: ""
resource: ""
tags: []
timestamp: YYYY-MM-DD
atlas_id: STG-YYYY-NNNN
status: new
confidence: raw-unreviewed
source_type: incident | mock-incident | near-miss | engineer-note | jira | confluence
  | teams | email | claude-investigation
source_link: ""
incident_type: real | mock | near-miss | operational-learning
severity: unknown
related_flows: []
related_components: []
related_infra_templates: []
related_runbooks: []
related_incident_records: []
intended_curated_targets: []
```

### Evidence expectations

A useful incident staging entry should include:

- incident or mock incident reference;
- affected flow;
- affected components;
- affected infra resources if known;
- symptom;
- suspected or confirmed cause;
- what helped diagnosis;
- what was missing or hard to find;
- runbook gaps;
- links to full incident records where appropriate;
- evidence or a clear statement that the learning is developer-supplied.

### Claude instructions

When curating from this folder, Claude should:

1. identify the reusable learning;
2. avoid copying full incident records into `_curated/`;
3. link to full records where needed;
4. identify affected flows, components, infra and runbooks;
5. propose updates to incident learnings, runbooks, flow pages and maps where evidence supports it;
6. mark suspected causes as suspected unless confirmed;
7. avoid overstating blast radius;
8. avoid “not affected” claims unless explicitly proven.

### Reviewer checklist

Before approving a curated update based on incident staging, check:

- Is this a reusable learning rather than a full incident record?
- Is the affected flow clear?
- Are affected components and infra supported by evidence?
- Is the cause confirmed or only suspected?
- Are runbook gaps clear?
- Are dependency-map updates justified?
- Are links to full records included where needed?
- Is sensitive incident detail excluded from Atlas if it should not be copied?

---

## Incidents Template

<!-- Source: incidents_template_extracted.md -->

---
type: atlas.staging.incident
title: ""
description: ""
resource: ""
tags: []
timestamp: YYYY-MM-DD
atlas_id: STG-YYYY-NNNN
status: new
confidence: raw-unreviewed

source_type: mock-incident
source_link: ""
incident_type: mock
severity: unknown

related_flows: []
related_components: []
related_infra_templates: []
related_runbooks: []
related_incident_records: []

intended_curated_targets:
- "_curated/incidents/learnings/"
- "_curated/flows/"
- "_curated/components/"
- "_curated/infra/"
- "_curated/runbooks/"
- "_curated/maps/repo-dependency-map.json"
- "_curated/maps/infra-dependency-map.json"
- "_curated/maps/flow-component-map.json"

captured_by: ""
review_notes: ""
---

## Summary

Briefly describe the incident, mock incident or operational learning.

## Incident type

Choose one:

```text
real
mock
near-miss
operational-learning
```

## What happened or was simulated?

Describe the event or scenario.

## Affected flow

- Flow:
- Evidence:
- Confidence:

## Affected components

| Component | Role in incident | Evidence | Confidence |
|---|---|---|---|
|  |  |  |  |

## Affected infrastructure

| Infra package/resource | Role in incident | Evidence | Confidence |
|---|---|---|---|
|  |  |  |  |

## Symptoms

List observable symptoms.

-

## Cause

### Confirmed cause

If known, describe the confirmed cause.

### Suspected cause

If not confirmed, describe suspected causes and mark them clearly as unconfirmed.

## What helped diagnosis?

List evidence, logs, dashboards, tests, runbooks or knowledge that helped.

-

## What was hard to find?

List missing or hard-to-find context.

-

## What Atlas should remember

Write the reusable learning Atlas should preserve.

-

## Runbook impact

- Existing runbook:
- Missing runbook:
- Suggested runbook update:

## Dependency map impact

### Repo/component dependencies

List known dependency-map changes or gaps.

-

### Infra dependencies

List known infra-map changes or gaps.

-

## Links to full records

Do not paste full major incident records unless explicitly allowed. Link to them instead.

-

## Evidence

- Incident record:
- Mock incident notes:
- Jira/change reference:
- Runbook:
- Logs/dashboard reference:
- Repo/config path:
- Infra template:
- Engineer-supplied statement:
- Other:

## Suggested Atlas updates

Claude should consider whether this staging entry should update:

- `_curated/incidents/learnings/...`
- `_curated/flows/...`
- `_curated/components/...`
- `_curated/infra/...`
- `_curated/runbooks/...`
- `_curated/maps/repo-dependency-map.json`
- `_curated/maps/infra-dependency-map.json`
- `_curated/maps/flow-component-map.json`

## Open questions

- What cause still needs confirmation?
- Which components or infra resources are uncertain?
- Which runbook gap needs review?
- Which dependency relationship needs evidence?

## Do not curate as fact unless reviewed

List claims that are plausible but not confirmed.

-

---

## Infrastructure README

<!-- Source: infra_readme_extracted.md -->

## `_staging/infra/`

### Purpose

`_staging/infra/` captures raw, untrusted knowledge about infrastructure packages, service catalogue templates, configuration files, cloud resources, deployment dependencies and resource relationships used by DataLens.

Use this folder when the knowledge is mainly about infrastructure rather than application/component behaviour.

An infra entry should help answer:

> Which infrastructure package or resource exists, how is it connected, which components use it,
> and which flows could be affected if it changes or fails?

### When to use this folder

Use `_staging/infra/` when capturing or updating knowledge about:

- an infra package/folder;
- `product.template.yaml` or equivalent service catalogue template;
- `metadata.yaml` or service catalogue metadata;
- environment-specific folders such as `dev/`, `uat/` and `prod/`;
- supporting scripts such as `preconfig.sh`;
- queues, topics, buckets, Lambdas, ECS resources, databases, policies, roles or parameters;
- resource dependencies;
- template outputs, exports or imports;
- scheduled triggers;
- permissions or IAM relationships;
- alarms, monitors or operational resources;
- infrastructure used by one or more components;
- infrastructure used by one or more flows;
- Claude-discovered infra context that should not be lost.

Examples:

```text
CloudFormation/SAM/Terraform-style template discovery
service catalogue template package discovery
Lambda and queue relationship
S3 bucket used by a Glue job
scheduler triggering an ETL job
IAM role used by a DataLens Lambda
alarm monitoring a pipeline failure condition
```

### When not to use this folder

Do not use this folder for:

- a single MR or logical code change; use `_staging/changes/`;
- an end-to-end flow description; use `_staging/flows/`;
- general component/repo onboarding; use `_staging/components/`;
- a specific incident or mock incident learning; use `_staging/incidents/`;
- a reusable operational procedure draft; use `_staging/runbooks/`;
- a reusable engineering rule; use `_staging/standards/`.

If infra knowledge was discovered during an MR or code change, it can start in `_staging/changes/`.
Claude can later propose an `_staging/infra/` entry or curated infra update if the resource relationship is reusable.

### Infra granularity rule

A curated infra page should usually represent one meaningful infra package/folder, especially where that folder contains files such as:

- `product.template.yaml`;
- `metadata.yaml`;
- `preconfig.sh`;
- `dev/`;
- `uat/`;
- `prod/`;
- `src/`.

Do not create a separate infra page for every environment folder, script, YAML resource or individual cloud resource by default.

Instead, capture lower-level artefacts inside the parent infra package page under `Internal resources` or `Infra package structure`.

Create a separate infra page for an internal resource only if it is:

- shared by multiple infra packages;
- used by multiple flows;
- operationally critical;
- independently operated or monitored;
- independently changed or deployed;
- attached to its own runbook;
- repeatedly incident-relevant;
- a major blast-radius node, such as a shared bucket, shared queue, shared IAM policy, shared database, shared cluster or shared networking layer.

### Operating rule

Infrastructure relationships belong in `_curated/maps/infra-dependency-map.json`.

Repo/component relationships belong in `_curated/maps/repo-dependency-map.json`.

If a component depends on an infrastructure output or resource, both maps may need links, but the infrastructure resource relationship itself should remain in the infra map.

A staged infra entry may result in:

1. creation or update of an `_curated/infra/` page;
2. updates to `_curated/maps/infra-dependency-map.json`;
3. updates to `_curated/maps/flow-component-map.json` if flows use the resources;
4. updates to `_curated/components/` pages if components rely on the resources;
5. updates to runbooks or incident learnings if operationally relevant;
6. reviewer decision that more evidence is needed.

### Trust rule

Files in `_staging/infra/` are raw evidence, not trusted Atlas knowledge.

Claude may use these files to propose curated infra updates, but trusted infrastructure knowledge only exists after the relevant `_curated/` update is reviewed and approved through GitLab.

### Required filename format

Use:

```text
YYYY-MM-DD-infra-<infra-package-or-topic>.md
```

Examples:

```text
2026-07-30-infra-tradedata-api-monthly-flow.md
2026-07-30-infra-marketmind-knowledgebase.md
2026-07-30-infra-94-lambda-generate-tlda-token.md
```

### Optional grouping

Early implementation may keep files flat:

```text
_staging/infra/2026-07-30-infra-tradedata-api-monthly-flow.md
```

If volume grows, group by infra package:

```text
_staging/infra/tradedata-api-monthly-flow/2026-07-30-template-discovery.md
```

### Required frontmatter

Each file must use YAML frontmatter.

Required fields:

```yaml
type: atlas.staging.infra
title: ""
description: ""
resource: ""
tags: []
timestamp: YYYY-MM-DD
atlas_id: STG-YYYY-NNNN
status: new
confidence: raw-unreviewed
source_type: repo | mr | confluence | jira | teams | email | sharepoint | engineer-note
  | incident | mock-incident | claude-investigation
source_link: ""
infra_scope: []
infra_package: ""
infra_package_path: ""
service_catalogue_template: ""
metadata_path: ""
preconfig_path: ""
environments: []
contains_internal_resources: true
resource_names: []
related_flows: []
related_components: []
related_infra_templates: []
related_runbooks: []
related_incident_learnings: []
intended_curated_targets: []
```

### Allowed `infra_scope` values

Use one or more:

```text
infra-package
service-catalogue-template
template
resource
config
deployment
permission
monitoring
scheduler
network
database
storage
queue
topic
function
policy
environment-config
script
metadata
unknown
```

### Evidence expectations

A useful staged infra entry should include evidence such as:

- infra package/folder path;
- `product.template.yaml` path;
- `metadata.yaml` path;
- environment folder paths;
- supporting script paths;
- resource name;
- logical ID;
- parameter/export/import name;
- schedule definition;
- IAM role or permission reference;
- monitoring/alarm reference;
- component that uses the resource;
- flow that uses the resource;
- incident or runbook reference;
- developer supplied statement clearly marked as such.

If a package relationship, resource relationship or environment difference is inferred, mark it as `possible` or `unconfirmed`.

### Claude instructions

When curating from this folder, Claude should:

1. read the staged infra entry;
2. identify the infra package/folder being described;
3. identify the service catalogue template, metadata file, environment folders and supporting scripts;
4. identify resources created, referenced, imported or exported;
5. inspect any existing `_curated/infra/` page for the package or area;
6. inspect `_curated/maps/infra-dependency-map.json` for existing resource relationships;
7. inspect `_curated/maps/flow-component-map.json` if flows are named;
8. inspect `_curated/components/` pages if components use the resources;
9. propose only evidence-backed infra updates;
10. keep unknown or suspected resource relationships explicit;
11. avoid mixing infrastructure relationships into `_curated/maps/repo-dependency-map.json`;
12. unless the relationship is specifically a component using an infra output.

### Reviewer checklist

Before approving a curated update based on staged infra knowledge, check:

- Is the infra package/folder clearly identified?
- Is the service catalogue template path clear?
- Are environment folders and supporting files represented correctly?
- Are resource names or logical IDs supported by evidence?
- Are resource relationships explicit and evidence-backed?
- Are component-to-resource relationships supported?
- Are flow-to-resource relationships supported or marked as unconfirmed?
- Are permissions, triggers, schedules and monitoring relationships separated clearly?
- Are infra dependencies represented in `_curated/maps/infra-dependency-map.json`?
- Are any repo/component map updates genuinely component-level rather than infra-level?
- Is anything being overstated as fact?

---

## Infrastructure Template

<!-- Source: infra_template_extracted.md -->

---
type: atlas.staging.infra
title: ""
description: ""
resource: ""
tags: []
timestamp: YYYY-MM-DD
atlas_id: STG-YYYY-NNNN
status: new
confidence: raw-unreviewed

source_type: claude-investigation
source_link: ""
infra_scope:
- infra-package
  infra_package: ""
  infra_package_path: ""
  service_catalogue_template: ""
  metadata_path: ""
  preconfig_path: ""
  environments:
- dev
- uat
- prod
  contains_internal_resources: true
  resource_names: []

related_flows: []
related_components: []
related_infra_templates: []
related_runbooks: []
related_incident_learnings: []

intended_curated_targets:
- "_curated/infra/"
- "_curated/maps/infra-dependency-map.json"
- "_curated/maps/flow-component-map.json"
- "_curated/components/"
- "_curated/runbooks/"
- "_curated/incidents/learnings/"

captured_by: ""
review_notes: ""
---

## Summary

Briefly describe the infrastructure package or resource knowledge captured in this entry.

Example:

> This entry captures the structure and known resources for `tradedata-api-monthly-flow`,
> including `product.template.yaml`, `metadata.yaml`, environment folders and any resources used by related components or flows.

## Infrastructure package identity

### Package name

Name the infra package or folder.

### Location

- Infra package path:
- Service catalogue template:
- Metadata file:
- Preconfig script:
- Source folder:
- Related deployment path:

## Infra package structure

Describe the package layout. Mark uncertain information as `possible` or `unconfirmed`.

| Path | Type | Purpose | Evidence | Confidence |
|---|---|---|---|---|
| metadata.yaml | metadata |  |  |  |
| product.template.yaml | service-catalogue-template |  |  |  |
| preconfig.sh | script |  |  |  |
| dev/ | environment-config |  |  |  |
| uat/ | environment-config |  |  |  |
| prod/ | environment-config |  |  |  |
| src/ | source |  |  |  |

## Environment notes

Capture known differences between environments if relevant.

| Environment | Path | Difference or note | Evidence | Confidence |
|---|---|---|---|---|
| dev |  |  |  |  |
| uat |  |  |  |  |
| prod |  |  |  |  |

## Internal resources

Use this section for resources defined inside the package.

Do not split these into separate infra pages unless they are shared, independently operated, incident-relevant, flow-critical or reused across multiple components.

| Resource name/logical ID | Resource type | Defined in | Purpose | Evidence | Confidence |
|---|---|---|---|---|---|
|  | lambda/queue/topic/bucket/database/role/policy/scheduler/alarm/other |  |  |  |  |

## Resource relationships

List relationships between resources.

| From resource | Relationship | To resource | Evidence | Confidence |
|---|---|---|---|---|
|  | depends_on_resource / triggers / reads_from / writes_to / exports_value / imports_value / permission_to |  |  |  |

## Components using these resources

List known components that use or depend on these resources.

| Component | Resource | Relationship | Evidence | Confidence |
|---|---|---|---|---|
|  |  | uses_resource / reads_from / writes_to / triggered_by / scheduled_by |  |  |

## Flows using these resources

List known flows that rely on these resources.

| Flow | Resource | Role in flow | Evidence | Confidence |
|---|---|---|---|---|
|  |  |  |  |  |

## Parameters, exports and imports

List known parameters, exports, imports or shared values.

| Name | Kind | Producer | Consumer | Evidence | Confidence |
|---|---|---|---|---|---|
|  | parameter/export/import |  |  |  |  |

## Schedules, triggers and events

List scheduled or event-based triggers.

| Trigger | Target | Schedule/event | Evidence | Confidence |
|---|---|---|---|---|
|  |  |  |  |  |

## Permissions and roles

List known permissions, roles or access relationships.

| Role/permission | Allows | Used by | Evidence | Confidence |
|---|---|---|---|---|
|  |  |  |  |  |

## Monitoring and operational relevance

List alarms, dashboards, logs, monitors or operational notes.

-

## Evidence

List all supporting evidence.

- Infra package path:
- Service catalogue template:
- Metadata file:
- Environment folder:
- Script:
- Resource definition:
- Parameter/export/import:
- Schedule/trigger:
- IAM/permission reference:
- Component reference:
- Flow reference:
- Runbook:
- Incident/Jira/Confluence reference:
- Engineer-supplied statement:
- Other:

## Suggested Atlas updates

Claude should consider whether this staging entry should update:

- `_curated/infra/...`
- `_curated/maps/infra-dependency-map.json`
- `_curated/maps/flow-component-map.json`
- `_curated/components/...`
- `_curated/runbooks/...`
- `_curated/incidents/learnings/...`

## Open questions

- Which package files need confirmation?
- Which resources need confirmation?
- Which dependencies are inferred rather than explicit?
- Which components use these resources?
- Which flows depend on these resources?
- Are environment differences relevant?
- Are any permissions, schedules or monitors missing?

## Do not curate as fact unless reviewed

List claims that are plausible but not confirmed.

-

---

## Runbooks README

<!-- Source: runbooks_readme_extracted.md -->

## `_staging/runbooks/`

### Purpose

`_staging/runbooks/` captures raw, untrusted operational guidance that may become or update a curated Atlas runbook.

Use this folder when the knowledge is mainly about how to investigate, recover, validate or escalate an operational problem.

A runbook entry should help answer:

> When this symptom occurs, what should an engineer check, in what order,
> and what evidence supports those steps?

### When to use this folder

Use `_staging/runbooks/` for:

- draft operational procedures;
- updates to existing runbooks;
- incident-derived investigation steps;
- mock incident recovery steps;
- common failure modes;
- logs, dashboards or checks useful during triage;
- escalation guidance;
- validation steps after recovery;
- runbook gaps discovered during code or incident work.

### When not to use this folder

Do not use this folder for:

- incident narrative or learning; use `_staging/incidents/`;
- a single MR/code change; use `_staging/changes/`;
- an end-to-end flow description; use `_staging/flows/`;
- component onboarding; use `_staging/components/`;
- infra package discovery; use `_staging/infra/`;
- general coding standards; use `_staging/standards/`.

### Operating rule

A staged runbook should be practical and evidence-linked.

Do not include dangerous production execution steps unless they are already approved operational guidance.
If a step needs caution, mark it clearly as requiring reviewer confirmation.

A staged runbook may result in:

1. creation or update of `_curated/runbooks/`;
2. links from flow pages;
3. links from component pages;
4. links from incident learnings;
5. reviewer decision that more evidence or operational approval is needed.

### Trust rule

Files in `_staging/runbooks/` are raw guidance, not approved operational procedure.

A runbook only becomes trusted when the corresponding `_curated/runbooks/` update is reviewed and approved through GitLab.

### Required filename format

Use:

```text
YYYY-MM-DD-runbook-<short-topic>.md
```

Examples:

```text
2026-07-30-runbook-stale-trade-data.md
2026-07-30-runbook-kafka-lag-investigation.md
2026-07-30-runbook-pricing-refresh-failure.md
```

### Required frontmatter

```yaml
type: atlas.staging.runbook
title: ""
description: ""
resource: ""
tags: []
timestamp: YYYY-MM-DD
atlas_id: STG-YYYY-NNNN
status: new
confidence: raw-unreviewed
source_type: incident | mock-incident | repo | confluence | jira | teams | email
  | engineer-note | claude-investigation
source_link: ""
runbook_type: investigation | recovery | validation | escalation | checklist | unknown
related_flows: []
related_components: []
related_infra_templates: []
related_incident_learnings: []
intended_curated_targets: []
```

### Evidence expectations

A useful staged runbook should include:

- symptom or trigger;
- when to use the runbook;
- investigation steps;
- checks, logs or dashboards;
- relevant components;
- relevant flows;
- relevant infra resources;
- escalation path or owner link if known;
- validation steps;
- evidence for any operational claims.

### Claude instructions

When curating from this folder, Claude should:

1. identify the operational scenario;
2. separate investigation, recovery, validation and escalation steps;
3. link relevant flows, components, infra and incident learnings;
4. preserve cautions and unresolved questions;
5. avoid inventing production commands;
6. mark unapproved or risky steps for reviewer confirmation;
7. propose updates only to relevant curated runbooks and linked pages.

### Reviewer checklist

Before approving a curated runbook update, check:

- Is the symptom or trigger clear?
- Are steps safe and appropriate?
- Are risky steps clearly marked or removed?
- Are commands/checks evidence-backed?
- Are related flows/components/infra correct?
- Does this duplicate an existing runbook?
- Are escalation and validation steps clear?
- Should this remain staged until operational approval is provided?
