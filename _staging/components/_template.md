---
id: STG-YYYYMMDD-<slug>
type: staging.component
package: teama
timestamp: YYYY-MM-DD
title: ""
description: ""
status: new
captured_by: ""
source_type: ""
---

# Repository and component discovery: <repository or service>

> Capture attributable evidence, not a polished architecture page. One record should preserve the repository scan and every candidate component that curation may later split.

## Summary

Explain why the scan was performed and what was found at a high level.

## Discovery boundary

- Accessible physical Git repository/checkout:
- Git locator or remote:
- Logical repository root relative to the Git root:
- Revision, branch or snapshot inspected:
- Paths included:
- Paths excluded or inaccessible:
- Related repositories or documentation not inspected:
- User-confirmed boundary statements:

## Repository evidence

### Identity, ownership and domain

| Attribute | Observed value | Evidence | State |
|---|---|---|---|
| Repository name | | | observed/user-confirmed |
| Physical Git locator or URL | | | observed/user-confirmed |
| Logical repository root | `.` or Git-relative path | | observed/user-confirmed |
| Boundary evidence | ownership/build/release/source/config/test/docs/child-product | | observed/user-confirmed/possible |
| Repository type | standalone/monorepo-root/monorepo-project/nested-project/mirror/other/unknown | | observed/user-confirmed |
| Enclosing repository candidate | | | observed/user-confirmed/possible |
| Default branch | | | observed/user-confirmed |
| Owner or SME | | | observed/user-confirmed/unknown |
| Candidate primary domain | | | observed/user-confirmed/possible |
| Related domains | | | observed/user-confirmed/possible |

### Repository topology and source dependencies

| Repository or source boundary | Relationship | Path/locator | Why it matters | Evidence | State |
|---|---|---|---|---|---|
| | parent/nested/submodule/generated-source/shared-tooling/shared-config/build/other | | | | observed/user-confirmed |

Keep repository-level source/build dependencies separate from runtime component dependencies.

### Important source roots

| Source root | Responsibility | Important entrypoints | Candidate component(s) | Evidence | State |
|---|---|---|---|---|---|
| | | | | | observed/user-confirmed |

### Source-owned guidance

| Purpose | Durable repository reference | Evidence/state |
|---|---|---|
| Setup/local development | | |
| Build/dependencies | | |
| Tests | | |
| Deployment/release | | |
| Local agent instructions | | |

## Candidate components

| Candidate | Suggested type | Responsibility | Independent boundary evidence | Parent candidate | Repository-relative paths | Candidate domain | State |
|---|---|---|---|---|---|---|---|
| | service/job/etl-job/lambda/api/shared-library/batch/other/unknown | | | | | | observed/user-confirmed/possible |

Folders, domains, repositories and job groups are not components by default. Record internal modules below when they do not merit stable identity.

All candidate component paths are relative to the candidate logical repository root, not necessarily the physical Git root.

### Internal modules that are not component candidates

| Candidate component | Unit | Type | Purpose | Path | Evidence | State |
|---|---|---|---|---|---|---|
| | | | | | | observed/user-confirmed |

## Detailed architectural evidence

### Entrypoints and implementation behavior

| Candidate component | Entrypoint/path | Trigger or caller | Concise control-flow responsibility | Evidence | State |
|---|---|---|---|---|---|
| | | | | | observed/user-confirmed |

### Consumes

| Candidate component | Asset type | ID/name | From/source | Evidence | State |
|---|---|---|---|---|---|
| | api/event/table/file/schema/dataset/config/job-output/other | | | | observed/user-confirmed |

### Produces

| Candidate component | Asset type | ID/name | Known consumer/use | Evidence | State |
|---|---|---|---|---|---|
| | api/event/table/file/schema/dataset/job-output/other | | | | observed/user-confirmed |

### Runtime and code dependencies

| Candidate component | Dependency ID/name | Dependency type | Why required | Evidence | State |
|---|---|---|---|---|---|
| | | component/shared-library/schema-library/configuration/build-tooling/service/api/other/unknown | | | observed/user-confirmed |

### Infrastructure interactions

| Candidate component | Package/resource ID/name | Natural action | Why material | Evidence | State |
|---|---|---|---|---|---|
| | | uses/reads from/writes to/triggers/scheduled by/deployed by/monitored by | | | observed/user-confirmed |

### Configuration, deployment, failures and operations

| Candidate component | Concern | Finding or route | Evidence | State |
|---|---|---|---|---|
| | configuration/deployment/failure-mode/signal/monitoring/support/runbook | | | observed/user-confirmed |

### Related flows

| Candidate component | Flow/candidate flow | Role or step | Evidence | State |
|---|---|---|---|---|
| | | | | observed/user-confirmed |

Do not manufacture an end-to-end flow from one local call chain. Stage `_staging/flows/` only when a full boundary and ordering are supported.

## What is possible / unconfirmed

| Candidate/repository | Possible finding or connection | Why plausible | Evidence needed |
|---|---|---|---|
| | | | |

## Suggested curated targets

- `_curated/repositories/<primary-domain>/...`
- `_curated/components/<primary-domain>/...`
- Any evidenced related flow, infrastructure, schema, runbook, standard or incident target.

## Open questions

- Which repository boundary, primary domain or owner still needs confirmation?
- Which candidates are independently addressable components rather than folders or internal modules?
- Which component parent relationships represent real architectural composition?
- Which I/O, runtime dependencies or infrastructure actions remain possible rather than known?
- Which related repository, infrastructure or documentation source is inaccessible?
- Can the repository be curated safely while one or more component candidates remain deferred?
