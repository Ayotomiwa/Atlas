---
name: atlas-impact
description: Use for blast-radius questions such as what may break when a TeamA component, flow, schema or infrastructure item changes, fails or is deleted.
allowed-tools: Read, Grep, Glob
---

# atlas-impact

This is a read-only impact-analysis workflow.

1. Resolve the Atlas package from `package.md` and locate the starting concept by ID, alias, repository, or relevant curated index.
2. Read the starting curated page and preserve its relationship confidence.
3. Open the relevant generated map from `_curated/maps/` and traverse both forward and derived reverse edges.
4. Follow only the smallest useful set of linked flows, components, schema assets and infrastructure pages.
5. Bucket results as **known affected**, **possibly affected**, and **unknown or not covered**.
6. Cite the supporting Atlas page ID/path and relationship evidence for each material result.
7. Never claim `not affected` merely because a relationship is absent.
8. Never write Atlas, product files, status, reviews, or maps.

If the starting concept is not covered by curated Atlas, report that limitation rather than constructing a confident graph from staging evidence.
