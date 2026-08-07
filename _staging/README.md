# `_staging/` — raw evidence layer

## Purpose

`_staging/` captures useful TeamA engineering evidence before it is trusted. It preserves what was observed or supplied, where it came from, what is uncertain, and which curated areas may eventually need an update.

Staging is **not** polished documentation and is never authoritative.

## Trust model

```text
source/repository/engineer evidence
        ↓
_staging/ record
        ↓
Claude-assisted curation proposal
        ↓
human review
        ↓
_curated/ page with status: curated
```

A staging file may support a proposal, but it does not become trusted merely because it exists.

## Buckets

| Bucket | Use for |
|---|---|
| `changes/` | Reusable context discovered during a logical code/change investigation |
| `components/` | Raw repo/service/component discovery |
| `flows/` | Raw end-to-end flow evidence |
| `infra/` | Raw IaC/package/resource evidence |
| `schema-info/` | Raw table/event/file/API/data-contract evidence |
| `business-concepts/` | Raw supplied business definitions and meaning |
| `incidents/` | Sanitised reusable incident/near-miss learning |
| `runbooks/` | Draft operational procedures |
| `standards/` | Candidate reusable team standards/conventions |

Use `_staging/index.md` to route to buckets. V1 deliberately has **no manually maintained per-bucket indexes**; Git/search handles individual evidence discovery.

## Common staging contract

Every staging page starts from its bucket `_template.md` and uses the common envelope:

```yaml
id: STG-YYYYMMDD-<slug>
type: atlas.staging.<bucket>
package: teama
schema_version: atlas/1.0
timestamp: YYYY-MM-DD
title: ""
description: ""
status: new
captured_by: ""
source_type: ""
source_links: []
intended_curated_targets: []
```

Use a deterministic `-2`, `-3`, etc. suffix when the same-day slug already exists.

## Evidence and uncertainty

A useful staging entry should distinguish:

- what is directly observed;
- what a user/engineer explicitly confirmed;
- what is possible or inferred;
- what is not covered or inaccessible;
- what evidence/reviewer questions remain.

Do not rewrite raw evidence to sound more certain than its source.

## Immutability after consumption

Once a staging file is referenced by a curation proposal, its contents and path are immutable. Do not "clean it up" after the fact. Add a new corrective staging record and let review/status records describe the outcome.

Promotion/rejection state belongs in `reviews/` and `_curated/status/curation-status.md`, not by mutating consumed evidence.

## Sensitive data

Never stage credentials, tokens, secret values, customer data, raw sensitive logs, connection strings or unnecessary personal information. Redact or link to the authorised source instead.

## Claude behaviour

Claude should preserve provenance and uncertainty, propose only evidence-backed curated changes, avoid duplicate staging records where a logical change should be grouped, and never treat absence from staging as proof that something does not exist.
