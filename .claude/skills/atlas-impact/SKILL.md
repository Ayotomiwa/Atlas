---
name: atlas-impact
description: Use for explicit datalens change-risk, deletion, migration, failure, or blast-radius questions involving a file, repository, component, flow, schema, or infrastructure item.
allowed-tools: Read, Grep, Glob, Bash, Agent
---

# atlas-impact

Read `../_shared/human-intents.md`, `../_shared/runtime.md`, `../_shared/answer-provenance.md`, and `../_shared/agent-handoffs.md`. This is the risk-focused **Ask Atlas** route and is read-only.

1. Start from the selected file, diff, artifact or current path. Resolve explicit IDs exactly; otherwise combine typed `find` with path context, preserve ambiguity and disclose any `not-verified` candidate before establishing the starting ID or external/unmapped boundary.
2. Delegate substantive analysis to `atlas-impact-analyst`. Inspect direct neighbors before transitive traversal. Default to downstream impact; add upstream analysis only for causes, prerequisites, recovery or an explicit request.
3. Separate confirmed, possible/conflicting, external and unknown impact. Preserve direction, depth, confidence, evidence and at least one material path for every result.
4. Open routed pages and bounded repository evidence where needed. State where Atlas coverage ended and what fallback checked. Never claim safety from an absent edge.
5. Present claim references plus `How this was traced`. Offer upstream analysis as a follow-up when useful but outside the current scope.

Query traversal is a deterministic route through recorded facts, not proof that every possible dependency has been captured.

The user does not need to know that impact uses a separate specialist. Recognise the risk intent from ordinary language and present the engineering result first.
