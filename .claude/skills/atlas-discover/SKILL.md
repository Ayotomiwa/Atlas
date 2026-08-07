---
name: atlas-discover
description: >
  Use when answering a question about DataLens systems, components, flows,
  infrastructure, tables or standards. Routes through Atlas curated context
  before scanning code, and labels any answer Atlas does not cover.
allowed-tools: Read, Grep, Glob
---

# Atlas discover

1. Read `package.md`, then `_curated/index.md`.
2. Route through the relevant concept or domain index and open the smallest useful set of pages.
3. For impact questions, inspect `_curated/maps/`; for flow questions start with `flow-component-map.json`.
4. Cite the Atlas `id` and file path for every Atlas-backed claim.
5. Explicitly label anything not Atlas-backed and list what Atlas did not cover.
6. Never treat staging material as authoritative.
