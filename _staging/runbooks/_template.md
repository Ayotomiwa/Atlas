---
id: STG-YYYYMMDD-<slug>
type: atlas.staging.runbook
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
runbook_name: ""
covers: []
severity_scope: ""
observed_exercise_date: ""
---

# Runbook evidence: <scenario / procedure>

> This is evidence, not trusted operational guidance. Mark observed, confirmed and proposed steps separately.

## Summary

Describe the operational scenario, why a procedure is needed/changed and the source of the candidate guidance.

### Candidate procedure shape

- Trigger/symptom:
- Scope/covers:
- Desired recovery outcome:

## Evidence

- Existing runbook/docs:
- Repository script/config:
- Incident/exercise reference:
- Monitoring/alert definition:
- Engineer/operator-confirmed statement:
- Other:

## What is known

Capture steps/constraints that were observed or explicitly confirmed.

| Area | Finding/step | Source | State (`observed` / `user-confirmed`) |
|---|---|---|---|
| trigger/prerequisite/safety/investigation/recovery/validation/rollback/escalation/monitoring | | | |

## What is possible / unconfirmed

Capture proposed steps, untested rollback, inferred safety constraints or missing prerequisites that require review.

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
- How is success objectively validated?
- What is the rollback/stop condition?
- When must an operator escalate instead of continuing?
- Has the procedure been exercised, and in which environment/context?
