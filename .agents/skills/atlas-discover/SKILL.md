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

Treat Atlas connections marked possible, unconfirmed, or conflicting as coverage limits; never promote them to confirmed. Curated page authority never upgrades an individual field or edge confidence. When a definitive, executable, or complete claim depends on one, qualify the claim or perform the smallest source verification of precisely the uncertain edge. Treat external targets and unknown coverage as separate states and preserve them as external or unresolved. Exact volatile values are source-authoritative, including commands, code, configuration, and IaC literals.

Repository documentation alone supports documented or intended behavior; it does not confirm executable or deployed wiring. Verify with current executable or deployed evidence appropriate to the boundary, such as code, configuration, IaC, tests, or runtime/control-plane state.

When already verified repository evidence remains current and supports every material follow-up claim at the required confidence, a follow-up may use it with zero new retrieval; do not force fallback merely because the original Atlas edge was possible; related evidence must not upgrade a different uncertain edge.

For a flow question, synthesize trigger and outcome; start and end boundaries; system boundaries; ordered participants and handoffs; data and infrastructure transitions; conditional, retry, and failure paths; standards, incidents, and runbooks; and coverage limits from the existing model. Do not reduce the answer to a list of matched records.

When the request needs a complete flow or readiness result and Atlas coverage is partial or uncertain, perform a bounded source fallback for the missing flow edge rather than presenting the partial route as complete. If that edge cannot be verified, keep it qualified and state the unresolved boundary.

Never write files, silently choose fuzzy matches, use staging/query output as authority, or infer absence from a missing connection.

Do not make the user select a query or specialist. Lead with the engineering answer and keep mechanics in compact provenance.
