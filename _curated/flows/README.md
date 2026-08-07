# Flows policy

## Purpose

`_curated/flows/` stores reviewed end-to-end operational and data-flow knowledge. A flow page explains how meaningful steps/components work together from an entry point to an outcome.

A flow page should help answer: **how does this path work end to end, what participates in it, what is upstream/downstream, and what may be affected if it changes or fails?**

## Trust level

Only `status: curated` pages are authoritative. `draft` and `proposed` pages require human review. Claude can propose flow knowledge but cannot approve or merge it.

## When to use this area

Use a flow page when the knowledge is primarily about an end-to-end path that crosses meaningful steps/components, for example:

- scheduled or event-driven data pipelines;
- API request paths spanning multiple components;
- ingestion/publication flows;
- operational paths with meaningful upstream/downstream impact;
- flows with runbooks, failure modes or incident relevance.

## When not to use it

Do not use a flow page for:

- detailed implementation notes belonging to one component;
- every individual job, Lambda or script unless it is itself an independently meaningful flow;
- raw walkthrough notes or unverified sequences;
- full incident records;
- unsupported blast-radius statements.

## Granularity rule

One page should represent one meaningful end-to-end operational/data path crossing meaningful steps or components. Keep internal implementation detail on component pages and infrastructure detail on infra pages; link rather than duplicate.

## Storage/filename convention

Use stable kebab-case filenames directly or under sensible grouping folders in `_curated/flows/`. The page `id` is logical and stable; file moves do not force ID changes.

## Required frontmatter/type-specific fields

Start from `_template.md` with `type: atlas.flow`, the common curated envelope and:

```yaml
flow_scope: ""
trigger: ""
schedule: ""
entry_component: ""
exit_component: ""
```

## Relationship guidance

Use taxonomy-approved relationships only. `atlas.participates-in` drives the flow-component projection; flow-to-flow `atlas.depends-on` relationships may also be projected there. Keep detailed application contracts in component/schema relationships and detailed resource relationships in infra pages.

Preserve direction, confidence, evidence and uncertainty. Absence of a relationship means "not covered/no known relationship", not proof of no impact.

## Evidence expectations

Evidence may include:

- staging flow/component/infra entries;
- repository/config/schema paths;
- scheduler or orchestration definitions;
- component pages;
- infrastructure definitions;
- runbooks and incident learnings;
- external engineering documentation;
- reviewer-confirmed explanations.

Every material step, participant and dependency should be evidenced or explicitly marked possible/unconfirmed.

## `not covered` rule

Use exactly `*Not covered — no evidence in current staging material.*` when a required section has no evidence. Never invent missing steps or consumers.

## Agent curation instructions

Before proposing a flow change, read this README, `_template.md` and `index.md`. Resolve the flow boundary before writing. Search for an existing page before creating one. Preserve unknown steps, update typed relationships on curated Markdown only, rebuild maps, update status/review records and run validation.

## Reviewer checklist

Check that:

- the flow boundary, trigger and output are clear;
- ordered steps are evidence-backed;
- participating components are linked correctly;
- upstream/downstream claims are supported;
- schedules/orchestration are accurately represented;
- infrastructure, runbooks and incident learnings are relevant;
- uncertainty is explicit;
- indexes/maps are consistent;
- no sensitive material is copied into Atlas.

## Index maintenance rule

Every non-archived flow page must appear in `index.md`. Archived pages stay out of normal routing.

## Security/sensitivity reminder

Do not include secrets, credentials, raw production/customer data or sensitive logs. Prefer references to authorised sources.
