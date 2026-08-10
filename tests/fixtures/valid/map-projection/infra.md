---
id: atlas-infra.fixture.stack
type: atlas.infra
package: fixtures
schema_version: atlas/1.0
status: curated
last_reviewed: '2026-08-07'
reviewed_by:
- fixture-reviewer
owners: []
routing:
  aliases: []
  domains: []
relationships:
- type: atlas.participates-in
  target: atlas-flow.fixture.flow
  role: storage
  sequence: 2
  confidence: reviewed
  evidence:
  - fixture://infra-flow
- type: atlas.depends-on
  target: atlas-resource.fixture.shared-bucket
  kind: infra-resource
  confidence: reviewed
  evidence:
  - fixture://package-resource
evidence:
- fixture://reviewed-source
coverage:
  level: good
  notes:
  - Synthetic test fixture.
title: Fixture infra
description: Synthetic test fixture only.
infra_package: fixture-infra
template_path: main.tf
resource_names:
- fixture-resource
environments:
- test
promoted_resources:
- id: atlas-resource.fixture.shared-bucket
  name: Fixture shared bucket
  resource_type: s3-bucket
  defined_in_path: main.tf
  environments: [test]
  promotion_reason: Shared data-bearing fixture resource.
  confidence: reviewed
  coverage:
    level: good
    notes: [Synthetic fixture.]
  evidence: [fixture://shared-bucket]
  relationships:
  - type: atlas.depends-on
    target: atlas-resource.fixture.queue
    kind: infra-resource
    confidence: reviewed
    evidence: [fixture://resource-dependency]
  - type: atlas.triggers
    target: atlas-flow.fixture.flow
    kind: event
    confidence: reviewed
    evidence: [fixture://resource-trigger]
  - type: atlas.permission-allows
    target: atlas-comp.fixture.component
    kind: permission
    confidence: reviewed
    evidence: [fixture://resource-permission]
  - type: atlas.monitored-by
    target: atlas-resource.fixture.queue
    kind: monitoring
    confidence: reviewed
    evidence: [fixture://resource-monitor]
- id: atlas-resource.fixture.queue
  name: Fixture queue
  resource_type: sqs-queue
  defined_in_path: main.tf
  environments: [test]
  promotion_reason: Orchestration-critical fixture resource.
  confidence: reviewed
  coverage:
    level: partial
    notes: [Synthetic fixture.]
  evidence: [fixture://queue]
  relationships: []
---

## Summary

Synthetic fixture content.

## Package location and structure

Synthetic fixture content.

## Environment notes

Synthetic fixture content.

## Internal resources

Synthetic fixture content.

## Promoted resources and promotion reason

Synthetic fixture content.

## Resource relationships

Synthetic fixture content.

## Components using resources

Synthetic fixture content.

## Flows using resources

Synthetic fixture content.

## Parameters/imports/exports

Synthetic fixture content.

## Schedules/triggers/events

Synthetic fixture content.

## Permissions and roles

Synthetic fixture content.

## Monitoring

Synthetic fixture content.

## Impact if changed or deleted

Synthetic fixture content.

## Evidence

Synthetic fixture content.

## Possible relationships

Synthetic fixture content.

## Open questions / coverage limits

Synthetic fixture content.
