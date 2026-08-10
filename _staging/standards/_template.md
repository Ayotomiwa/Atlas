---
id: STG-YYYYMMDD-<slug>
type: staging.standard
package: teama
timestamp: YYYY-MM-DD
title: ""
description: ""
status: new
captured_by: ""
source_type: ""
---

# Standard evidence: <candidate rule or convention>

> This record captures evidence for a possible reusable standard. Repetition is evidence of practice, not proof of policy.

## Summary

State the candidate reusable rule/theme and why the evidence may matter beyond one repository.

### Candidate rule

Phrase the observation without overstating authority, e.g. "Multiple inspected Java services use ..." rather than "TeamA requires ..." unless an authoritative source says so.

### Candidate scope/category

- Likely category (`general`, `java`, `python`, `aws`, `infra`, `jira`, `data`, `testing`, `git`):
- Observed component/repo/flow/infra scope:
- Authority state (`explicit`, `repeated-practice`, `repo-local`, `possible`, `unknown`):
- Mandatory vs recommended: leave `unknown` unless supported by authority.

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

### Observed applicability evidence

| Context/repository/technology | Applies / does not apply / unclear | What demonstrates this | Source |
|---|---|---|---|
| | | | |

### Observed rationale

Record rationale only when a source states it or a user explicitly confirms it. Otherwise put a proposed rationale under `What is possible / unconfirmed`.

- 

### Observed examples

Examples are evidence of how the candidate rule is applied; they do not by themselves prove mandate.

| Example | Context | Source |
|---|---|---|
| | | |

### Counterexamples / anti-pattern evidence

Capture conflicting implementation, explicitly documented anti-patterns, or examples that limit the candidate's scope.

| Counterexample/anti-pattern | Context | What it tells us | Source |
|---|---|---|---|
| | | | |

### Known exceptions

| Exception | Scope | Authority/evidence |
|---|---|---|
| | | |

Do not manufacture consistency by omitting counterexamples or exceptions.

## What is possible / unconfirmed

| Possible rule/scope/rationale | Why plausible | Evidence/authority needed |
|---|---|---|
| | | |

Questions such as "mandatory or recommended?", "does this apply to all Java services?" or "is this rationale intentional?" belong here until supported.

## Suggested curated targets

- `_curated/standards/<category>/...`
- existing standard to update/extend/supersede:
- related components/flows that may eventually `must-follow` the standard:

Do not create governed applicability edges from pattern frequency alone.

## Open questions

- Is this an explicit TeamA rule or merely repeated practice?
- Who/what is the authority for the rule?
- What category and scope are correct?
- Is it mandatory or recommended?
- What rationale is actually evidenced?
- Which repositories/technologies are examples, counterexamples or valid exceptions?
- Is there an organisation/security policy that takes precedence?
- Does an existing standard already cover, extend or conflict with this candidate?
