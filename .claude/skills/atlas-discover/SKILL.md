---
name: atlas-discover
description: Use for direct Ask Atlas requests and bound-repository questions where durable architecture, ownership, flows, infrastructure, schemas, standards, operations, or business meaning could improve the answer.
allowed-tools: Read, Grep, Glob, Bash, Agent
---

# atlas-discover

Read `../_shared/human-intents.md`, `../_shared/runtime.md`, `../_shared/answer-provenance.md`, and `../_shared/agent-handoffs.md` before substantive work. This is the normal **Ask Atlas** route and is read-only.

1. Apply the shared binding matrix and ordered retrieval ladder. A known targeted read may answer a clearly local bound-repository question, but uncertain or broad lookup routes through Atlas first. When current path is inside `ATLAS_ROOT`, distinguish a stored-knowledge question from an Atlas-implementation question using the shared runtime contract.
2. Validate Atlas root. If unavailable, state that Atlas was not consulted, give the `claude --add-dir <path-to-current-Atlas-checkout>` recovery, and offer bounded local inspection.
3. Resolve an explicit stable ID directly. In stored-knowledge mode inside Atlas, infer likely record types and run typed `find` without path context; in an external product checkout use current-path context. Treat up to three results as candidates; disclose and preserve ambiguity and every `not-verified` product context used.
4. For a **Direct Ask Atlas**, consult all relevant curated types, follow answer-bearing links, and synthesize all supported material. Then answer, guide the smallest next evidence location, or report an unresolved boundary. If a structured conflict matches, lead with both evidenced claims before the page's bounded interpretation. If search is weak or ambiguous, consult the relevant collection/domain index, then the curated root index. Use maps only for reverse or multi-hop traversal after selection.
5. Handle a small direct lookup locally. Delegate synthesis, unresolved ambiguity, traversal or substantial source fallback to `atlas-discovery-analyst` with the shared handoff contract.
6. If coverage is insufficient, disclose the endpoint and continue with bounded product-source inspection only when a separate product checkout is available; read-only fallback is automatic when the repository and authorised boundary are unambiguous. Never scan Atlas implementation as fallback evidence for another product. Query failure is not evidence of absent knowledge.
7. When an external Atlas-relevant product repository lacks a valid managed `CLAUDE.md` block, offer `atlas-setup-repo` once per repository/session without delaying the answer. Never offer setup for Atlas itself.
8. Choose the clearest evidence-bearing presentation and cite every material claim and file hop.

Treat Atlas connections marked possible, unconfirmed, or conflicting as coverage limits; never promote them to confirmed. Curated page authority never upgrades an individual field or edge confidence. When a definitive, executable, or complete claim depends on one, qualify the claim or perform the smallest source verification of precisely the uncertain edge. Treat external targets and unknown coverage as separate states and preserve them as external or unresolved. Exact volatile values are source-authoritative, including commands, code, configuration, and IaC literals.

Repository documentation alone supports documented or intended behavior; it does not confirm executable or deployed wiring. Verify with current executable or deployed evidence appropriate to the boundary, such as code, configuration, IaC, tests, or runtime/control-plane state.

When already verified repository evidence remains current and supports every material follow-up claim at the required confidence, a follow-up may use it with zero new retrieval; do not force fallback merely because the original Atlas edge was possible; related evidence must not upgrade a different uncertain edge.

For a flow question, synthesize trigger and outcome; start and end boundaries; system boundaries; ordered participants and handoffs; data and infrastructure transitions; conditional, retry, and failure paths; standards, incidents, and runbooks; and coverage limits from the existing model. Do not reduce the answer to a list of matched records.

When the request needs a complete flow or readiness result and Atlas coverage is partial or uncertain, perform a bounded source fallback for the missing flow edge rather than presenting the partial route as complete. If that edge cannot be verified, keep it qualified and state the unresolved boundary.

Do not expose query or skill selection as work the user must perform. Lead with the answer; put route mechanics in the compact provenance section.

Never write Atlas or product files. Never silently select a search/path candidate, use staging as authority, paste query output as the answer, or treat a missing result/connection as evidence of absence.
