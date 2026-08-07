# Incident Learnings policy

## Purpose

`_curated/incidents/` stores reviewed, sanitised **reusable operational learning** from incidents, near misses or exercises. It is not an incident-management system and should not duplicate the full incident record.

An incident-learning page should help answer: **what reusable failure pattern or lesson should engineers remember, what impact/cause/detection/recovery evidence supports it, and what should change in Atlas knowledge or operational practice?**

## Trust level

Only `status: curated` incident learnings are authoritative Atlas knowledge. `draft` and `proposed` pages require human review. The source incident system remains authoritative for the original incident timeline and governance record.

## When to use this area

Use an incident-learning page when an event produced durable knowledge such as:

- a failure mode worth remembering;
- a dependency or blast-radius relationship that was hard to discover;
- a monitoring/detection lesson;
- a recovery lesson;
- a runbook gap;
- a standard/process gap;
- a recurring diagnostic clue;
- a near-miss or exercise lesson with operational value.

## When not to use it

Do not use this area for:

- the complete incident record or minute-by-minute chronology;
- transient incident status updates;
- raw logs, screenshots or customer data;
- blame-oriented narrative or unnecessary personal details;
- unreviewed suspected causes presented as confirmed;
- a full recovery procedure — use `_curated/runbooks/`;
- general component/flow description not specific to reusable learning.

## Granularity rule

Create one page per coherent reusable incident learning record. A major incident may yield multiple durable learnings if they have different scopes or consumers; conversely, do not split every observation into its own page.

Optimise for reusable memory, not archival completeness.

## Storage/filename convention

Use descriptive, sanitised kebab-case filenames based on the learning/failure pattern rather than sensitive ticket text. IDs are stable logical identities and do not need to contain incident-system identifiers.

## Required frontmatter/type-specific fields

Start from `_template.md`. Use `type: atlas.incident-learning`, the common curated envelope and:

```yaml
incident_date: ""
severity: ""
resolved: false
```

Only populate values that are safe and supported by evidence. Do not embed confidential incident metadata merely because it exists upstream.

## Relationship guidance

Use only taxonomy-approved relationships.

Common relationships include:

- `atlas.informed-by` from a runbook/standard/component/flow to the incident learning when it materially changes understanding;
- `atlas.depends-on` only where the incident established a real durable dependency;
- `atlas.operated-by` when a relevant reviewed runbook applies;
- `atlas.must-follow` for standards implicated by the learning;
- `atlas.supersedes` if a learning record replaces a prior sanitised interpretation.

Do not create edges from speculative blast-radius observations until supported.

## Evidence expectations

Use attributable, sanitised evidence such as:

- link/reference to the authorised incident record;
- staging incident evidence;
- reviewed post-incident notes;
- monitoring or alert references;
- repository/configuration paths;
- runbook references;
- reviewer-confirmed findings.

Prefer linking to sensitive source systems instead of copying their contents.

## `not covered` rule

When a required section has no safe/evidenced content, use exactly:

```markdown
*Not covered — no evidence in current staging material.*
```

Do not turn a suspected cause or impact into fact to fill the page.

## Agent curation instructions

Before proposing an incident-learning page, read this README, `_template.md` and `index.md`. Sanitise source material, extract only reusable engineering learning, preserve uncertainty around cause/impact, and link affected components/flows/infra/runbooks/standards only when supported. Never copy a full major-incident record by default.

## Reviewer checklist

Before approval, verify:

- the page captures durable learning rather than incident administration;
- summary and impact are appropriately sanitised;
- confirmed cause is distinguished from suspected cause;
- detection and recovery lessons are evidence-backed;
- runbook/standard gaps lead to useful follow-up context without inventing policy;
- relationship updates reflect proven dependencies/impact;
- sensitive data, names and raw logs are absent unless explicitly appropriate;
- the page is indexed and coverage gaps are clear.

## Index maintenance rule

Every non-archived incident-learning page must appear in `index.md`. Archived learnings remain in history but are excluded from normal routing.

## Security/sensitivity reminder

Minimise incident detail. Never copy secrets, credentials, customer information, unnecessary personal data, raw sensitive logs or restricted investigation material. Use `[REDACTED]` where needed and link to the authorised source for details that should remain outside Atlas.
