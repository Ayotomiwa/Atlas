---
name: atlas-discover
description: Use when answering a question about a TeamA system, service, flow, infrastructure, schema, runbook or standard. Route through curated Atlas before broad code scanning and label fallback clearly.
allowed-tools: Read, Grep, Glob
---

# atlas-discover

1. Locate the Atlas root from this skill and read `package.md`.
2. Read the root and smallest relevant curated index.
3. Route to the smallest useful concept/index/map set.
4. Treat only `status: curated` as authoritative.
5. Cite Atlas page ID + path for Atlas-backed claims.
6. If not covered, state what is missing before normal repo discovery.
7. Label scan-derived conclusions separately.
8. Never write Atlas files.
