---
name: atlas-impact
description: Use for explicit datalens change-risk, deletion, migration, failure, or blast-radius questions involving a file, repository, component, flow, schema, or infrastructure item.
---

# atlas-impact

Read `../_shared/human-intents.md`, `../_shared/runtime.md`, `answer-provenance.md` and `agent-handoffs.md`. This is the risk-focused read-only **Ask Atlas** route.

1. Start from the file/diff/artifact/current path. Resolve explicit IDs exactly; otherwise combine typed `find` with path context, preserve ambiguity and disclose `not-verified` candidates before establishing the starting boundary.
2. Delegate substantive analysis to `atlas-impact-analyst`. Inspect direct neighbors before transitive traversal. Default downstream; include upstream only for causes, prerequisites, recovery or explicit request.
3. Separate confirmed, possible/conflicting, external and unknown impact. Preserve direction, depth, confidence, evidence and one material path per result.
4. Cite claims and disclose every material hop plus the Atlas-to-source fallback boundary. Never claim safety from absence. Offer upstream analysis when useful but outside scope.

Recognise risk intent from ordinary language; the user need not know this is a separate specialist workflow.
