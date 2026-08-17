---
id: STG-YYYYMMDD-<slug>
type: staging.flow
package: datalens
timestamp: YYYY-MM-DD
title: ""
description: ""
status: new
captured_by: ""
source_type: ""
---

# Flow evidence: <flow or candidate flow>

> Capture the evidenced path, including its hand-offs and gaps. A flow may cross repositories and platforms. Do not manufacture missing steps or create a complete-looking path from inference alone.

> Store this record one level below the bucket at `_staging/flows/<candidate-domain-or-unassigned>/<STG-ID>.md`. Use a domain only when evidenced or user-confirmed; otherwise use `unassigned`. Do not group by repository path.

## Summary

State the apparent outcome first, then the boundary and why this path is reusable. Use plain technical language before Atlas terms.

### Candidate purpose and boundary

- Apparent purpose/outcome:
- Starts at:
- Ends at:
- In scope:
- Explicitly out of scope:
- Boundary state: `observed` / `user-confirmed` / `possible` / `not-covered`

If the start/end boundary is not defensible, say so explicitly rather than presenting a confirmed flow.

## Evidence

List exact attributable sources. Include sources for ordering and hand-offs, not only for participant identity.

- Repository/source/config path:
- Scheduler/orchestration definition:
- API/event/table/file/schema contract:
- Job/dependency definition:
- Infrastructure/template reference:
- Monitoring/runbook/incident reference:
- Jira/Confluence/engineering-document reference:
- Engineer/user-confirmed walkthrough:
- Other:

## What is known

Record only **observed** or **user-confirmed** findings below.

### Entry point / trigger

| Trigger/source | Kind | Target/first step | Evidence | State |
|---|---|---|---|---|
| | event/schedule/file/api/manual/other | | | observed/user-confirmed |

Represent an upstream completion by its evidenced signal (usually `event`) and name the upstream source; do not invent a separate compiled kind.

### End-to-end steps

Record the meaningful sequence. The step table is the sole participant capture surface; do not add a second participant roster.

| Order | Candidate step ID | Activity / hand-off | Participant name | Participant type | Known Atlas ID | Role | Material receives | Material emits | Transition/condition | Evidence | State |
|---:|---|---|---|---|---|---|---|---|---|---|---|
| 10 | | | | component/infra/infra-resource/external-system/manual/unknown | | | | | | | observed/user-confirmed |

Do not add a missing step merely because it would make the sequence easier to explain.

Record whether each handoff is success-gated, failure-gated, unconditional, retried, or merely observed in attempted order. Visual adjacency or sequential declarations do not prove that the earlier step succeeded before the later step ran.

### Execution narrative

Explain the evidenced normal path in readable prose, including why each material transition occurs and where data/control crosses a component, infrastructure or external boundary. Describe supported branches, retries and failure-only paths. Cite ordering and gating evidence directly; label gaps instead of filling them with an inferred step.

- Normal path:
- Conditional/failure/retry paths:
- Material boundary crossings:
- Completion or success evidence:
- Coverage limits:

### Boundary inputs, outputs and material hand-offs

Capture whole-flow boundary contracts here. Step-local durable hand-offs belong on the applicable step above and should not be duplicated.

| Kind | Name/contract | Producer/source | Consumer/destination | Ordering/trigger if known | Evidence |
|---|---|---|---|---|---|
| api/event/table/file/schema/dataset/job-output/other | | | | | |

### Upstream dependencies

| Upstream item | What the flow needs from it | Evidence | State |
|---|---|---|---|
| | | | observed/user-confirmed |

### Downstream consumers

| Consumer | What it consumes/depends on | Evidence | State |
|---|---|---|---|
| | | | observed/user-confirmed |

### Jobs, schedules and orchestration

| Job/orchestrator | Role | Trigger/frequency/dependency | Definition/reference | Evidence |
|---|---|---|---|---|
| | | | | |

### Infrastructure used by the path

Record only infrastructure material to understanding execution, routing, orchestration or failure. Use action-specific observed wording such as uses, reads, writes, schedules or monitors. Detailed package/resource discovery belongs in `_staging/infra/`.

| Infra/package/resource | Role in flow | Participant/step using it | Evidence |
|---|---|---|---|
| | | | |

### Operational and failure evidence

This section captures evidence about the flow; it is not a substitute for a reviewed runbook or incident record.

| Failure/signal | Where observed | Known impact or symptom | Monitoring/runbook/incident reference | Evidence |
|---|---|---|---|---|
| | | | | |

## What is possible / unconfirmed

Keep plausible but unsupported sequencing, dependencies, consumers and blast-radius implications here.

| Possible step/connection/impact | Why plausible | Evidence needed to confirm |
|---|---|---|
| | | |

Examples include an inferred downstream consumer, an assumed scheduler dependency, a likely resource relationship or an unverified failure effect. Do not promote these because names or timestamps appear correlated.

## Suggested curated targets

List only evidence-supported durable targets, for example:

- `_curated/flows/<primary-domain>/...`
- related `_curated/components/<primary-domain>/...`
- related `_curated/infra/<primary-domain>/...`
- related `_curated/schema-info/<primary-domain>/...`
- related `_curated/runbooks/...`
- related `_curated/incidents/...`
- curated connection fields that will regenerate the appropriate maps

Do not propose direct edits to generated map JSON as the source of truth.

## Open questions

- Is the start/end boundary confirmed?
- Which steps or hand-offs remain missing?
- Which participant identities or repositories are unresolved?
- Which upstream prerequisites are proven versus assumed?
- Which downstream consumers are known versus possible?
- Are schedules, triggers and ordering dependencies evidenced?
- Which APIs/events/tables/files/schemas define important hand-offs?
- Is material infrastructure in another supplied but inaccessible location?
- What failure/retry/partial-completion behaviour remains unknown?
- Which areas were not investigated and therefore must remain not covered?
