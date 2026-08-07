# Schema Info policy

## Purpose
Store curated schema info knowledge.
## Trust level
Only `status: curated` is authoritative; proposed pages require human review.
## When to use this area
Use for stable, reusable knowledge matching this concept type.
## When not to use it
Do not store raw evidence, secrets, routine logs or unsupported claims.
## Granularity rule
one durable schema, table, event, file, API or data-contract concept.
## Storage/filename convention
Use descriptive kebab-case filenames; IDs are stable logical identities and do not have to match paths.
## Required frontmatter/type-specific fields
Use `_template.md` and type `atlas.schema-info`.
## Relationship guidance
Use only taxonomy-approved relationships; preserve confidence and evidence.
## Evidence expectations
Every material claim should be traceable to staging, repository paths, external references, or reviewer-confirmed sources.
## `not covered` rule
Use exactly `*Not covered — no evidence in current staging material.*` when a required body section lacks evidence.
## Agent curation instructions
Read this README, `_template.md`, and `index.md` before proposing changes. Never self-approve.
## Reviewer checklist
Check evidence, granularity, IDs, relationships, uncertainty, index/map/status updates and sensitive data.
## Index maintenance rule
Every non-archived governed page must appear in `index.md`; archived pages stay out of normal routing.
## Security/sensitivity reminder
Never introduce credentials, customer data, raw sensitive logs or unnecessary personal data.
