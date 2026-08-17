# Runbooks policy

## Purpose

`_curated/runbooks/` stores reviewed, reusable operational procedures for diagnosing, recovering or safely handling known engineering situations.

A runbook should help answer: **when should I use this procedure, what must I check before acting, what steps are safe, how do I know recovery worked, and when should I stop or escalate?**

## Trust level

Every `status: curated` runbook is authoritative Atlas guidance; Git/merge state is only a checkout advisory. A curated runbook does not override live incident command, organisation policy or access controls.

## When to use this area

Use a runbook for stable operational guidance that is worth reusing, including:

- recurring failure/recovery procedures;
- diagnostic sequences;
- safe restart/replay/reprocessing guidance;
- validation after recovery;
- rollback or escalation decision points;
- monitoring/alert response procedures;
- operational checks tied to components, flows or infrastructure.

## When not to use it

Do not use runbooks for:

- a full incident record — use incident tooling and capture reusable learning separately;
- speculative recovery steps that have not been reviewed;
- local development setup owned by a product repository;
- broad architecture explanation better stored in components/flows/infra;
- transient status updates;
- credentials, tokens or sensitive operational data.

## Granularity rule

Create one runbook per coherent operational scenario/procedure. It may cover multiple components when the recovery path is naturally end-to-end, but avoid giant catch-all runbooks that mix unrelated failure modes.

A full runbook requires all four of these evidenced elements: a trigger and scope, an ordered diagnostic or recovery procedure, safety/stop conditions, and objective validation or escalation. If any element is absent, keep the material as an operational note on the narrowest applicable component or infrastructure page instead of manufacturing a complete procedure. `last_exercised` may remain empty, but the page must disclose that limitation.

Split procedures when triggers, safety constraints, ownership, recovery actions or validation differ materially.

## Storage/filename convention

Use descriptive action/scenario-oriented kebab-case filenames, for example `reference-data-recovery.md`. IDs are stable logical identities and are not derived from paths.

## Required frontmatter/type-specific fields

Start from `_template.md`. Use `type: runbook`, the common curated envelope and:

```yaml
last_exercised: ""
```

Populate `last_exercised` only with a validated `YYYY-MM-DD` date supported by evidence; lint rejects any other non-empty value. An unexercised procedure keeps the field empty rather than guessing. Scope, environments and exclusions belong in the Scope / applicability section, where their limits can be explained.

## Relationship guidance

Use only page-link types registered in `contracts/map-fields.yaml`.

Typical relationships include:

- `operated-by` from a component/flow/infra concept to the runbook;
- `must-follow` for standards constraining recovery behaviour;
- `informed-by` when incident learning materially shaped the runbook;
- `supersedes` when a runbook replaces an older procedure.

Record operational prerequisites in the runbook body with direct links to their owning source. If a prerequisite is also a durable architectural dependency, author it through the natural dependency field on the owning repository, component, or infrastructure page. Do not invent a generic page link. Do not create operational relationship edges unless the procedure actually applies to the target.

## Evidence expectations

Operational guidance should be backed by sources such as:

- existing approved operational documentation;
- repository scripts/configuration;
- monitoring/alert definitions;
- incident or exercise learning;
- staging evidence;
- reviewer/operator-confirmed steps.

High-risk actions deserve stronger evidence than descriptive context. Where a command or endpoint is likely to drift, link to the owning repository/document rather than duplicating it.

## `not covered` rule

The template uses this placeholder while evidence is still being assembled:

```markdown
*Not covered — no evidence in current staging material.*
```

Before final curation, replace the placeholder in the four core elements: trigger/scope, ordered diagnostic or recovery procedure, safety/stop conditions, and objective validation or escalation.

If any core element remains unsupported, do not curate a full runbook. Keep the supported material as an operational note on the narrowest applicable component or infrastructure page. Optional sections may retain the placeholder to show an explicit coverage gap.

Never invent a recovery, rollback, or validation step to make a runbook appear complete.

## Agent curation instructions

Before proposing a runbook change, read this README, `_template.md` and `index.md`. Resolve the exact scenario and covered concepts, preserve safety boundaries, distinguish observation from procedure, and surface missing recovery/rollback/escalation evidence. Prefer links to authoritative executable instructions when exact commands may drift.

## Reviewer checklist

Before completing curation, verify:

- trigger/symptom and scope are clear;
- prerequisites and permissions are explicit;
- safety/stop conditions are adequate;
- investigation steps precede destructive recovery where appropriate;
- recovery steps are ordered and evidence-backed;
- success validation is objective;
- rollback and escalation paths are usable;
- none of the four required core elements remains `Not covered`;
- monitoring references remain valid;
- sensitive values are not embedded;
- `last_exercised` is not fabricated and coverage gaps are visible.

## Index maintenance rule

The catalogue in `index.md` is generated by `python scripts/rebuild_atlas.py`, and `python scripts/rebuild_atlas.py --check` reports drift, so do not hand-edit it. Archived runbooks are excluded automatically and remain for history.

## Security/sensitivity reminder

Never store secrets, privileged tokens, customer data, raw production logs or bypass instructions. Describe required access at the appropriate level and link to authorised secret/operational systems instead of copying sensitive values into Atlas.
