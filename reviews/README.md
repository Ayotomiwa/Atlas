# Reviews

## Purpose

`reviews/` records the reasoning and human-review boundary between raw staging evidence and governed curated knowledge.

A review record should make it possible to reconstruct **what evidence was considered, what claims were accepted or rejected, why relationships were proposed, what validation ran, and what a human ultimately decided** without rewriting the original staging evidence.

## When to create or update a review record

Create/update a review note for non-trivial curation work, especially when:

- a curated page is created or materially updated;
- evidence is insufficient and the decision is `DEFER`;
- candidate knowledge is rejected as non-reusable/unsupported;
- staging evidence conflicts with existing curated knowledge;
- relationship edges are added, removed or disputed;
- a reviewer needs explicit questions or coverage decisions.

Use filenames such as:

```text
STG-YYYYMMDD-<slug>-review.md
```

A review may reference more than one staging item when they form one coherent curation decision.

## Decision meanings

- `CREATE` — evidence supports a new curated concept proposal.
- `UPDATE` — evidence belongs in an existing curated concept.
- `DEFER` — potentially useful, but evidence/clarification is insufficient.
- `REJECT` — should not become governed Atlas knowledge (for example transient, duplicate, unsupported or inappropriate content).
- `CONFLICT` — material evidence contradicts existing curated knowledge and requires human resolution rather than silent reconciliation.

These are curation decisions, not substitutes for human approval of `status: curated`.

## What the record must preserve

A useful review note separates:

- claims accepted as supported;
- claims not accepted and why;
- possible/unconfirmed claims left out of authoritative relationships;
- relationship type/target/confidence/evidence decisions;
- open questions and coverage limits;
- index/map/status updates made by the proposal;
- deterministic lint/map/test results;
- human reviewer and final outcome when available.

## Human review boundary

Claude may prepare the review record and propose files, but it cannot fill `Human reviewer` as if approval occurred or set a final approval outcome on behalf of a person.

If the review has not happened, say so explicitly.

## Relationship to staging and status

Do not rewrite consumed staging evidence to reflect review decisions. The staging record remains the original evidence; the review note records interpretation/decision; `_curated/status/curation-status.md` records routine workflow state.

## Security and sensitivity

A review record should cite sensitive source systems rather than copy their data. Do not duplicate secrets, customer information, raw incident logs or unnecessary personal data merely to justify a curation decision.
