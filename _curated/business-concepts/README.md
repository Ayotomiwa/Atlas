# Business Concepts policy

## Purpose

`_curated/business-concepts/` stores reviewed, reusable business meaning that engineers need when interpreting systems, data and requirements.

A business-concept page should help answer: **what does this term mean for TeamA, what is inside or outside the definition, which variants are approved, and where is that meaning implemented or represented?**

## Trust level

Only pages with `status: curated` are authoritative TeamA knowledge. `draft` pages require human review. A label found in code, a dashboard or an email is evidence of usage, not automatically an approved definition.

## When to use this area

Use a business-concept page when a term or rule has durable meaning that is reused across engineering work, for example:

- a business entity or classification;
- an agreed inclusion/exclusion rule;
- a term whose meaning differs from its everyday interpretation;
- an approved variant or alias;
- semantics needed to interpret schemas, flows or Jira requirements;
- a definition that repeatedly causes ambiguity across systems.

## When not to use it

Do not use this area for:

- physical table/event/API structure — use `_curated/schema-info/`;
- implementation responsibilities — use `_curated/components/`;
- a one-off ticket requirement or transient delivery decision;
- an unreviewed assumption inferred from code names;
- general glossary content that does not affect TeamA engineering decisions;
- long source documents that are better linked than copied.

## Granularity rule

Create one page per coherent reviewed concept. Keep closely related synonyms/approved variants on the same page when they share the same boundaries. Split concepts when their inclusion/exclusion rules, governance or operational consequences differ materially.

A concept page should define meaning, not become a catch-all domain document.

## Storage/filename convention

Use descriptive kebab-case filenames. IDs are stable logical identities and do not need to mirror folder structure.

Example:

```text
_curated/business-concepts/reference-entity.md
id: atlas-concept.reference-data.entity
```

## Required frontmatter/type-specific fields

Start from `_template.md`. Use `type: atlas.business-concept`, the common curated envelope and:

```yaml
approved_definition: ""
inclusion_criteria: []
exclusion_criteria: []
approved_variants: []
```

The body may explain nuance; the frontmatter fields should remain concise and routable.

## Relationship guidance

Use only taxonomy-approved relationships.

Typical relationships include:

- `atlas.implemented-by` to components or contracts that materially implement the concept;
- `atlas.must-follow` to standards governing the concept's use;
- `atlas.extends` where one reviewed concept specialises another;
- `atlas.supersedes` when a new concept definition replaces an older one without erasing history;
- `atlas.informed-by` when reusable reviewed learning materially shaped the definition.

Do not create relationships merely because two terms appear near each other in source material.

## Evidence expectations

Prefer evidence that establishes approved meaning, such as:

- supplied business definitions;
- governed documentation or policy references;
- schema/data-contract documentation where semantics are explicit;
- Jira/Confluence/SharePoint references supplied as evidence;
- reviewer-confirmed SME statements;
- staging entries preserving original wording and provenance.

Code, column names and UI labels can support implementation mapping but should not silently define business meaning.

## `not covered` rule

When a required section lacks evidence, use exactly:

```markdown
*Not covered — no evidence in current staging material.*
```

Do not manufacture examples, exclusions or variants to make a definition look complete.

## Agent curation instructions

Before proposing a business-concept change, read this README, `_template.md` and `index.md`. Search by ID, aliases and semantic match to avoid duplicate definitions. Preserve original evidence, distinguish approved definition from observed usage, surface conflicts rather than reconciling them automatically, and keep implementation detail in linked component/schema pages.

## Reviewer checklist

Before approval, verify:

- the definition is clear enough to drive engineering decisions;
- inclusion and exclusion boundaries are explicit where needed;
- examples and non-examples actually follow the definition;
- aliases/variants are genuinely approved;
- implementation/data links do not substitute for semantic evidence;
- conflicts with existing concepts are resolved or surfaced;
- sensitive or policy-controlled source material is not copied unnecessarily;
- the page is indexed and relationships are evidence-backed.

## Index maintenance rule

Every non-archived business-concept page must appear in `index.md`. Archived pages remain available for history but are excluded from normal routing.

## Security/sensitivity reminder

Capture the minimum business context needed for engineering. Do not copy customer data, personal data, confidential case details, secrets or restricted source material. Link to authorised sources when the source itself should remain outside Atlas.
