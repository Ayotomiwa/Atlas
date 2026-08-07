---
id: STG-YYYYMMDD-<slug>
type: atlas.staging.change
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
repositories: []
local_paths: []
mrs: []
commits: []
change_scope: unknown
change_type: []
---

# Change evidence: <logical change>

> Capture reusable context discovered through the change, not a delivery diary. Keep observed facts separate from possible impact.

## Summary

Describe the logical change, why this evidence is worth keeping, and the boundary of the investigation.

### What changed

- Behaviour/contract/configuration change:
- Repositories/paths:
- Relevant MR/PR/commit/release references:

### Why it matters to Atlas

Explain which durable engineering context may need review: component, flow, infra, schema, runbook, standard, incident learning or relationship.

## Evidence

List exact attributable sources.

- Repository/path:
- Diff/commit/MR/PR:
- Test/build evidence:
- Config/schema/contract:
- Documentation/Jira/Confluence reference:
- Engineer/user-confirmed statement:
- Other:

## What is known

Record only observed or explicitly confirmed findings.

| Finding | Scope | Source | State (`observed` / `user-confirmed`) |
|---|---|---|---|
| | | | |

### Changed contracts/dependencies

| Change | Kind | Before | After | Evidence |
|---|---|---|---|---|
| | api/event/table/file/job/library/infra/config/other | | | |

## What is possible / unconfirmed

Capture suspected downstream effects, compatibility concerns or relationships that still require evidence.

| Possible effect/relationship | Why plausible | Evidence needed |
|---|---|---|
| | | |

Do not equate absence from the current investigation with "not affected".

## Suggested curated targets

List only plausible durable targets supported by this evidence, for example:

- `_curated/components/...`
- `_curated/flows/...`
- `_curated/infra/...`
- `_curated/schema-info/...`
- `_curated/runbooks/...`
- `_curated/standards/...`
- `_curated/incidents/...`
- relationship updates that will regenerate maps

## Open questions

- Which consumers or dependencies still need confirmation?
- Is the observed behaviour intended and durable?
- Does this change alter a flow boundary or only one component?
- Are schema/compatibility implications known?
- Is there related infra outside the inspected repository?
- Which findings are one-off delivery detail and should **not** be curated?
