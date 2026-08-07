---
id: STG-YYYYMMDD-<slug>
type: atlas.staging.infra
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

# Infrastructure evidence: <package or topic>

## Summary

Identify the infrastructure package/resource context and why this evidence is reusable.

## Evidence

Capture exact IaC/config references where available.

- Package/path:
- Template/IaC file:
- Environment config:
- Resource/logical ID:
- Parameter/import/export:
- Schedule/trigger:
- IAM/monitoring reference:
- Other:

## What is known

Record observed or user-confirmed package structure, resources and relationships.

| Finding | Source | State |
|---|---|---|
| | | observed/user-confirmed |

Include component/flow usage only when supported by evidence.

## What is possible / unconfirmed

| Possible relationship/resource significance | Why plausible | Evidence needed |
|---|---|---|
| | | |

Do not assume every resource should become a promoted impact-analysis node.

## Suggested curated targets

List only supported targets such as `_curated/infra/`, linked component/flow pages or infra relationships that will regenerate the infra dependency map.

- 

## Open questions

- Is the package boundary correct?
- Which environment differences matter?
- Which resources are shared/operationally significant?
- Which components/flows actually use them?
- Which permissions, triggers or monitors remain unverified?
- Which resources, if any, merit promotion for impact analysis?
