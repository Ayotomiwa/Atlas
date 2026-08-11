---
id: flow.<stable-name>
type: flow
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
flow_scope: ""
diagram: false
entry_points: []
# - entry_point_type: schedule
#   name: Daily schedule
#   confidence: reviewed
#   evidence: [path/to/schedule]
inputs: []
outputs: []
upstream_flows: []
steps: []
# - step_id: extract
#   order: 10
#   name: Extract records
#   participant: {type: component, id: comp.extract-records, name: Extract records}
#   role: producer
#   confidence: reviewed
#   evidence: [path/to/extractor]
#   onboarding_question_id: add-extract-component # required only when component id is omitted
#   receives: []
#   emits:
#     - id: schema.raw-records
#       asset_type: schema
#       confidence: reviewed
#       evidence: [path/to/schema]
#   transitions:
#     - {to: validate, "on": success}
runbooks: []
standards: []
incident_learnings: []
evidence: []
conflicts: [] # omit when no evidenced conflict exists
coverage:
  level: unknown
  notes: []
---

# Flow: <flow name>

## Summary and boundary

Describe the end-to-end outcome, start, end, in-scope behavior and explicit exclusions.

## Entry points and boundary I/O

Explain material triggers and external boundary contracts. Exact values are authored in frontmatter.

## End-to-end steps

<!-- atlas:generated-steps-table:start -->
| Order | Step ID | Step | Participant | Type | Role | Receives | Emits | Transitions | Confidence |
|---:|---|---|---|---|---|---|---|---|---|
| — | — | No steps captured | — | — | — | — | — | — | — |
<!-- atlas:generated-steps-table:end -->

## Diagram

<!-- atlas:generated-flow-diagram:start -->
_No generated diagram requested._
<!-- atlas:generated-flow-diagram:end -->

## Failure and conditional paths

Explain branches, retries, partial completion and operational implications supported by evidence.

## Infrastructure and operational routes

Explain material infrastructure use and link relevant runbooks, monitoring and incident learnings.

<!-- atlas:generated-related-routes:start -->
## Related Atlas routes

_No resolved direct Atlas routes._
<!-- atlas:generated-related-routes:end -->

## Evidence

List sources for boundary, ordering, handoffs, participants and failure paths.

## Open questions / coverage limits

| Question ID | Question | Affected IDs | Evidence gap |
|---|---|---|---|
| missing-step | Which step or handoff remains unconfirmed? | `flow.<stable-name>` | Ordering evidence is incomplete. |
