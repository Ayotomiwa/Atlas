# Schema Info staging

## Purpose

`_staging/schema-info/` captures raw, attributable evidence about durable data/interface contracts before their physical and semantic meaning is reviewed.

Use it for tables, events, files, APIs, schemas or other contracts where Atlas may eventually need to describe grain, keys, temporal behaviour, producers, consumers, joins, quality or classification.

## Belongs here

Useful evidence includes:

- DDL, schema, IDL, OpenAPI/AsyncAPI or migration paths;
- table/topic/file/API identities;
- observed record/message grain;
- candidate primary/business keys;
- temporal/versioning behaviour;
- important fields and constraints;
- producer/consumer evidence;
- candidate joins with their source;
- quality limitations;
- classification/access notes;
- user/SME-supplied semantic explanations.

## Does not belong here

Do not use this bucket for:

- a business definition with no physical contract — use `_staging/business-concepts/`;
- full component onboarding — use `_staging/components/`;
- end-to-end process capture — use `_staging/flows/`;
- generated schema dumps with no reusable context;
- speculative joins/keys/consumers written as fact;
- production rows, customer records, secrets or sensitive sample payloads.

## Schema evidence rule

Keep **physical observation** separate from **business interpretation**. A column name, DTO or event field can establish shape; it may not establish approved meaning.

For keys, grain, latest-record rules and joins, record the evidence and the uncertainty explicitly. If a join appears in code but its business validity is unknown, capture it as observed usage or possible/unconfirmed rather than "approved".

A curation-ready record also explains the contract in practice: what crosses the boundary, who produces and consumes it, how identity/time/versioning behave, and what compatibility or lifecycle consequence follows from change. Do not make the curator reconstruct this meaning from a field inventory.

## Granularity

Stage one coherent asset/contract investigation per entry. A single entry may cover tightly coupled schema variants when the investigation treats them as one durable contract; split unrelated assets so curation provenance remains clear.

## Curation outcomes

A staged schema entry may update/create:

- `_curated/schema-info/`;
- linked components/flows where producer/consumer evidence exists;
- linked business concepts when approved meaning is separately evidenced;
- standards governing schema usage.

Staging does not approve joins, definitions or relationships.

## Immutability

After first commit, only top-level frontmatter `status` may change. The body, provenance, title, description, path and ID remain immutable; corrections require a follow-up staging record.

## Security and sensitivity

Do not stage real sensitive records, secrets, credentials or unnecessary personal data. Prefer structural examples with redacted/fake values and links to authorised source systems.
