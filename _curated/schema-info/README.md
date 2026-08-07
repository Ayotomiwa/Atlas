# Schema Info policy

## Purpose

`_curated/schema-info/` stores reviewed knowledge about durable data and interface contracts: tables, events, files, APIs, schemas and other assets whose structure or semantics engineers need to understand safely.

A schema-info page should help answer: **what is this asset, what does one record/message represent, how is it identified over time, who produces or consumes it, and what usage constraints matter?**

## Trust level

Only pages with `status: curated` are authoritative TeamA knowledge. `draft` and `proposed` pages are reviewable proposals. A schema definition found in code or staging evidence is not automatically an approved business interpretation.

## When to use this area

Use a schema-info page for stable, reusable knowledge about a durable contract or data asset, including:

- physical identity and platform;
- record/message grain;
- primary and business keys;
- temporal/versioning behaviour;
- important fields and meaning;
- known producers and consumers;
- reviewed joins or compatibility relationships;
- known quality limitations;
- classification and access constraints.

## When not to use it

Do not use schema-info for:

- raw schema dumps or generated DDL with no reusable explanation — link to the source instead;
- a business term with no physical contract — use `_curated/business-concepts/`;
- an end-to-end process — use `_curated/flows/`;
- component implementation detail — use `_curated/components/`;
- speculative joins or inferred consumers presented as fact;
- secrets, production extracts, customer records or sensitive sample payloads.

## Granularity rule

Create one page per durable schema/table/event/file/API/data-contract concept that engineers can identify and reason about independently. Group tightly coupled variants on one page when they share meaning and lifecycle; split when the contracts have materially different grain, ownership, compatibility, access or consumers.

Do not create a page for every transient DTO, internal class or intermediate object unless it is a durable interface that matters outside its immediate implementation.

## Storage/filename convention

Use descriptive kebab-case filenames. Grouping folders may be used for useful routing, but IDs remain stable logical identities and are not derived from the physical path.

Example:

```text
_curated/schema-info/reference-data/reference-store.md
id: atlas-schema.reference-data.reference-store
```

## Required frontmatter/type-specific fields

Start from `_template.md`. Use `type: atlas.schema-info`, the common curated envelope and:

```yaml
asset_kind: unknown
physical_name: ""
platform: ""
grain: ""
primary_keys: []
business_keys: []
temporal_model: unknown
latest_record_rule: ""
classification: unknown
```

Do not use a page-level confidence field. Confidence belongs on individual relationships.

## Relationship guidance

Use only relationships defined in `taxonomy/relationships.yaml`.

Common schema relationships include:

- `atlas.produces` from a component/flow to a durable asset;
- `atlas.consumes` from a component/flow to an asset;
- `atlas.implemented-by` when a business concept/contract is materially implemented by a component;
- `atlas.depends-on` for durable contract dependencies;
- `atlas.must-follow` for governing standards;
- `atlas.supersedes` for replacement contracts where history must remain visible.

A join described in the page body is **not** automatically a relationship edge. Treat joins as approved only when evidence supports the keys, grain compatibility and intended usage.

## Evidence expectations

Material claims should be traceable to sources such as:

- DDL/schema/IDL/OpenAPI/AsyncAPI or contract files;
- repository and config paths;
- migration definitions;
- producer/consumer code;
- data catalogue or platform references;
- staging evidence;
- approved business definitions;
- reviewer-confirmed statements.

For field meaning, grain, latest-record logic and joins, code shape alone may be insufficient. Keep semantic claims unconfirmed until an appropriate source supports them.

## `not covered` rule

When a required section genuinely has no evidence, use exactly:

```markdown
*Not covered — no evidence in current staging material.*
```

Unknown is preferable to an invented key, grain, consumer or interpretation.

## Agent curation instructions

Before proposing a schema-info change, read this README, `_template.md` and `index.md`. Search existing pages by ID, alias, physical name, repository path and semantic match. Reconcile physical evidence separately from business meaning, preserve uncertainty, and never invent producer/consumer or join relationships. Update the index and any relationship-generated maps through the normal curation workflow.

## Reviewer checklist

Before approval, verify:

- the asset is durable enough for Atlas;
- physical identity and platform are correct;
- grain is explicit and evidenced;
- key semantics and temporal model are not guessed;
- producers/consumers are supported;
- joins are safe for the stated grains and keys;
- quality/access notes are useful without exposing sensitive data;
- uncertainty and coverage limits are explicit;
- the page is indexed and relationships resolve correctly.

## Index maintenance rule

Every non-archived schema-info page must appear in `index.md`. Archived pages remain in Git/history but are excluded from normal routing.

## Security/sensitivity reminder

Record classification and access constraints, not sensitive data itself. Never paste credentials, production rows, raw customer data, private tokens, secrets or unnecessary personal data. Prefer authorised links and structural examples with redacted values.
