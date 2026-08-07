# Changes staging

## Purpose

`_staging/changes/` captures **reusable engineering context discovered because of a logical engineering change**. The change is the discovery context, not necessarily the durable Atlas concept.

Use this bucket so knowledge learned during delivery is not lost before it can be reviewed and routed to components, flows, infra, schemas, runbooks, standards or incident learnings.

A logical change may be evidenced by one merged MR/PR, several related merged MRs/PRs, commits, a release bundle or another bounded engineering change. The logical change — not the number of delivery artefacts — is the staging boundary.

## Capture timing for code changes

For working-code changes, **capture into Atlas after the relevant code PR/MR has been approved and merged to the repository's default/main branch whenever practical**. Atlas should reason from the resulting repository state, not document an implementation that is still changing during review or may never land.

MR/PR identifiers are optional provenance. They do not control Atlas lifecycle state and they are not required for findings that did not originate from a code review.

If useful knowledge is discovered independently of a code change — for example during investigation, onboarding, architecture discussion, incident follow-up or an engineer-supplied clarification — stage it directly in the most appropriate bucket instead of manufacturing a change record.

## Default MR/PR-to-staging rule

The normal monorepo case is:

```text
one merged working-code MR/PR
        ↓
one logical change
        ↓
one `_staging/changes/` record
```

This is a default, not a rigid one-to-one invariant.

**Group multiple MRs/PRs into one change record** when they are delivery pieces of one coherent engineering outcome, substantially share the same reusable knowledge, and reviewing one without the others would produce misleading context.

**Split one broad MR/PR into multiple staging records** when it contains materially independent reusable findings with different boundaries, consumers or curation targets.

A release/epic association alone is not sufficient reason to group unrelated changes.

## Belongs here

Capture attributable evidence when a logical change reveals or modifies reusable context such as:

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

The staging record should make clear **what changed**, **where**, **what final/merged state was inspected when applicable**, and **why it may matter beyond this delivery item**.

## Evidence and uncertainty

Prefer concrete references: repositories, paths, merged commits/MRs/PRs, config/schema diffs, tests, documentation and supplied reviewer/user statements.

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

The curation workflow decides this; staging does not become authoritative.

## Lifecycle and immutability

Use the lifecycle defined by `_staging/README.md`. New change records start with `status: new`. After first commit, only the top-level `status` field may change; all evidence content and the path/ID remain immutable. Corrections or newly discovered context are new staging records.

## Security and sensitivity

Do not store credentials, tokens, secrets, customer data, raw sensitive logs or unnecessary personal data. Link to authorised systems and redact values that should not live in Atlas.
