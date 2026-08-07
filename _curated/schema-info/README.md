# Schema Info policy

## Purpose
Curated durable data/interface contract knowledge.
## Trust level
Only curated status is authoritative.
## When to use this area
Tables, events, files, APIs, schemas and durable data contracts.
## When not to use it
Do not store transient query output or unsupported data meaning.
## Granularity rule
One page per meaningful durable asset/contract.
## Storage/filename convention
Descriptive filenames; stable IDs.
## Required frontmatter/type-specific fields
Use `_template.md` and `atlas.schema-info`.
## Relationship guidance
Capture producers/consumers with typed, evidenced relationships.
## Evidence expectations
Trace physical/business meaning to evidence.
## `not covered` rule
Use exact not-covered marker where evidence is absent.
## Agent curation instructions
Read README/template/index before proposing.
## Reviewer checklist
Check grain, keys, temporal model, classification and evidence.
## Index maintenance rule
Index non-archived pages.
## Security/sensitivity reminder
Do not copy sensitive data samples unnecessarily.
