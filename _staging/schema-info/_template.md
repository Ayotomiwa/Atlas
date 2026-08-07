---
id: STG-YYYYMMDD-<slug>
type: atlas.staging.schema-info
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
asset_name: ""
asset_kind: unknown
repository: ""
source_path: ""
platform: ""
classification: unknown
---

# Schema evidence: <asset or contract>

## Summary

Describe what contract/asset was investigated, where it was found and why the evidence may be reusable.

### Asset identity and location

| Item | Observed value | Source |
|---|---|---|
| Physical name/topic/path/endpoint | | |
| Asset kind | | |
| Platform/system | | |
| Repository/schema path | | |

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

### Important fields / compatibility / quality

| Field or rule | Observed meaning/constraint | Source | State |
|---|---|---|---|
| | | | |

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
