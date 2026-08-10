---
name: atlas-discover
description: Use when answering a question about a TeamA system, repository, component, flow, infrastructure, schema, runbook or standard. Route through curated Atlas before broad code scanning and label fallback clearly.
allowed-tools: Read, Grep, Glob, Bash
---

# atlas-discover

Use this as the read-only consumer route for TeamA engineering context.

1. When the package is already known, route directly by stable ID, map, or curated index. Read `atlas-package.json` only for package discovery, domain definitions, or registered paths; it is not an obligatory navigation hop.
2. Prefer `python scripts/atlas_query.py resolve <id>` or `python scripts/atlas_query.py route <id>`. Use the smallest relevant domain index when no stable ID is known.
3. Use the generated `flows`, `repositories`/`components`, or `packages`/`resources` collections for routing. Open linked pages only for narrative meaning, detailed evidence, operational context, or open questions.
4. If a record is not mapped, search for its exact stable ID or use its domain index. Never silently select an ambiguous title match.
5. Treat only `_curated/` pages with `status: curated` as authoritative. A local working branch may contain intentionally new curated proposals; heed the query tool's governed-branch warning and distinguish local routing from governed authority.
6. For Atlas-backed claims, report the page ID and repository-relative path. Never use `_staging/` as authoritative knowledge.
7. If curated Atlas does not cover the question, state exactly what is missing. A normal repository scan may then be used, clearly labelled repository-derived.
8. Never write staging, curated, map, status, review, or product-repository files.

If evidence is absent, say `not covered`; do not turn absence of an Atlas connection into proof that a dependency does not exist.
