---
id: STG-YYYYMMDD-<slug>
type: atlas.staging.incident
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
incident_type: unknown
severity: unknown
occurred_at: ""
related_flows: []
related_components: []
related_infra: []
---

# Incident evidence: <sanitised incident / near miss / exercise>

> Capture reusable engineering learning only. Link to the authoritative incident record and remove sensitive detail.

## Summary

Provide a sanitised description of the event and why it may change Atlas knowledge.

### Observed impact / timeline anchors

Record only the minimal timeline points needed to understand cause, detection or recovery.

| Time/phase | Observation | Evidence |
|---|---|---|
| | | |

## Evidence

- Authorised incident record:
- Mock/exercise notes:
- Jira/change reference:
- Monitoring/log/dashboard reference:
- Repository/config path:
- Infra/template reference:
- Runbook:
- Engineer/user-confirmed statement:
- Other:

## What is known

| Finding | Category | Source | State |
|---|---|---|---|
| | impact/detection/cause/recovery/dependency/gap | | observed/user-confirmed |

Keep confirmed cause separate from suspected cause. Record recovery steps as observations, not automatically as an approved runbook.

## What is possible / unconfirmed

| Possible finding | Why plausible | Evidence needed |
|---|---|---|
| | | |

Include suspected cause, possible blast radius and uncertain dependencies here until reviewed.

## Suggested curated targets

- `_curated/incidents/...`
- `_curated/runbooks/...`
- `_curated/flows/...`
- `_curated/components/...`
- `_curated/infra/...`
- `_curated/standards/...`
- relationship updates that regenerate maps

## Open questions

- Is the root/technical cause confirmed?
- Which affected components/flows/resources are proven?
- Which impact is known versus possible?
- What detection/monitoring gap is reusable?
- Which recovery steps deserve a reviewed runbook update?
- Which standard/process gap needs separate evidence?
- Has all sensitive material been removed from this staging record?
