---
id: repo.<stable-name>
type: repository
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
repository_locator: ""
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
coverage:
  level: unknown
  notes: []
---

# Repository: <repository name>

## Summary and boundary

Describe why the repository exists, what source boundary it represents, and what is explicitly outside it.

## Source topology

<!-- atlas:generated-source-roots:start -->
| Source root | Purpose | Evidence |
|---|---|---|
| — | No source roots captured | — |
<!-- atlas:generated-source-roots:end -->

Explain meaningful monorepo or nested-repository structure that the compact table cannot convey.

## Code architecture summary

Describe important entrypoints, control flow and source-root responsibilities without narrating individual functions.

## Architecture routes

Link important component, flow, infrastructure and schema pages. Contained components are derived from their `repository` fields.

## Source-owned guidance

Route to durable repository documentation for setup, build, test, deployment and local agent instructions. Do not copy exact commands into Atlas.

## Ownership and operational context

Record evidenced ownership, support boundaries and stable operational context.

## Evidence

List the staging records and source references supporting material claims.

## Open questions / coverage limits

| Question ID | Question | Affected IDs | Evidence gap |
|---|---|---|---|
| boundary-owner | Who confirms this repository boundary? | `repo.<stable-name>` | No reviewed ownership source. |
