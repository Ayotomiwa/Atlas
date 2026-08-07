---
name: atlas-discover
description: Use when answering a question about a TeamA system, service, flow, infrastructure, schema, runbook or standard. Route through curated Atlas before broad code scanning and label fallback clearly.
allowed-tools: Read, Grep, Glob
---

# atlas-discover

1. Locate Atlas root from this skill and read `package.md`.
2. Read the relevant root/curated index and route to the smallest concept/index/map set.
3. Use only `status: curated` as authoritative.
4. Cite Atlas page ID + path for Atlas-backed claims.
5. If not covered, say what is missing, then allow normal repository discovery outside this workflow and label scan-derived conclusions separately.
6. Never write staging, curated, maps, status or review files.
