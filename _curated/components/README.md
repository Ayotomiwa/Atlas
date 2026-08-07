# Components policy

## Purpose
Curated component knowledge.
## Trust level
Only `status: curated` is authoritative; proposed pages require human review.
## When to use this area
Meaningful repos, services, deployable units, scheduled job groups or reusable libraries.
## When not to use it
Do not store raw evidence, routine logs, secrets, or unsupported claims.
## Granularity rule
One page per meaningful repo/service/deployable/job group/reusable library; do not split every handler or script by default.
## Storage/filename convention
Descriptive kebab-case filenames; IDs are stable logical identities, not path checksums.
## Required frontmatter/type-specific fields
Use `_template.md` and `type: atlas.component`.
## Relationship guidance
Use taxonomy-approved typed relationships with confidence and evidence.
## Evidence expectations
Trace material claims to staging, repository paths, external references or reviewer-confirmed sources.
## `not covered` rule
Use exactly `*Not covered — no evidence in current staging material.*` when evidence is absent.
## Agent curation instructions
Read this README, `_template.md`, and `index.md` before proposing changes; never self-approve.
## Reviewer checklist
Check evidence, granularity, IDs, relationships, uncertainty, index/map/status updates and sensitive data.
## Index maintenance rule
Every non-archived page belongs in `index.md`; archived pages stay out of normal routing.
## Security/sensitivity reminder
Never introduce credentials, customer data, raw sensitive logs or unnecessary personal data.
