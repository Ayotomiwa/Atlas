---
name: atlas-impact
description: Use after direct Ask Atlas or routing from a bound repository for change-risk, deletion, migration, failure, or blast-radius questions.
allowed-tools: Read, Grep, Glob, Bash, Agent
---

# atlas-impact

Read `../_shared/human-intents.md`, `../_shared/runtime.md`, `../_shared/answer-provenance.md`, `../_shared/agent-handoffs.md`, `../_shared/source-analysis.md`, `../_shared/change-risk-analysis.md`, and `../_shared/diagram-writing.md`. This is the risk-focused **Ask Atlas** route and is read-only.

1. Start from the selected file, diff, artifact or current path. Resolve explicit IDs exactly; otherwise combine typed `find` with path context, preserve ambiguity and disclose any `not-verified` candidate before establishing the starting ID or external/unmapped boundary.
2. Delegate every substantive or transitive impact analysis to `atlas-impact-analyst`. A one-record direct dependency lookup may stay local under the shared handoff definition and remains concise. Require the full risk packet only for a concrete change, deletion, migration, failure, or readiness scenario. Inspect direct neighbors before transitive traversal. Default to downstream impact; add upstream analysis only for causes, prerequisites, recovery or an explicit request.
3. Apply the shared change-risk contract. Separate confirmed, possible/conflicting, external and unknown impact. Preserve direction, depth, confidence, evidence and at least one material path for every result.
4. Open routed pages and bounded repository evidence where needed. State where Atlas coverage ended and what fallback checked. Never claim safety from an absent edge.
5. Present claim references plus `How this was traced`. For console output, prefer a plain-text route, small tree, or compact table; do not dump raw Mermaid unless requested or reliably rendered. Follow `diagram-writing.md` for any visual. Offer upstream analysis as a follow-up when useful but outside the current scope.

Apply the shared provenance rules to uncertainty, executable claims, source revision, source reuse, and coverage. Use the source-analysis contract for bounded fallback and the change-risk contract for behavioral change, safety facts, non-symbol effects, cleared concerns, unresolved boundaries, and the smallest settling check.

For an exact-change prompt, query `_staging/changes` with `python <ATLAS_ROOT>/scripts/atlas_query.py --root <ATLAS_ROOT> staging --bucket changes --include-terminal --source-key <source-key> --branch <branch> --from-exclusive <sha-or-start> --through-inclusive <sha> --format json` before completeness-sensitive source verification. Use the exact known immutable range, including terminal records; `--from-exclusive start` matches an explicit null start. `_staging/` records are non-authoritative routing and completeness evidence, never factual authority. Verify with referenced immutable evidence or the exact-range Git diff and history, including per-commit inspection when endpoint state is empty. An empty endpoint diff or current file does not prove no change: an add-then-revert sequence is net-zero but still material history. Never substitute similarity for range identity.

Trigger semantic-risk change readiness regardless of diff size for an API, schema, event, data, or flow boundary; an AWS, IAM, account, environment, region, schedule, event-filter, monitoring, deployment, or rollback concern; or a standards, operations, recovery, or cross-repository boundary. A local isolated edit may stay at the targeted-source step only when positive evidence shows none of those semantics can escape it.

Readiness combines standards, conflicts, and exceptions; confirmed, possible, external, and unknown impact; incidents and runbooks; source-owned exact commands; and Atlas-owned testing, compatibility, deployment, and recovery obligations. Apply and report clear required standards. Reserve confirmation for exceptions, ambiguity, destructive or cross-team risk, or missing critical evidence.

When the request needs a complete flow or readiness result and Atlas flow coverage is partial or uncertain, apply bounded source fallback under `source-analysis.md` to the missing flow edge. If the edge cannot be verified, preserve its confidence and report the readiness boundary as unresolved.

The user does not need to know that impact uses a separate specialist. Within an eligible direct-Ask or bound-repository route, recognise risk intent from ordinary language and present the engineering result first.
