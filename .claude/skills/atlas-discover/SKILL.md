---
name: atlas-discover
description: Use for natural datalens engineering questions where durable architecture, ownership, flows, infrastructure, schemas, standards, operations, or business meaning could improve the answer. Bypass Atlas for simple local-code questions.
allowed-tools: Read, Grep, Glob, Bash, Agent
---

# atlas-discover

Read `../_shared/human-intents.md`, `../_shared/runtime.md`, `../_shared/answer-provenance.md`, and `../_shared/agent-handoffs.md` before substantive work. This is the normal **Ask Atlas** route and is read-only.

1. Decide whether Atlas can add durable cross-file or cross-system context. Answer a fully local simple explanation from repository evidence.
2. Validate Atlas root. If unavailable, state that Atlas was not consulted, give the `claude --add-dir <path-to-current-Atlas-checkout>` recovery, and offer bounded local inspection.
3. Resolve an explicit stable ID directly. Otherwise infer likely record types and run typed `find` with current path. Treat up to three results as candidates; disclose and preserve ambiguity and every `not-verified` context used.
4. Open the selected curated page and follow linked routes. If a structured conflict matches, lead with both evidenced claims before the page's bounded interpretation. If search is weak or ambiguous, consult the relevant collection/domain index, then the curated root index. Use maps only for reverse or multi-hop traversal after selection.
5. Handle a small direct lookup locally. Delegate synthesis, unresolved ambiguity, traversal or substantial source fallback to `atlas-discovery-analyst` with the shared handoff contract.
6. If coverage is insufficient, disclose the endpoint and continue with bounded product-source inspection. Query failure is not evidence of absent knowledge.
7. When an Atlas-relevant product repository lacks a valid managed `CLAUDE.md` block, offer `atlas-setup-repo` once per repository/session without delaying the answer or writing automatically.
8. Choose the clearest evidence-bearing presentation and cite every material claim and file hop.

Do not expose query or skill selection as work the user must perform. Lead with the answer; put route mechanics in the compact provenance section.

Never write Atlas or product files. Never silently select a search/path candidate, use staging as authority, paste query output as the answer, or treat a missing result/connection as evidence of absence.
