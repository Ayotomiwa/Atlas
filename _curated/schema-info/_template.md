---
id: schema.<stable-name>
type: schema-info
package: datalens
schema_version: atlas/1.0
title: ""
description: ""
status: curated
last_reviewed: YYYY-MM-DD
reviewed_by: []
owners: []
routing:
  aliases: []
  keywords: []
primary_domain: ""
related_domains: []
assets: []
# - id: asset.example.output
#   name: example_output
#   asset_type: table
#   physical_name: example_output
#   description: ""
#   confidence: reviewed
#   evidence: [path/to/model.sql]
#   inputs:
#     - id: asset.example.input
#       confidence: reviewed
#       evidence: [path/to/model.sql]
#       note: ""
links: []
evidence: []
conflicts: [] # omit when no evidenced conflict exists
coverage:
  level: unknown
  notes: []
asset_type: unknown
physical_name: ""
platform: ""
temporal_model: unknown
classification: ""
---

# Schema info: <asset or contract name>

> Describe the durable contract and its reviewed semantics. Do not infer business meaning, joins or consumers from field names alone. Remove authoring guidance as sections are completed.

## Summary

Explain what the asset/contract is, where it lives and why engineers use it.

*Not covered — no evidence in current staging material.*

## Business meaning

State the reviewed meaning of the asset and what a record/message/document represents. Link a curated business concept when one exists rather than duplicating its definition.

*Not covered — no evidence in current staging material.*

## Physical identity

| Item | Value | Evidence |
|---|---|---|
| Asset type | | |
| Physical name/topic/path/endpoint | | |
| Platform/system | | |
| Repository/schema definition | | |
| Version/compatibility marker | | |

*Not covered — no evidence in current staging material.*

## Grain

Describe exactly what one row, event, file record, API representation or message instance represents. Note whether multiple records can exist for the same business entity and why.

*Not covered — no evidence in current staging material.*

## Keys

| Key | Type | Purpose/uniqueness | Evidence |
|---|---|---|---|
| | primary/business/natural/composite | | |

Do not call a field a key solely because its name looks like an identifier.

*Not covered — no evidence in current staging material.*

## Temporal model

Explain append/update/version/snapshot behaviour, effective dates, event time versus processing time and the reviewed latest-record rule where relevant.

*Not covered — no evidence in current staging material.*

## Compatibility / versioning

Describe version identifiers, compatibility guarantees, migration expectations, known breaking changes and consumer constraints. Keep unverified compatibility assumptions explicit.

| Version/change | Compatibility or migration rule | Affected consumers | Evidence |
|---|---|---|---|
| | | | |

*Not covered — no evidence in current staging material.*

## Important fields

Document only fields whose meaning is reusable for engineering decisions; do not reproduce the entire schema unless that is genuinely the most useful representation.

| Field | Meaning | Constraints/notes | Evidence |
|---|---|---|---|
| | | | |

*Not covered — no evidence in current staging material.*

## Producers

| Producer | What it writes/emits | Relationship/evidence |
|---|---|---|
| | | |

*Not covered — no evidence in current staging material.*

## Consumers

| Consumer | How it uses the asset | Relationship/evidence |
|---|---|---|
| | | |

*Not covered — no evidence in current staging material.*

## Approved/known joins

Record only reviewed joins. Include both sides, keys, cardinality/grain assumptions and any temporal filter needed for correctness.

| Other asset | Join keys | Cardinality/grain assumption | Temporal/latest rule | Evidence |
|---|---|---|---|---|
| | | | | |

*Not covered — no evidence in current staging material.*

## Quality issues

Capture known reusable limitations such as lateness, duplication, nullability, backfill behaviour, compatibility caveats or incomplete historical coverage.

*Not covered — no evidence in current staging material.*

## Classification and access notes

Describe classification, broad access constraints and safe handling expectations without copying restricted values or credentials.

*Not covered — no evidence in current staging material.*

<!-- atlas:generated-related-routes:start -->
## Related Atlas routes

_No resolved direct Atlas routes._
<!-- atlas:generated-related-routes:end -->

## Evidence

List the evidence supporting material physical and semantic claims.

- Staging evidence:
- Schema/DDL/IDL/API definition:
- Producer/consumer code:
- Migration/configuration:
- Data catalogue/documentation:
- Reviewer-confirmed source:

*Not covered — no evidence in current staging material.*

## Open questions / coverage limits

Be explicit about unknown grain, keys, consumers, temporal rules, joins, quality behaviour, classification or uninvestigated versions/environments.

| Question ID | Question | Affected IDs | Evidence gap |
|---|---|---|---|
