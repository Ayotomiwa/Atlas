---
id: STG-YYYYMMDD-<slug>
type: staging.component
package: datalens
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
- Selected source commit (full SHA):
- Active branch at selection, if any:
- Default ref and resolved commit:
- Merge base and relationship to default:
- Future merged-change intake anchor (normally the selected default commit or merge base for an unmerged branch):
- Snapshot mode (`in-place` / `temporary-worktree`); temporary manifest is not evidence:
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
| Operational/product owner | | | observed/user-confirmed/unknown |
| Review or approval route | | | observed/user-confirmed/unknown |
| Subject-matter expert | | | observed/user-confirmed/unknown |
| Candidate primary domain | | | observed/user-confirmed/possible |
| Related domains | | | observed/user-confirmed/possible |

Do not treat CODEOWNERS, approval rules or a person who can review this evidence as proof of operational/product ownership. Preserve each role separately.

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

### Publication and artifact assembly

Complete this when a directory, bundle or generated artifact is uploaded, synced or published. Declaration order does not establish clean assembly or success gating.

| Candidate publisher | Source directory/artifact | Destination | Inclusion or allow-list behaviour | Exclusions/cleanup | Clean assembly evidence | Control-flow condition | Safety significance | Evidence | State |
|---|---|---|---|---|---|---|---|---|---|
| | | | explicit allow-list / directory-wide / unknown | | clean workspace / isolated output / not evidenced | success / failure / always / attempted order / unknown | | | observed/user-confirmed/possible |

Flag paths that could expose secrets or unrelated files without opening or copying their contents. A directory-wide publication with no evidenced clean assembly or allow-list is not curation-ready as a publication claim.

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

### Per-component causal walkthroughs

Write one short subsection per candidate component. Explain the normal causal path from entrypoint or trigger through material processing and dependencies to durable output or externally visible effect. Include failure/partial-completion behavior and the operational signal when evidenced. Cite the source after each material sentence. Do not substitute a source-file list or infer success gating from command order.

#### <candidate component>

- Entry/trigger and preconditions:
- Material processing and decisions:
- Dependencies, state and infrastructure used:
- Outputs or external effects:
- Failure, retry or partial-completion behavior:
- Completion/operational signals:
- Coverage limits:

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
