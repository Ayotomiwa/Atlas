# Flows staging

## Purpose

`_staging/flows/` captures raw, attributable evidence about an end-to-end TeamA operational or data path **before the flow is trusted**.

Use this bucket when the important knowledge is how multiple components, jobs, contracts, resources or systems work together across a path of execution or data movement.

A useful flow entry should help an investigator answer:

> **How does this path behave end to end, where are its hand-offs, what is known upstream/downstream, and what evidence is still missing?**

Staging may be incomplete. An incomplete evidenced path is better than a complete-looking invented one.

## Belongs here

Use this bucket when evidence primarily describes a meaningful end-to-end path, for example:

- a scheduled or event-driven data pipeline;
- an API/request path crossing multiple components;
- ingestion, transformation and publication across repositories;
- a sequence of jobs connected by orchestration or scheduler dependencies;
- an event-processing path across producers, brokers/queues and consumers;
- an operational path whose failure can affect downstream processing;
- a flow walkthrough discovered during service onboarding, incident review or engineering investigation.

A flow can cross repository and platform boundaries. **Do not assume one repository equals one flow.** A valid flow may start in one component, cross infrastructure or scheduling boundaries, and finish in another component or data asset.

## Does not belong here

Do not use this bucket for:

- a single component/repository description — use `_staging/components/`;
- one logical MR/change — use `_staging/changes/`;
- raw infrastructure-package/resource discovery — use `_staging/infra/`;
- a standalone schema/data-contract investigation — use `_staging/schema-info/`;
- a full incident record — use `_staging/incidents/` for reusable sanitised incident evidence;
- a draft recovery procedure — use `_staging/runbooks/`;
- unsupported flow placeholders created merely because onboarding could not discover a path.

If evidence only proves one component's local behaviour, stage the component and leave the wider flow as unknown until the boundary is evidenced or user-confirmed.

## Flow boundary and granularity rule

One staging entry should represent one coherent candidate end-to-end operational/data path.

Capture, where evidence exists:

- **purpose/outcome** — what the path appears to achieve;
- **start** — schedule, event, API request, file arrival, upstream completion or manual action;
- **end** — published event/file/table, API response, downstream hand-off or other observable outcome;
- **in-scope steps** — the sequence needed to understand the path;
- **out-of-scope boundary** — where this entry deliberately stops.

Split flows when they have materially different triggers, outcomes, consumers, operational behaviour or failure/recovery paths. Do not split merely because the path crosses repositories.

## Discovery lenses

A flow investigation should deliberately look for the following, without forcing an answer where evidence is absent:

| Lens | Useful questions |
|---|---|
| Boundary | What starts the flow? What marks successful completion? |
| Sequence | What are the observed steps and in what order? |
| Participants | Which components, jobs, external systems or resources perform each step? |
| Hand-offs | Which APIs, events, tables, files, schemas or job outputs connect steps? |
| Upstream | What must exist, arrive or complete first? |
| Downstream | Who consumes the result and what do they depend on? |
| Orchestration | Which scheduler, event rule, workflow or dependency controls execution? |
| Infrastructure | Which infrastructure is material to execution or routing? |
| Operations | Which alarms, dashboards, runbooks or failure signals help explain the path? |
| Failure | Where can the path stop, partially complete, retry or create downstream risk? |

These are **capture prompts**, not completeness requirements. `unknown`/not-covered is valid.

## Sequence and hand-off discipline

Do not infer a step merely because two components mention the same table, event or resource. Ordering and dependency need evidence such as orchestration definitions, code/config references, explicit contracts or user-confirmed explanations.

For each material hand-off, preserve enough evidence to distinguish:

- producer/source;
- consumer/destination;
- contract or payload kind when known;
- trigger/ordering mechanism when known;
- whether the relationship is observed, user-confirmed or only possible.

A possible downstream consumer is not a proven dependency.

## Evidence expectations

Useful evidence includes:

- repository/config/source paths;
- scheduler/orchestration definitions;
- API/event/table/file/schema contracts;
- job definitions and dependency configuration;
- component and infrastructure references;
- monitoring/runbook/incident references;
- engineer walkthroughs or explicit user-confirmed explanations.

Prefer evidence for **each material boundary, step and hand-off**, not just one source proving that the flow name exists.

## Evidence and uncertainty states

Keep these states distinct:

- **observed** — directly supported by accessible source/config/documentation;
- **user-confirmed** — explicitly supplied/confirmed by the user or engineer;
- **possible / unconfirmed** — plausible but still missing sufficient evidence;
- **not covered** — not investigated, inaccessible or outside the evidence supplied.

Never fill a missing middle step to make the path look coherent.

## Likely curated targets

Evidence may support `_curated/flows/` plus linked component, infra, schema, runbook or incident pages. Reviewed relationships may later regenerate the relevant maps.

Do **not** write relationship facts into generated map JSON from staging. Curated Markdown relationships remain the authoring source of truth.

Only propose targets supported by the evidence; a flow entry does not require every related bucket to exist.

## Immutability

Once consumed/referenced by a curation proposal, this file and path are immutable. Add corrective or follow-up evidence rather than rewriting history.

## Reviewer questions

Before accepting curated flow knowledge, check:

- Is the start/end boundary actually evidenced or user-confirmed?
- Are ordered steps supported rather than inferred from naming proximity?
- Are cross-repo/platform hand-offs explicit enough to follow?
- Which upstream prerequisites and downstream consumers are confirmed?
- Are schedules/triggers/orchestration represented accurately?
- Are failure implications evidence-backed and safely worded?
- Which components, infra or contracts remain inaccessible/not covered?
- Has any possible relationship accidentally been presented as known?

## Security and sensitivity

Do not stage credentials, tokens, customer data, raw sensitive production logs or unnecessary personal information. Prefer durable references to authorised sources.