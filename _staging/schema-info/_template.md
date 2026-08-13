---
id: STG-YYYYMMDD-<slug>
type: staging.schema-info
package: datalens
timestamp: YYYY-MM-DD
title: ""
description: ""
status: new
captured_by: ""
source_type: ""
---

# Schema evidence: <asset or contract>

## Summary

Describe what contract/asset was investigated, where it was found and why the evidence may be reusable.

### Asset identity and location

| Item | Observed value | Source |
|---|---|---|
| Physical name/topic/path/endpoint | | |
| Asset type | | |
| Platform/system | | |
| Repository/schema path | | |

### Contract meaning and lifecycle

Explain what one record/message/request represents, when and why it is produced, how a known consumer uses it, and how versioning, mutation, retention or latest-record behavior affects compatibility. Separate physical observation from business interpretation and cite each material assertion.

- Boundary purpose:
- Production/consumption lifecycle:
- Identity, grain and temporal behavior:
- Compatibility/migration significance:
- Unknown or inaccessible lifecycle context:

## Evidence

- Schema/DDL/IDL/API definition:
- Migration/configuration:
- Producer code:
- Consumer code:
- Documentation/catalogue:
- Engineer/SME-supplied statement:
- Other:

## What is known

Capture only observed or explicitly user-confirmed facts.

### Grain and keys

| Finding | Value | Source | State |
|---|---|---|---|
| Grain | | | observed/user-confirmed |
| Primary key candidate | | | |
| Business key candidate | | | |
| Temporal/latest-record behaviour | | | |

### Important fields / quality

| Field or rule | Observed meaning/constraint | Source | State |
|---|---|---|---|
| | | | |

### Compatibility / versioning

| Version/change | Observed compatibility or breaking risk | Migration/consumer evidence | State |
|---|---|---|---|
| | | | observed/user-confirmed |

### Known producers and consumers

| Direction | Component/system | Evidence | State |
|---|---|---|---|
| producer/consumer | | | |

### Observed joins

| Other asset | Keys/condition | Where observed | What is actually known |
|---|---|---|---|
| | | | |

## What is possible / unconfirmed

Record semantic interpretations, key assumptions, consumers or joins that still need review.

| Possible finding | Why plausible | Evidence/reviewer needed |
|---|---|---|
| | | |

## Suggested curated targets

- `_curated/schema-info/...`
- related `_curated/components/...`
- related `_curated/flows/...`
- related `_curated/business-concepts/...`
- related `_curated/standards/...`

Only list targets the evidence can actually support.

## Open questions

- What exactly does one record/message represent?
- Are keys unique for the stated grain?
- What is the temporal/version/latest-record rule?
- Which producers/consumers are confirmed versus inferred?
- Are observed joins approved and grain-safe?
- What classification/access restrictions matter?
- Which versions/environments were not inspected?
