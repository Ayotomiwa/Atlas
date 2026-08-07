# Components staging

## Purpose

`_staging/components/` captures raw, attributable evidence about a TeamA repository, service, deployable unit, scheduled job group, API, library or other meaningful implementation component.

Use it to preserve **what was found, how the component fits into its surrounding system, and what is still unknown** before any component knowledge becomes trusted.

A useful component entry should help a later curator answer:

> What is this component, where does it live, what does it do, what does it consume or produce, and which flows, infrastructure and operational concerns connect to it?

## Belongs here

Capture evidence such as:

- component/repository identity and location;
- observed responsibility and boundary;
- build/dependency metadata;
- important source/config/schema paths;
- meaningful internal units;
- known inputs/consumes and outputs/produces;
- related flows when evidenced;
- related infrastructure when evidenced;
- local README/CLAUDE references;
- operational signals, dashboards or common failure concerns;
- runbook, standard and incident-learning references;
- explicit engineer-supplied context.

Examples of reasonable component evidence include a Java service, an ETL job group, a shared library, an API component, a scheduled batch, or a meaningful monorepo submodule. A Lambda or script may be recorded as an internal unit without becoming a first-class component.

A component record may be incomplete; missing context should be visible rather than guessed.

## Does not belong here

Do not use this bucket for:

- a single MR/change — use `_staging/changes/`;
- a full end-to-end process across multiple components — use `_staging/flows/`;
- raw infrastructure package/resource discovery — use `_staging/infra/`;
- a standalone schema/data-contract investigation — use `_staging/schema-info/`;
- a full incident learning — use `_staging/incidents/`;
- a draft operational procedure — use `_staging/runbooks/`;
- a candidate reusable rule — use `_staging/standards/`;
- polished or authoritative conclusions — use curation later.

Never invent owners, consumers, dependencies, deployment behaviour or flow participation.

## Granularity

Stage the meaningful component first. Do not create one staging record per handler, Lambda, SQL file, script or config merely because those artefacts exist.

Record lower-level artefacts as **internal units** unless they are independently deployable/scheduled/operated, reused across meaningful contexts, attached to their own operational procedure, or otherwise significant for impact analysis.

## Component discovery lenses

When the evidence permits, inspect the component through these lenses rather than reducing discovery to one generic summary:

| Lens | Questions to answer from evidence |
|---|---|
| Identity/location | What is it called? Which repository/monorepo path owns it? Where are the main README/config/build files? |
| Responsibility | What behaviour is directly evidenced? What is explicitly outside its boundary? |
| Internal units | Which jobs/handlers/scripts/modules are useful to record without promoting them? |
| Consumes | Which APIs, events, tables, files, config, libraries or job outputs enter the component? |
| Produces | Which APIs, events, tables, files, alerts or job outputs leave it? |
| Flows | Which end-to-end paths does it participate in, and what role is evidenced? |
| Infrastructure | Which packages/resources deploy, trigger, host or support it? |
| Local references | Which local README/CLAUDE/build/config paths should a future engineer follow instead of duplicating drift-prone commands? |
| Operations | Which alerts, dashboards, failure signals, runbooks or incident learnings are evidenced? |
| Standards | Which candidate or curated standards appear relevant, without treating repo defaults as team policy? |

Do not create empty linked staging files merely because a lens has no evidence.

## Evidence expectations

Prefer concrete, attributable sources such as:

- repository and monorepo paths;
- README or local `CLAUDE.md`;
- build/dependency metadata;
- source/config/schema paths;
- API/event/data-contract definitions;
- infrastructure definitions;
- scheduler/workflow definitions;
- runbooks/operational docs;
- tickets or authorised external documentation;
- clearly labelled engineer/user statements.

Distinguish `observed` and `user-confirmed` evidence from `possible` or `unconfirmed` inference.

## Local-development reference rule

The product repository owns exact build, test and run commands. Staging may record where those instructions live and may capture stable local-development facts when relevant, but should prefer references to the local README/CLAUDE over copying commands likely to drift.

## Likely curated targets

A component staging record may lead to:

- `_curated/components/`;
- evidence-backed component relationships that regenerate repo/flow/infra maps;
- linked flow/infra/schema/runbook/standard/incident pages where the evidence genuinely supports them.

Staging records suggest targets; they do not author generated maps directly and do not establish authoritative relationships.

## Immutability

Once referenced by a curation proposal, do not alter, rename or move this evidence. Add a corrective staging record instead.

## Reviewer questions

Before curation, ask whether:

- identity, location and responsibility are evidenced;
- component granularity is sensible;
- internal units have been over-promoted or under-described;
- consumes/produces relationships are supported;
- flow participation and infrastructure use are actually evidenced;
- local references point to durable sources rather than duplicated commands;
- operational/runbook/standard/incident context is attributable;
- inaccessible or uninvestigated context remains explicit.

## Security and sensitivity

Never stage credentials, tokens, secret values, customer data, connection strings or raw sensitive logs. Link to authorised sources when the detail should not live in Atlas.
