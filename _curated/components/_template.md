---
id: comp.<stable-name>
type: component
package: teama
schema_version: atlas/1.0
title: ""
description: ""
status: curated
last_reviewed: YYYY-MM-DD
reviewed_by: []
owners: []
routing:
  aliases: []
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
coverage:
  level: unknown
  notes: []
---

# Component: <component name>

## Summary

Describe what the component is, where it fits, and why an engineer would care.

## Responsibility and boundary

State evidenced responsibilities, explicit non-responsibilities and whether this is an independently addressable architectural unit.

## Source location and entrypoints

Explain the relevant repository paths and important code/configuration entrypoints.

## Code architecture summary

Describe important control flow and implementation structure without function-by-function narration.

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

Add reviewed Mermaid only when it materially clarifies internal structure or boundaries.

## Evidence

List staging, repository, configuration and reviewer-confirmed sources.

## Open questions / coverage limits

| Question ID | Question | Affected IDs | Evidence gap |
|---|---|---|---|
| missing-consumer | Which downstream consumer is confirmed? | `comp.<stable-name>` | No consumer evidence reviewed. |
