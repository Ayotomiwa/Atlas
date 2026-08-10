# `_staging/` — raw evidence and curation queue

## Purpose

`_staging/` captures useful TeamA engineering evidence before it is trusted. It preserves what was observed or supplied, where it came from, what is uncertain, and which curated areas may eventually need an update.

Staging is **not** polished documentation and is never authoritative. It is also the scalable curation queue: lifecycle state lives on each staging record rather than in a central per-record ledger.

## Trust model

```text
source / repository / engineer evidence
        ↓
_staging/ record with status: new
        ↓
Claude-assisted curation proposal
        ↓
Atlas PR/MR + human review
        ↓
_curated/ page with status: curated
```

A staging file may support a proposal, but it does not become trusted merely because it exists or because its workflow status changes.

## Buckets

| Bucket | Use for |
|---|---|
| `changes/` | Reusable context discovered because of a logical engineering change |
| `components/` | Raw repo/service/component discovery |
| `flows/` | Raw end-to-end flow evidence |
| `infra/` | Raw IaC/package/resource evidence |
| `schema-info/` | Raw table/event/file/API/data-contract evidence |
| `business-concepts/` | Raw supplied business definitions and meaning |
| `incidents/` | Sanitised reusable incident/near-miss learning |
| `runbooks/` | Draft operational procedures |
| `standards/` | Candidate reusable team standards/conventions |

Use `_staging/index.md` to route to buckets. Component and flow queues have generated root/domain indexes because those records are domain-routed; other buckets continue to use Git/search rather than manually maintained catalogues.

## Common staging contract

Every staging page starts from its bucket `_template.md` and uses the common envelope:

```yaml
id: STG-YYYYMMDD-<slug>
type: staging.<bucket>
package: teama
timestamp: YYYY-MM-DD
title: ""
description: ""
status: new
captured_by: ""
source_type: ""
```

Evidence sources and suggested curation destinations are captured in the body (`## Evidence` and `## Suggested curated targets`), not duplicated as frontmatter fields. `atlas-curate` reads the full record, and may bulk-scan the `## Suggested curated targets` section across multiple eligible staging records when routing curation work, rather than relying on a machine-only frontmatter field.

The filename must be exactly `<staging-id>.md`, for example `STG-20260809-retry-evidence.md`. Use a deterministic `-2`, `-3`, etc. ID suffix when the same-day slug already exists.

## Source-type recommendations

`source_type` is open-ended provenance, not a closed enum. Prefer a clear value from the relevant group when it fits:

- changes: `merged-change`, `release`, `repository`, `engineer-note`, `claude-investigation`, `other`;
- component, flow, infrastructure and schema discovery: `repository`, `onboarding`, `documentation`, `engineer-note`, `user-statement`, `claude-investigation`, `other`;
- incidents and runbooks: `incident`, `near-miss`, `exercise`, `documentation`, `operator-note`, `engineer-note`, `other`;
- standards: `policy`, `team-guidance`, `repository`, `multi-repo-observation`, `incident`, `engineer-note`, `claude-investigation`, `other`;
- business concepts: `governed-definition`, `sme-statement`, `documentation`, `implementation-observation`, `other`.

New precise values are allowed when these do not describe the source.

## Common reviewer gate

Before using a staging record for curation, confirm that its filename matches its ID, provenance is attributable, known and possible claims are separated, sensitive material is absent, and suggested targets do not overreach the evidence.

## Lifecycle status

The staging record itself is the queue. On the default branch:

| Status | Meaning | Automatic curation behaviour |
|---|---|---|
| `new` | captured evidence not yet processed | eligible |
| `curating` | actively being reconciled in Atlas work | do not start a duplicate; resume/check the active work |
| `curated` | curation completed and accepted knowledge was produced | skip |
| `no-change` | reviewed; no durable curated change was needed | skip |
| `deferred` | insufficient evidence or a deliberate blocker remains | skip until explicitly reset/reconsidered |
| `rejected` | not suitable for durable Atlas knowledge | skip |

A branch or open Atlas PR/MR may contain a proposed status transition before it exists on the default branch. For queue decisions, prefer the default branch and also check active Atlas work for the same staging ID when concurrent curation is plausible.

`curated` is a **staging workflow outcome**, not a statement that every claim in the staging file was accepted. Curated knowledge remains governed by `_curated/` page status and evidence.

## Immutability after capture

After a staging record is first committed, its evidence is immutable. **The only field that may subsequently change is top-level frontmatter `status`.**

Do not edit the body, title, description, provenance, path or ID to make old evidence look cleaner or more accurate. Add a new corrective/follow-up staging record instead.

This status-only exception supersedes any bucket wording that says consumed evidence must never be edited: lifecycle status may change; evidence content may not.

## Evidence and uncertainty

A useful staging entry should distinguish:

- what is directly observed;
- what a user/engineer explicitly confirmed;
- what is possible or inferred;
- what is not covered or inaccessible;
- what evidence/reviewer questions remain.

Do not rewrite raw evidence to sound more certain than its source.

## Where review history lives

The **Atlas PR/MR is the human review and audit record** for curation. Its description should identify staging records consumed, curation outcomes, curated pages/connection fields changed, material claims not promoted, open questions and validation results. Git then retains reviewer identity, comments, approvals, changes requested, timestamps, diff and merge commit without duplicating that reasoning into a second Markdown review system.

`_curated/status/curation-status.md` is only a compact last-run/checkpoint summary. It is not the queue and must not grow into a row per staging record.

## Sensitive data

Never stage credentials, tokens, secret values, customer data, raw sensitive logs, connection strings or unnecessary personal information. Redact or link to the authorised source instead.

## Claude behaviour

Claude should preserve provenance and uncertainty, propose only evidence-backed curated changes, avoid duplicate staging records where a logical change should be grouped, and never treat absence from staging as proof that something does not exist.
