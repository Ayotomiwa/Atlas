---
name: atlas-impact
description: Use after direct Ask Atlas or routing from a bound repository for change-risk, deletion, migration, failure, or blast-radius questions.
allowed-tools: Read, Grep, Glob, Bash, Agent
---

# atlas-impact

Read `../_shared/human-intents.md`, `../_shared/runtime.md`, `../_shared/answer-provenance.md`, and `../_shared/agent-handoffs.md`. This is the risk-focused **Ask Atlas** route and is read-only.

1. Start from the selected file, diff, artifact or current path. Resolve explicit IDs exactly; otherwise combine typed `find` with path context, preserve ambiguity and disclose any `not-verified` candidate before establishing the starting ID or external/unmapped boundary.
2. Delegate substantive analysis to `atlas-impact-analyst`. Inspect direct neighbors before transitive traversal. Default to downstream impact; add upstream analysis only for causes, prerequisites, recovery or an explicit request.
3. Separate confirmed, possible/conflicting, external and unknown impact. Preserve direction, depth, confidence, evidence and at least one material path for every result.
4. Open routed pages and bounded repository evidence where needed. State where Atlas coverage ended and what fallback checked. Never claim safety from an absent edge.
5. Present claim references plus `How this was traced`. Offer upstream analysis as a follow-up when useful but outside the current scope.

For an exact-change prompt, query `_staging/changes` with `python <ATLAS_ROOT>/scripts/atlas_query.py --root <ATLAS_ROOT> staging --bucket changes --include-terminal --source-key <source-key> --branch <branch> --from-exclusive <sha-or-start> --through-inclusive <sha> --format json` before completeness-sensitive source verification. Use the exact known immutable range, including terminal records; `--from-exclusive start` matches an explicit null start. `_staging/` records are non-authoritative routing and completeness evidence, never factual authority. Never substitute similarity for range identity.

Trigger semantic-risk change readiness regardless of diff size for an API, schema, event, data, or flow boundary; an AWS, IAM, account, environment, region, schedule, event-filter, monitoring, deployment, or rollback concern; or a standards, operations, recovery, or cross-repository boundary. A local isolated edit may stay at the targeted-source step only when evidence shows none of those semantics can escape it.

Readiness combines standards, conflicts, and exceptions; confirmed, possible, external, and unknown impact; incidents and runbooks; source-owned exact commands; and Atlas-owned testing, compatibility, deployment, and recovery obligations. Apply and report clear required standards. Reserve confirmation for exceptions, ambiguity, destructive or cross-team risk, or missing critical evidence.

Query traversal is a deterministic route through recorded facts, not proof that every possible dependency has been captured.

The user does not need to know that impact uses a separate specialist. Within an eligible direct-Ask or bound-repository route, recognise risk intent from ordinary language and present the engineering result first.
