---
name: atlas-discover
description: Use for direct Ask Atlas requests and bound-repository questions where durable architecture, ownership, flows, infrastructure, schemas, standards, operations, or business meaning could improve the answer.
---

# atlas-discover

Read `../_shared/human-intents.md`, `../_shared/runtime.md`, `answer-provenance.md` and `agent-handoffs.md`. This is the normal read-only **Ask Atlas** route.

1. Apply the shared binding matrix and ordered retrieval ladder. A known targeted read may answer a clearly local bound-repository question, but uncertain or broad lookup routes through Atlas first. If Atlas root is unavailable, state that it was not consulted and offer bounded repository inspection. Inside `ATLAS_ROOT`, distinguish stored engineering knowledge from questions about Atlas implementation.
2. Resolve an explicit stable ID directly. For stored knowledge while inside Atlas, run typed `find` without path context; for an external product use current-path context. Preserve ambiguity and disclose every `not-verified` product context used.
3. For a **Direct Ask Atlas**, consult all relevant curated types, follow answer-bearing links, and synthesize all supported material. Then answer, guide the smallest next evidence location, or report an unresolved boundary. If a structured conflict matches, lead with both evidenced claims before its bounded interpretation. If candidates are weak or ambiguous, use the collection/domain index then the curated root index. Use maps only for reverse or multi-hop traversal.
4. Handle small lookups locally; delegate ambiguity, synthesis, traversal or substantial fallback to `atlas-discovery-analyst`.
5. When coverage ends, disclose the boundary and inspect bounded product source only from an available separate product checkout; read-only fallback is automatic when the repository and authorised boundary are unambiguous. Never use Atlas implementation as fallback for another product or offer setup for Atlas itself; never write from discovery.
6. Choose the clearest presentation, cite every material claim, and disclose answer-bearing hops.

For a flow question, synthesize trigger and outcome; start and end boundaries; system boundaries; ordered participants and handoffs; data and infrastructure transitions; conditional, retry, and failure paths; standards, incidents, and runbooks; and coverage limits from the existing model. Do not reduce the answer to a list of matched records.

Never write files, silently choose fuzzy matches, use staging/query output as authority, or infer absence from a missing connection.

Do not make the user select a query or specialist. Lead with the engineering answer and keep mechanics in compact provenance.
