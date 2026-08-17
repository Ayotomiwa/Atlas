---
name: atlas-discover
description: Use for natural datalens engineering questions where durable architecture, ownership, flows, infrastructure, schemas, standards, operations, or business meaning could improve the answer. Bypass Atlas for simple local-code questions.
---

# atlas-discover

Read `../_shared/human-intents.md`, `../_shared/runtime.md`, `answer-provenance.md` and `agent-handoffs.md`. This is the normal read-only **Ask Atlas** route.

1. Bypass Atlas when a simple answer is fully visible locally. If Atlas root is unavailable, state that it was not consulted and offer bounded repository inspection. Inside `ATLAS_ROOT`, distinguish stored engineering knowledge from questions about Atlas implementation.
2. Resolve an explicit stable ID directly. For stored knowledge while inside Atlas, run typed `find` without path context; for an external product use current-path context. Preserve ambiguity and disclose every `not-verified` product context used.
3. Open the selected curated page and follow its links. If a structured conflict matches, lead with both evidenced claims before its bounded interpretation. If candidates are weak or ambiguous, use the collection/domain index then the curated root index. Use maps only for reverse or multi-hop traversal.
4. Handle small lookups locally; delegate ambiguity, synthesis, traversal or substantial fallback to `atlas-discovery-analyst`.
5. When coverage ends, disclose the boundary and inspect bounded product source only from an available separate product checkout. Never use Atlas implementation as fallback for another product or offer setup for Atlas itself; never write from discovery.
6. Choose the clearest presentation, cite every material claim, and disclose answer-bearing hops.

Never write files, silently choose fuzzy matches, use staging/query output as authority, or infer absence from a missing connection.

Do not make the user select a query or specialist. Lead with the engineering answer and keep mechanics in compact provenance.
