# Bounded source analysis

Use this contract when an Atlas workflow inspects product source to establish behavior, architecture, or recorded rationale.

`runtime.md` owns routing, source boundaries, and fallback. `answer-provenance.md` owns authority, claim classifications, confidence, citations, and coverage reporting. This contract defines how to inspect and explain source. It does not create another evidence vocabulary.

## Hold the source boundary

Accept the product root, logical boundary, resolved revision or range, exclusions, and permitted references from the owning workflow.

- Inspect an immutable commit, range, or onboarding snapshot. Treat working-tree content separately unless its identity to that source state is established.
- Repository onboarding stays on its one selected snapshot and does not traverse history. A different owning workflow may supply an authorised immutable range for a history question.
- Stay inside the authorised boundary. Follow a shared, infrastructure, sibling, or external path only when the source explicitly references it and the owning workflow permits it.
- Reuse revision-compatible source already supplied in the handoff. Do not restart a broad scan for a narrower follow-up.
- Preserve missing, inaccessible, ambiguous, and conflicting evidence. Do not fill a gap from filenames, proximity, naming convention, or a likely design pattern.

Source inspection never makes a claim curated Atlas knowledge. Use the classifications and confidence rules from `answer-provenance.md`. For onboarding, retain its lens states and its `observed`, `user-confirmed`, `possible`, and `conflicting` claim states.

## Trace actual behavior

Start where the behavior starts: an entrypoint, request handler, command, consumer, scheduler, deployment hook, callback, or public API.

Follow the relevant path in execution order:

1. identify the trigger and incoming data;
2. locate parsing, validation, and representation changes;
3. identify the rules or decisions that run;
4. record state and configuration read;
5. record state changed;
6. follow external calls, messages, infrastructure actions, and later consumers;
7. identify outputs, durable effects, completion signals, retries, partial completion, and failure behavior;
8. locate operational signals, recovery routes, and source-owned guidance when they affect the result.

For asynchronous behavior, follow the event or message to the material consumer. For data-heavy behavior, record where the representation or ownership changes. Do not turn a local call chain into an end-to-end flow without evidence of its start, end, and participants.

Explain who owns each material rule, state transition, and boundary. Distinguish an independently addressable component from an internal module or grouping folder. A file list or dependency inventory is supporting evidence, not an architecture explanation.

Documentation supports documented or intended behavior. Use executable evidence appropriate to the claim when current wiring matters. Inspect only the tests, configuration, IaC, scripts, or runtime evidence needed to establish that claim.

## Recover recorded rationale

Current code establishes what is implemented at that revision. It does not by itself establish deployment or why the team chose it.

For a rationale or history question, follow the available authorised record from the relevant path or symbol into commit history and then into any linked change request, ticket, design document, standard, incident, or review discussion.

- Treat a reason as direct only when a source states it.
- Treat a reason assembled from premises as `Inference` and cite every material premise.
- Use `Unresolved` when the record does not support a reason.
- Do not infer that an incident caused a later change from chronology alone.
- Mention a rejected alternative only when the record shows that the team considered or previously implemented it.
- Preserve disagreement between proposed intent, shipped implementation, and later evidence.

For change analysis, keep the stated goal separate from the observed behavioral effect.

## Stop at a defensible boundary

Continue only while another known source route could materially change a claim, candidate boundary, confidence, coverage statement, or deferral decision.

Stop when every material claim has an evidence-bearing route or a recorded gap, and report:

- the entrypoint or trigger;
- the causal path and material representation changes;
- ownership, state, and system boundaries;
- outputs, failures, and operational effects;
- recorded rationale or its absence;
- exact source anchors and resolved revision;
- coverage limits and the stopping reason.

## Explain the result

Lead with the smallest complete explanation. Describe the behavior in domain terms before naming implementation details. Introduce a concept when the route first needs it.

Use real source names and examples. Call out non-obvious timing, derived values, indirect writes, retries, configuration-dependent paths, or split representations when they change the engineer's mental model.

Keep current implementation, documented intent, recorded rationale, inference, and recommendation separate. Do not present a recommendation as discovered architecture or persist it as evidence.
