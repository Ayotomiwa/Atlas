---
name: atlas-impact
description: Use after direct Ask Atlas or routing from a bound repository for change-risk, deletion, migration, failure, or blast-radius questions.
---

# atlas-impact

Read `../_shared/human-intents.md`, `../_shared/runtime.md`, `answer-provenance.md` and `agent-handoffs.md`. This is the risk-focused read-only **Ask Atlas** route.

1. Start from the file/diff/artifact/current path. Resolve explicit IDs exactly; otherwise combine typed `find` with path context, preserve ambiguity and disclose `not-verified` candidates before establishing the starting boundary.
2. Delegate substantive analysis to `atlas-impact-analyst`. Inspect direct neighbors before transitive traversal. Default downstream; include upstream only for causes, prerequisites, recovery or explicit request.
3. Separate confirmed, possible/conflicting, external and unknown impact. Preserve direction, depth, confidence, evidence and one material path per result.
4. Cite claims and disclose every material hop plus the Atlas-to-source fallback boundary. Never claim safety from absence. Offer upstream analysis when useful but outside scope.

For an exact-change prompt, query `_staging/changes` with `python <ATLAS_ROOT>/scripts/atlas_query.py --root <ATLAS_ROOT> staging --bucket changes --include-terminal --source-key <source-key> --branch <branch> --from-exclusive <sha-or-start> --through-inclusive <sha> --format json` before completeness-sensitive source verification. Use the exact known immutable range, including terminal records; `--from-exclusive start` matches an explicit null start. `_staging/` records are non-authoritative routing and completeness evidence, never factual authority. Verify with referenced immutable evidence or the exact-range Git diff and history, including per-commit inspection when endpoint state is empty. An empty endpoint diff or current file does not prove no change: an add-then-revert sequence is net-zero but still material history. Never substitute similarity for range identity.

Trigger semantic-risk change readiness regardless of diff size for an API, schema, event, data, or flow boundary; an AWS, IAM, account, environment, region, schedule, event-filter, monitoring, deployment, or rollback concern; or a standards, operations, recovery, or cross-repository boundary. A local isolated edit may stay at the targeted-source step only when evidence shows none of those semantics can escape it.

Readiness combines standards, conflicts, and exceptions; confirmed, possible, external, and unknown impact; incidents and runbooks; source-owned exact commands; and Atlas-owned testing, compatibility, deployment, and recovery obligations. Apply and report clear required standards. Reserve confirmation for exceptions, ambiguity, destructive or cross-team risk, or missing critical evidence.

Within an eligible direct-Ask or bound-repository route, recognise risk intent from ordinary language; the user need not know this is a separate specialist workflow.
