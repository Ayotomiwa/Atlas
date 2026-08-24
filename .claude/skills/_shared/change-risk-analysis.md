# Change and risk analysis

Use this contract for change, deletion, migration, failure, readiness, and blast-radius analysis.

Read `source-analysis.md` when source inspection is required. `answer-provenance.md` owns authority, confidence, claim classifications, citations, and coverage reporting. Keep Atlas's existing impact groups: confirmed, possible or conflicting, external, and unknown or not covered.

## Establish the behavioral change

Start from the exact file, diff, artifact, commit, or immutable range supplied by the owning workflow.

Describe what behavior, contract, state, timing, configuration, or operation changed. Include behavior removed implicitly. Diff size does not determine risk.

For a commit range, inspect material commits as well as endpoint state when an add-then-revert sequence or another net-zero change could matter. Never substitute a similar change or current file state for the selected range.

## State the safety facts

Write the conditions that must hold for the change to be safe. Examples include:

- every caller accepts the new absence or variant;
- persisted data remains readable across deployment order;
- no external consumer requires the removed field;
- duplicate delivery remains harmless;
- cleanup still runs before a dependent resource disappears.

Support each safety fact through the existing Atlas or repository classifications. If the available evidence cannot establish it, keep it `Unresolved` and state the smallest evidence needed to settle it.

For each safety fact, identify the available proof: a traced Atlas or repository path, an automated check, a runtime observation, or none. A stated assumption is not proof and remains `Unresolved`.

Do not infer safety from a missing Atlas connection, an empty query result, or the absence of a symbol in one repository.

## Trace beyond direct references

Inspect direct callers, imports, implementations, tests, configuration, and wiring first. Then follow effects that may not share a symbol:

- serialized fields, schemas, database rows, migrations, files, cache keys, and generated contracts;
- APIs, events, queues, topics, webhooks, RPCs, commands, and external consumers;
- startup, shutdown, cleanup, retries, timeouts, ordering, transactions, and concurrent access;
- feature flags, tenant settings, environments, regions, accounts, deployment modes, and pinned library behavior;
- shared state, locks, counters, checkpoints, branches, and other multi-writer targets;
- downstream state changes, later reads, operational behavior, and user-visible effects.

Check deleted behavior through dynamic references, configuration, documentation that defines an external contract, scripts, migrations, and operational tooling when relevant.

Use Atlas to route through recorded facts. Query and map traversal do not prove that every dependency was captured. At the Atlas coverage endpoint, inspect only the smallest authorised source boundary that can establish the missing edge. Preserve likely external consumers as external when their source is unavailable.

## Assess impact

For every material result, record:

- what changes, fails, or becomes uncertain;
- the causal route from the selected change;
- direction and traversal depth;
- supporting evidence, confidence, and lifecycle;
- the coverage limit;
- the smallest check that would settle any remaining uncertainty.

Keep confirmed impact, possible or conflicting impact, external impact, and unknown or not-covered areas separate.

For each credible risk, describe likelihood and consequence separately when evidence supports them. Otherwise keep the rating `Unresolved`; do not derive likelihood from diff size, connection confidence, or traversal depth.

List checked concerns that evidence ruled out under `Cleared concerns`. A concern is cleared only when direct evidence or a traced path establishes why it cannot fail. A search with no result may define a checked boundary, but it does not clear unknown external use.

Include applicable standards, conflicts, exceptions, incidents, runbooks, and testing, compatibility, deployment, monitoring, rollback, or recovery obligations when they change readiness.

## Require the right proof

Inspect whether an existing test, CI result, source check, or runtime observation exercises each material safety fact. A passing build does not prove behavior that it never tests.

When proof is missing, state the smallest useful test, reproduction, source inspection, or control-plane observation. Never claim that a test ran or runtime behavior was verified unless the available evidence shows it.

## Return a proportionate risk packet

For a material change, deletion, migration, failure, or readiness scenario, return:

1. behavioral change;
2. safety facts;
3. confirmed impact;
4. possible or conflicting impact;
5. external impact;
6. unknown or not-covered areas;
7. cleared concerns;
8. unresolved safety facts and the smallest proof needed;
9. testing, compatibility, deployment, and recovery obligations;
10. the standard claim ledger, route hops, consulted paths, and coverage limits.

For a small isolated change, compress the packet, but retain every material safety fact and unresolved boundary. For an ordinary dependency lookup without a concrete change, deletion, migration, or failure scenario, answer concisely and do not manufacture a readiness packet.

This contract is read-only. It does not author code, stage evidence, curate knowledge, approve readiness, or publish a change.
