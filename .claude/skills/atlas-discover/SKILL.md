---
name: atlas-discover
description: Use when answering a question about a TeamA system, service, flow, infrastructure, schema, runbook or standard. Route through curated Atlas before broad code scanning and label fallback clearly.
allowed-tools: Read, Grep, Glob
---

# atlas-discover

Use this as the read-only consumer route for TeamA engineering context.

1. Resolve the Atlas root from this skill's location and read `package.md`.
2. Read the root `index.md`, then only the curated index relevant to the question.
3. Route to the smallest useful set of concept pages and generated maps; do not read the whole Atlas repository.
4. Treat only `_curated/` pages with `status: curated` as authoritative. `draft` and `proposed` pages may explain coverage gaps but are not authoritative claims.
5. For Atlas-backed claims, report the page ID and repository-relative path.
6. Never use `_staging/` as authoritative knowledge.
7. If curated Atlas does not cover the question, state exactly what is missing. The active agent may then perform normal repository discovery outside this skill workflow if it has access.
8. Label any scan-derived conclusion as repository-derived rather than Atlas-backed.
9. Never write staging, curated, map, status, review, or product-repository files.

If evidence is absent, say `not covered`; do not turn absence of an Atlas edge into proof that a dependency does not exist.
