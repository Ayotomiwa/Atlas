---
id: infra.<stable-name>
type: infra
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
conflicts: [] # omit when no evidenced conflict exists
coverage:
  level: unknown
  notes: []
---

# Infrastructure: <package name>

## Summary and boundary

State what the infrastructure package creates or configures, who uses it when evidenced, and why the boundary matters. Do not promote every resource.

## Package location and environment structure

Explain repository/package paths and environment differences that affect behavior, operation or risk.

## Structured infrastructure routing

<!-- atlas:generated-infra-routing:start -->
| Record/field | Target or resource | Type/action | Confidence | Evidence |
|---|---|---|---|---|
| — | No structured infrastructure facts captured | — | — | — |
<!-- atlas:generated-infra-routing:end -->

## Ordinary resources

Describe ordinary resources in prose or concise tables, including their role when known. They do not need a stable map identity or proof that every promotion criterion fails.

## Promoted-resource rationale

For each promoted resource, name the evidenced criterion that justifies independent routing or impact identity. Keep uncertain significance as a coverage gap rather than promoting by guesswork.

## Permissions, monitoring and operational context

Record meaningful access, monitoring, trigger and operational context without secrets or copied logs.

## Impact context

Explain known, possible and unknown effects without duplicating generated reverse users.

<!-- atlas:generated-related-routes:start -->
## Related Atlas routes

_No resolved direct Atlas routes._
<!-- atlas:generated-related-routes:end -->

## Evidence

List infrastructure, repository and reviewer-confirmed evidence.

## Open questions / coverage limits

| Question ID | Question | Affected IDs | Evidence gap |
|---|---|---|---|
| unknown-user | Which additional user remains unconfirmed? | `infra.<stable-name>` | No reviewed consumer evidence. |
