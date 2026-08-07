# Changes staging

## Purpose

`_staging/changes/` captures **reusable engineering context discovered while investigating or implementing a logical change**. The change is the discovery context, not necessarily the durable Atlas concept.

Use this bucket so knowledge learned during delivery is not lost before it can be reviewed and routed to components, flows, infra, schemas, runbooks, standards or incident learnings.

A logical change may span one commit, one MR/PR, several related MRs, a release bundle or a bounded Claude investigation.

## Belongs here

Capture attributable evidence when a change reveals or modifies reusable context such as:

- component behaviour or responsibility;
- API/event/table/file/data-contract changes;
- new, removed or changed dependencies;
- schedules/triggers/orchestration;
- infrastructure references;
- runtime or operational behaviour;
- runbook gaps;
- standards/conventions;
- incident-related learning;
- upstream/downstream effects that need review.

Start here when the knowledge was discovered **because of the change** and has not yet been separated into its durable curated concept.

## Does not belong here

Do not use this bucket for:

- a full component onboarding — use `_staging/components/`;
- a full end-to-end flow capture — use `_staging/flows/`;
- raw infrastructure discovery — use `_staging/infra/`;
- a standalone schema/data-contract investigation — use `_staging/schema-info/`;
- a full incident learning — use `_staging/incidents/`;
- a draft operational procedure — use `_staging/runbooks/`;
- a candidate reusable engineering rule — use `_staging/standards/`;
- routine ticket status, implementation diary or noise with no reusable Atlas value.

## Logical-change boundary

Group evidence when several implementation changes form one coherent engineering outcome. Split entries when their scope, evidence, consumers or curation targets are materially independent.

The staging record should make clear **what changed**, **where**, and **why it may matter beyond this delivery item**.

## Evidence and uncertainty

Prefer concrete references: repositories, paths, commits/MRs, config/schema diffs, tests, documentation and supplied reviewer/user statements.

Separate:

- **known** — observed in evidence or explicitly user-confirmed;
- **possible / unconfirmed** — plausible impact that still needs evidence;
- **not covered** — an area not investigated or inaccessible.

A possible downstream effect is not a proven dependency.

## Curation outcomes

One change entry may result in:

1. no durable Atlas update;
2. update/create a component page;
3. update/create a flow page;
4. update/create infra or schema knowledge;
5. update/create a runbook, standard or incident learning;
6. relationship changes that regenerate maps;
7. defer/reject because evidence is insufficient or not reusable.

The curation workflow decides this; staging does not.

## Immutability

Once a staging record has been consumed/referenced by a curation proposal, **do not edit, rename or move it**. Add a corrective or follow-up staging record instead so the evidence trail remains reproducible.

## Security and sensitivity

Do not store credentials, tokens, secrets, customer data, raw sensitive logs or unnecessary personal data. Link to authorised systems and redact values that should not live in Atlas.
