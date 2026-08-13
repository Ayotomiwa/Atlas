---
id: STG-YYYYMMDD-<slug>
type: staging.runbook
package: datalens
timestamp: YYYY-MM-DD
title: ""
description: ""
status: new
captured_by: ""
source_type: ""
---

# Runbook evidence: <scenario / procedure>

> This is evidence, not trusted operational guidance. Mark observed, confirmed and proposed steps separately. Never present an untested destructive action as safe.

## Summary

Describe the operational scenario, why a procedure is needed/changed and the source of the candidate guidance.

### Candidate procedure boundary

- Trigger/symptom:
- Scope/covers:
- Desired recovery outcome:
- Environment/context observed:
- Last exercised/observed date, if known:

## Evidence

- Existing runbook/docs:
- Repository script/config:
- Incident/exercise reference:
- Monitoring/alert definition:
- Change/Jira reference:
- Engineer/operator-confirmed statement:
- Other:

## What is known

Capture only observed or explicitly confirmed procedure knowledge.

### Trigger and prerequisites

| Finding | Source | State |
|---|---|---|
| | | observed/user-confirmed |

### Affected context

| Component/flow/infra/environment | Applies or excluded | Evidence | State |
|---|---|---|---|
| | | | observed/user-confirmed |

### Known failure modes / when not to use

| Failure mode or exclusion | Why this procedure is unsafe/inapplicable | Alternative/escalation | Evidence |
|---|---|---|---|
| | | | |

### Safety / stop conditions

Record conditions that make an action unsafe, prohibited or escalation-only, including possible data loss, duplicate processing or partial-processing risk.

| Safety constraint/stop condition | Risk prevented | Source | State |
|---|---|---|---|
| | | | observed/user-confirmed |

### Investigation

| Step | Observation/action | Expected signal | Source | State |
|---|---|---|---|---|
| 1 | | | | observed/user-confirmed |

### Procedure rationale and decision path

Explain how observations select the next diagnostic or recovery action, why each action is safe within its preconditions, when the operator must stop, and how validation or escalation closes the procedure. Cite exercised or confirmed evidence and keep untested ideas below.

- Decision path:
- Step rationale:
- Safety boundary:
- Objective completion test:
- Escalation boundary:

### Recovery

Record what was actually performed or explicitly confirmed—not what merely seems technically possible.

| Step | Recovery action | Preconditions | Source | State |
|---|---|---|---|---|
| 1 | | | | observed/user-confirmed |

### Validation after recovery

| Check | Success condition | Source | State |
|---|---|---|---|
| | | | observed/user-confirmed |

### Rollback / rerun constraints

| Scenario | Rollback/rerun guidance | Safety condition | Source | State |
|---|---|---|---|---|
| | | | | observed/user-confirmed |

### Escalation

| Condition | Escalate to role/system | Evidence/source |
|---|---|---|
| | | |

### Monitoring / operational references

- Alerts:
- Dashboards:
- Logs/metrics references:
- Other:

### Other known findings

| Area | Finding/step | Source | State (`observed` / `user-confirmed`) |
|---|---|---|---|
| | | | |

## What is possible / unconfirmed

Capture proposed steps, untested rollback/rerun, inferred safety constraints or missing prerequisites that require review.

| Possible guidance | Risk/why plausible | Evidence or validation needed |
|---|---|---|
| | | |

Never promote a destructive candidate action solely because it appears technically possible.

## Suggested curated targets

- `_curated/runbooks/...`
- related `_curated/components/...`
- related `_curated/flows/...`
- related `_curated/infra/...`
- related `_curated/incidents/...`
- related `_curated/standards/...`

## Open questions

- When exactly should this procedure be used?
- What prerequisites/access are required?
- What actions can cause data loss, duplication or wider impact?
- When is rerun/replay safe, unsafe or prohibited?
- How is partial processing detected and handled?
- How is success objectively validated?
- What is the rollback/stop condition?
- When must an operator escalate instead of continuing?
- Has the procedure been exercised, and in which environment/context?
