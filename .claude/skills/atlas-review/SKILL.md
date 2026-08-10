---
name: atlas-review
description: Review Atlas staging IDs, curated IDs, paths, diffs, or commit ranges for evidence, trust, granularity, provenance, generated projection, and validation problems without editing or approving.
allowed-tools: Read, Grep, Glob, Bash, Agent
---

# atlas-review

Read `../_shared/runtime.md`, `../_shared/answer-provenance.md`, and `../_shared/agent-handoffs.md`. This workflow is read-only.

1. Resolve the requested staging IDs, curated IDs, paths, diff or commit range and identify original evidence plus affected generated surfaces.
2. Delegate independent inspection to `atlas-reviewer` with the full scope, original evidence, changed pages and validation deferrals.
3. Report blockers, major findings, minor findings, open decisions, validation state and residual risk. Every finding cites exact changed paths/lines and the original evidence it contradicts or fails to support.
4. When relevant, disclose the route from staging evidence through curated page to generated projection.

Never edit, approve, merge, commit or publish. An empty findings list is not an approval.
