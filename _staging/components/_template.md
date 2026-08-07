---
id: STG-YYYYMMDD-<slug>
type: atlas.staging.component
package: teama
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

# Component evidence: <component or repository>

> Capture attributable discovery, not a polished component page. Keep observed/user-confirmed facts separate from possible relationships and do not create linked evidence files solely to make this record look complete.

## Summary

Describe why this evidence was captured, which component/repository it concerns, and the investigation boundary.

### Component identity and location

- Component name:
- Observed type/scope:
- Repository:
- Monorepo path:
- Main README / local `CLAUDE.md`:
- Build/dependency file:
- Important source/config/schema paths:

### Responsibility / boundary

State the directly observed or user-confirmed responsibility. Record unclear boundaries under `What is possible / unconfirmed` or `Open questions`.

## Evidence

List attributable sources. Prefer exact paths and references.

- Repository/path:
- README/docs:
- Build/dependency metadata:
- Code/config path:
- Schema/API/event/data-contract path:
- Infra/template path:
- Scheduler/workflow definition:
- Runbook/operational reference:
- Jira/Confluence/other authorised reference:
- Engineer/user-confirmed statement:
- Other:

## What is known

Record only observed or explicitly user-confirmed facts.

### Internal units

Use this for lower-level artefacts that belong inside the component rather than automatically creating first-class component records.

| Unit | Type | Purpose/role | Path | Source | State |
|---|---|---|---|---|---|
| | | | | | observed/user-confirmed |

### Consumes

| Kind | Name/target | From/source | Evidence | State |
|---|---|---|---|---|
| api/event/table/file/config/library/job-output/other | | | | observed/user-confirmed |

### Produces

| Kind | Name/target | Known consumer/use | Evidence | State |
|---|---|---|---|---|
| api/event/table/file/log/alert/job-output/other | | | | observed/user-confirmed |

### Related flows

| Flow/candidate flow | Role in flow | Evidence | State |
|---|---|---|---|
| | | | observed/user-confirmed |

Do not manufacture a complete flow from one component's local evidence. Stage `_staging/flows/` only when an end-to-end boundary is supported.

### Related infrastructure

| Package/resource | Relationship to component | Evidence | State |
|---|---|---|---|
| | | | observed/user-confirmed |

### Local repository references

Prefer durable references over copied commands that may drift.

- Local README/build guidance:
- Test guidance:
- Runtime/deployment guidance:
- Other stable reference:

### Operational notes

Capture stable evidence such as monitoring references, alerts, common failure signals or support boundaries. Do not copy sensitive logs.

- 

### Runbooks, standards and incident learnings

- Runbook evidence/reference:
- Standard/convention evidence/reference:
- Incident/near-miss learning reference:

### Other known findings

| Finding | Source | State (`observed` / `user-confirmed`) |
|---|---|---|
| | | |

## What is possible / unconfirmed

Keep inference visibly separate from known facts.

| Possible finding/relationship | Why plausible | Evidence needed |
|---|---|---|
| | | |

Examples include a suspected consumer, possible flow participation, likely infra relationship or inferred responsibility boundary. Do not convert these into authoritative relationships.

## Suggested curated targets

List only targets supported by the evidence, for example:

- `_curated/components/...`
- related `_curated/flows/...`
- related `_curated/infra/...`
- related `_curated/schema-info/...`
- related `_curated/runbooks/...`
- related `_curated/standards/...`
- related `_curated/incidents/...`
- relationship updates that will regenerate the appropriate maps

## Open questions

- What responsibility or boundary still needs confirmation?
- Which inputs/outputs or consumers/producers are uncertain?
- Which internal units are operationally meaningful versus implementation detail?
- Is a related flow boundary actually evidenced?
- Is relevant infrastructure in another supplied location?
- Which operational references or failure signals are missing?
- Which standard-looking patterns are team policy versus repo-local/tool defaults?
- What context is inaccessible or uninvestigated?
