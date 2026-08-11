---
id: STG-YYYYMMDD-<slug>
type: staging.incident
package: datalens
timestamp: YYYY-MM-DD
title: ""
description: ""
status: new
captured_by: ""
source_type: ""
---

# Incident evidence: <sanitised incident / near miss / exercise>

> Capture reusable engineering learning only. Link to the authoritative incident record and remove sensitive detail. This is not a replacement incident-management record.

## Summary

Provide a sanitised description of the event and why it may change Atlas knowledge.

### Observed impact / timeline anchors

Record only the minimal timeline points needed to understand impact, detection, cause or recovery.

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

### Impact

| Observed impact | Affected component/flow/resource | Evidence | State |
|---|---|---|---|
| | | | observed/user-confirmed |

### Detection

| Signal/observation | What it revealed | Evidence | State |
|---|---|---|---|
| | | | observed/user-confirmed |

### Diagnostic aids

| Signal/query/dashboard/log pattern | How it helped | Limitations | Evidence |
|---|---|---|---|
| | | | |

### Discovery friction / missing context

| Missing or hard-to-find context | Effect on diagnosis/recovery | Where it should live | Evidence |
|---|---|---|---|
| | | | |

### Confirmed cause

Record a cause here only when evidence or an authorised/user-confirmed source identifies it as confirmed.

| Cause finding | Evidence | State |
|---|---|---|
| | | observed/user-confirmed |

### Recovery actually performed

| Recovery action | Outcome | Evidence | State |
|---|---|---|---|
| | | | observed/user-confirmed |

Recovery observations are not automatically an approved runbook.

### Reusable gaps / learnings

| Learning/gap | Type | Why reusable | Evidence |
|---|---|---|---|
| | dependency/flow/infra/runbook/monitoring/standard/other | | |

### Other known findings

| Finding | Category | Source | State |
|---|---|---|---|
| | impact/detection/cause/recovery/dependency/gap | | observed/user-confirmed |

## What is possible / unconfirmed

| Possible finding | Why plausible | Evidence needed |
|---|---|---|
| | | |

Keep suspected cause, possible blast radius and uncertain dependencies here until reviewed. Do not present plausible causality as established fact.

## Suggested curated targets

- `_curated/incidents/...`
- `_curated/runbooks/...`
- `_curated/flows/...`
- `_curated/components/...`
- `_curated/infra/...`
- `_curated/standards/...`
- connection-field updates that regenerate maps

## Open questions

- Is the root/technical cause confirmed or still suspected?
- Which affected components/flows/resources are proven?
- Which impact is known versus possible?
- What detection/monitoring gap is reusable?
- Which dependency or flow relationship was difficult to establish during triage?
- Which recovery steps deserve a reviewed runbook update?
- Which standard/process gap needs separate evidence?
- Has all sensitive material been removed from this staging record?
