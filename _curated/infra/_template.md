---
id: infra.<stable-name>
type: infra
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
infra_package: ""
repository: null
package_path: ""
template_path: ""
environments: []
depends_on: []
uses_resources: []
reads_from: []
writes_to: []
triggers: []
scheduled_by: []
imports_values: []
exports_values: []
permissions: []
monitored_by: []
deployed_by: []
promoted_resources: []
# - id: resource.<stable-name>
#   name: ""
#   resource_type: other
#   defined_in_path: ""
#   environments: []
#   promotion_reason: ""
#   confidence: reviewed
#   coverage: {level: unknown, notes: []}
#   evidence: []
#   depends_on: []
#   uses_resources: []
#   reads_from: []
#   writes_to: []
#   triggers: []
#   scheduled_by: []
#   imports_values: []
#   exports_values: []
#   permissions: []
#   monitored_by: []
#   deployed_by: []
#   runbooks: []
#   standards: []
#   incident_learnings: []
runbooks: []
standards: []
incident_learnings: []
evidence: []
coverage:
  level: unknown
  notes: []
---

# Infrastructure: <package name>

## Summary and boundary

Describe the meaningful infrastructure package and why it matters. Do not promote every resource.

## Package location and environment structure

Explain repository/package paths and environment differences that affect behavior, operation or risk.

## Structured infrastructure routing

<!-- atlas:generated-infra-routing:start -->
| Record/field | Target or resource | Type/action | Confidence | Evidence |
|---|---|---|---|---|
| — | No structured infrastructure facts captured | — | — | — |
<!-- atlas:generated-infra-routing:end -->

## Ordinary resources

Describe unpromoted resources in prose or concise tables. They do not receive stable map identity.

## Promoted-resource rationale

Explain why each promoted resource deserves independent routing and impact identity.

## Permissions, monitoring and operational context

Record meaningful access, monitoring, trigger and operational context without secrets or copied logs.

## Impact context

Explain known, possible and unknown effects without duplicating generated reverse users.

## Evidence

List infrastructure, repository and reviewer-confirmed evidence.

## Open questions / coverage limits

| Question ID | Question | Affected IDs | Evidence gap |
|---|---|---|---|
| unknown-user | Which additional user remains unconfirmed? | `infra.<stable-name>` | No reviewed consumer evidence. |
