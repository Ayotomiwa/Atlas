# Infra

## Purpose
Store governed `atlas.infra` knowledge.

## Trust level
Only `status: curated` is authoritative; proposed pages await human review.

## When to use this area
Use it for stable, reusable knowledge matching this concept type.

## When not to use it
Do not store raw evidence, secrets, routine logs, or unsupported assumptions.

## Granularity rule
Normally one meaningful infra package/template. Promote lower-level resources only when independently significant.

## Storage/filename convention
Use descriptive kebab-case Markdown filenames; IDs are stable logical identities and are not derived from paths.

## Required frontmatter/type-specific fields
Use `_template.md` and the taxonomy; preserve the common envelope and type-specific fields.

## Relationship guidance
Use only taxonomy relationship types. `consumes`, `produces`, and `depends-on` require a valid `kind`; keep uncertainty on each edge.

## Evidence expectations
Claims must cite staging evidence, repository paths, external references, or reviewer-confirmed sources.

## Not covered rule
Use exactly `*Not covered — no evidence in current staging material.*` when a required section has no evidence.

## Agent curation instructions
Read this README, `_template.md`, and `index.md` before editing. Create/update as `proposed`; do not self-approve.

## Reviewer checklist
Check evidence, granularity, relationship targets/types/confidence, coverage gaps, sensitivity, index entry, maps, lint and tests.

## Index maintenance rule
Every non-archived page must appear in the catalogue; archived pages are excluded from normal routing.

## Security/sensitivity reminder
Never capture secrets, credentials, customer data, raw sensitive logs/query output, or unnecessary personal data.
