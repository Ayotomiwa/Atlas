---
id: comp.<stable-name>
type: component
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
component_type: unknown
repository: repo.<stable-name>
repository_paths: []
parent_component: null
consumes: []
# - id: schema.example-input
#   asset_type: schema
#   confidence: reviewed
#   evidence: [path/to/consumer]
produces: []
depends_on: []
# - id: comp.shared-parser
#   dependency_type: component
#   confidence: possible
#   note: Why this remains possible.
uses_resources: []
reads_from: []
# - id: resource.example-bucket
#   confidence: reviewed
#   evidence: [path/to/config]
writes_to: []
triggers: []
scheduled_by: []
deployed_by: []
monitored_by: []
runbooks: []
standards: []
incident_learnings: []
evidence: []
conflicts: [] # omit when no evidenced conflict exists
coverage:
  level: unknown
  notes: []
---

# Component: <component name>

## Summary

State what the component does, where it fits, and why an engineer would look it up. Use plain technical language before Atlas terminology.

## Responsibility and boundary

State evidenced responsibilities and explicit non-responsibilities. Explain the independent runtime or reuse boundary instead of relying on a folder name.

## Source location and entrypoints

Explain the relevant repository paths and important code/configuration entrypoints.

## Code architecture summary

Explain the causal path from entry or trigger through material work and state changes to outputs, failure, and observable completion. Do not narrate every function or turn file adjacency into causality.

## Structured routing

<!-- atlas:generated-component-routing:start -->
| Field | Target | Qualifier/action | Confidence | Evidence |
|---|---|---|---|---|
| — | No structured routing facts captured | — | — | — |
<!-- atlas:generated-component-routing:end -->

## Internal units

Keep implementation details here unless a child is independently addressable and qualifies for its own `comp.*` page.

## Configuration and deployment context

Capture durable configuration concepts and deployment boundaries; route to infrastructure pages for resource detail.

## Failure and operational context

Record evidenced failure modes, observable symptoms, monitoring routes and support boundaries without copying sensitive logs.

## Diagram

Add reviewed Mermaid only when one view of roughly three to eight meaningful nodes materially clarifies an internal boundary or control path. Keep the structured routing table and prose as the accessible fallback. Do not infer an edge for visual completeness.

<!-- atlas:generated-related-routes:start -->
## Related Atlas routes

_No resolved direct Atlas routes._
<!-- atlas:generated-related-routes:end -->

## Evidence

List staging, repository, configuration and reviewer-confirmed sources.

## Open questions / coverage limits

| Question ID | Question | Affected IDs | Evidence gap |
|---|---|---|---|
| missing-consumer | Which downstream consumer is confirmed? | `comp.<stable-name>` | No consumer evidence reviewed. |
