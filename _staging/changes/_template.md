---
id: STG-YYYYMMDD-<slug>
type: staging.change
package: datalens
timestamp: YYYY-MM-DD
title: ""
description: ""
status: new
captured_by: ""
source_type: ""
---

# Change evidence: <logical change>

> Capture reusable context discovered through the change, not a delivery diary. For code-derived changes, prefer the merged/default-branch state. MR/PR references are provenance, not the staging boundary.

## Summary

Describe the logical change, why this evidence is worth keeping, and the boundary of the investigation.

### Change context

- What changed:
- Why the change was made:
- Repositories/local paths:
- Final/default-branch state inspected:
- Relevant merged MR/PR/commit/release references (if any):
- Material changed files/config/contracts:
- If multiple MRs/PRs are grouped, why they form one logical change:
- If one broad MR/PR was split, what independent boundary this record owns:

### Atlas relevance

Choose one: `yes`, `no`, `unknown`.

Explain whether the change reveals or modifies reusable component, flow, dependency, infrastructure, schema, runbook, standard or incident context.

### Change classification

Select only what evidence supports:

- [ ] API changed
- [ ] Event/schema changed
- [ ] Table/data/file output changed
- [ ] Job schedule/dependency changed
- [ ] Shared library dependency changed
- [ ] Infrastructure/template/resource reference changed
- [ ] Runtime behaviour changed
- [ ] Runbook/recovery process changed
- [ ] Standard/convention evidence changed
- [ ] Incident fix/operational learning
- [ ] Documentation-only change
- [ ] Unknown

## Evidence

List exact attributable sources.

- Repository/path:
- Merged diff/commit/MR/PR (if applicable):
- Changed file:
- Test/build evidence:
- API/schema/event/data-contract:
- Config/infra/template:
- Jira/change/incident reference:
- Documentation reference:
- Engineer/user-confirmed statement:
- Other:

## What is known

Record only observed or explicitly confirmed findings.

| Finding | Scope | Source | State (`observed` / `user-confirmed`) |
|---|---|---|---|
| | | | |

### Dependency and contract impact

#### New dependencies

List evidence-backed dependencies introduced by the logical change.

| Dependency | Kind | Consumer | Evidence |
|---|---|---|---|
| | | | |

#### Removed dependencies

| Dependency | Kind | Previous consumer/use | Evidence |
|---|---|---|---|
| | | | |

#### Changed contracts/configuration

| Change | Kind | Before | After | Evidence |
|---|---|---|---|---|
| | api/event/table/file/job/library/infra/config/other | | | |

#### Compatibility and migration

| Breaking risk | Consumers verified | Migration needed | Rollback/compatibility path | Evidence |
|---|---|---|---|---|
| unknown | | | | |

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
- connection-field updates that will regenerate the appropriate maps

Do not list generated JSON maps as authoring targets; curated Markdown fields are the source of truth.

## Open questions

- Which consumers or dependencies still need confirmation?
- Is the observed behaviour intended and durable?
- Does this change alter a flow boundary or only one component?
- Are schema/compatibility implications known?
- Is there related infra outside the inspected repository?
- Are tests or compatibility checks still outstanding?
- Which findings are one-off delivery detail and should **not** be curated?
