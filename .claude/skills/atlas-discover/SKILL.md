---
name: atlas-discover
description: Use for natural TeamA engineering questions where durable architecture, ownership, flows, infrastructure, schemas, standards, operations, or business meaning could improve the answer. Bypass Atlas for simple local-code questions.
allowed-tools: Read, Grep, Glob, Bash, Agent
---

# atlas-discover

Read `../_shared/runtime.md`, `../_shared/answer-provenance.md`, and `../_shared/agent-handoffs.md` before substantive work. This is read-only.

1. Decide whether Atlas can add durable cross-file or cross-system context. For a simple local explanation whose answer is fully visible in the supplied file, answer locally with repository references.
2. Otherwise run `atlas_query.py context <current-path>`. Treat path matches as candidates and state any selection or ambiguity. Use exact IDs, `resolve`, `neighbors`, `route`, and registered indexes/maps only after context resolution.
3. Handle a small, direct cache lookup in the main skill. Delegate synthesis, ambiguity, multi-hop traversal or substantial source fallback to `atlas-discovery-analyst` with the shared handoff contract.
4. Open curated pages for semantics, evidence context, questions or operational detail. If coverage is insufficient, disclose the endpoint and continue with bounded product-source inspection inside the user's scope.
5. Let the evidence determine whether prose, a table, route list or Mermaid is clearest. Every substantive answer must have claim-level references and disclose all material Atlas/source hops.

Never write Atlas or product files. Never silently select a fuzzy title or path candidate, use staging as authority, paste query output as the answer, or treat a missing connection as evidence of absence.
