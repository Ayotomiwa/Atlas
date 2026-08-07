---
id: STG-YYYYMMDD-<slug>
type: atlas.staging.standard
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
candidate_category: general
applies_to_observed: []
authority: unknown
repositories_examined: []
---

# Standard evidence: <candidate rule or convention>

## Summary

State the candidate reusable rule/theme and why the evidence may matter beyond one repository.

### Candidate rule

Phrase the observation without overstating authority, e.g. "Multiple inspected Java services use ..." rather than "TeamA requires ..." unless an authoritative source says so.

## Evidence

List independent attributable sources.

| Source | Repository/path/reference | What it demonstrates | Evidence strength |
|---|---|---|---|
| | | | explicit/repeated/local |

Also record supplied team/lead/policy statements separately from observed implementation patterns.

## What is known

| Finding | Scope observed | Source | State (`observed` / `user-confirmed`) |
|---|---|---|---|
| | | | |

Capture known exceptions/conflicting practice too; consistency should not be manufactured by ignoring counterexamples.

## What is possible / unconfirmed

| Possible rule/scope/rationale | Why plausible | Evidence/authority needed |
|---|---|---|
| | | |

Questions such as "mandatory or recommended?" belong here until supported.

## Suggested curated targets

- `_curated/standards/<category>/...`
- existing standard to update/extend/supersede:
- related components/flows that may eventually `atlas.must-follow` the standard:

Do not create governed applicability edges from pattern frequency alone.

## Open questions

- Is this an explicit TeamA rule or merely repeated practice?
- What category and scope are correct?
- Is it mandatory or recommended?
- Which repositories/technologies are exceptions?
- Is there an organisation/security policy that takes precedence?
- Does an existing standard already cover this rule?
- What rationale is evidenced rather than inferred?
