---
id: repo.<stable-name>
type: repository
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
repository_locator: ""
repository_root: "."
repository_type: unknown
default_branch: ""
parent_repository: null
source_roots: []
# - path: src/example
#   purpose: Concise source responsibility.
#   evidence: [path/to/source]
depends_on_repositories: []
# - id: repo.shared-build
#   dependency_type: shared-tooling
#   confidence: reviewed
#   evidence: [path/to/build-config]
runbooks: []
standards: []
incident_learnings: []
evidence: []
conflicts: [] # omit when no evidenced conflict exists
coverage:
  level: unknown
  notes: []
---

# Repository: <repository name>

## Summary and boundary

In plain technical prose, state what this source boundary contains, why it is independently useful, and what is explicitly outside it. Lead with what an engineer can find here.

## Source topology

<!-- atlas:generated-source-roots:start -->
| Source root | Purpose | Evidence |
|---|---|---|
| — | No source roots captured | — |
<!-- atlas:generated-source-roots:end -->

Explain meaningful physical-monorepo, logical-project or nested-project structure that the compact table cannot convey. `repository_root` is relative to the physical Git root.

## Code architecture summary

Explain how an engineer moves from the important entrypoints through the main source areas. Connect each root to its responsibility without narrating individual functions or inferring runtime behavior.

## Architecture routes

Link important component, flow, infrastructure and schema pages. Contained components are derived from their `repository` fields.

## Source-owned guidance

Route to durable repository documentation for setup, build, test, deployment and local agent instructions. Do not copy exact commands into Atlas.

## Ownership and operational context

Record evidenced ownership, support boundaries and stable operational context.

<!-- atlas:generated-related-routes:start -->
## Related Atlas routes

_No resolved direct Atlas routes._
<!-- atlas:generated-related-routes:end -->

## Evidence

List the staging records and source references supporting material claims.

## Open questions / coverage limits

| Question ID | Question | Affected IDs | Evidence gap |
|---|---|---|---|
| boundary-owner | Who confirms this repository boundary? | `repo.<stable-name>` | No reviewed ownership source. |
