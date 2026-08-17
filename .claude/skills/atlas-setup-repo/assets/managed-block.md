<!-- atlas:managed:start -->
## Atlas context

Home Atlas package: `{{PACKAGE}}`
Repository seed: `{{REPOSITORY_SEED}}`
Repository seed verification: `{{SEED_VERIFICATION}}`

This repository uses Datalens Atlas for reviewed architecture, ownership, dependencies, flows, infrastructure, schemas, operations and standards.

Use Atlas through ordinary language:

- **Ask Atlas** for engineering context or change impact.
- **Teach Atlas** by asking to save a durable fact or answer an open question.
- **Sync Atlas** by asking to onboard or update this repository.
- **Curate Atlas** by asking to reconcile pending evidence for this context.

Claude selects the specialist workflow. For writes, it shows one concrete scope preview and requests one approval; internal handoffs do not ask for the same approval again.

Atlas relevance triggers:

- Use `atlas-discover` when durable architecture or cross-system context can improve the answer, even without an explicit slash command.
- Use `atlas-impact` for explicit blast-radius, change-risk, migration, deletion or failure questions.
- Use `atlas-stage-changes` when the user asks to assess or stage reusable knowledge from merged default-branch changes since Atlas last considered the source.
- Use full repository onboarding when adequate baseline coverage does not yet exist; use incremental change processing only after that baseline.

Typed search and index fallback: resolve exact stable IDs directly; otherwise use type-directed candidate search. If candidates are weak or ambiguous, use the relevant Atlas index. Open the selected curated page and follow its links; use maps only for reverse or multi-hop traversal.

Within one conversation, keep only ephemeral Atlas session context: Atlas/product roots and current path, selected stable IDs/opened curated pages, inspected source paths, the coverage endpoint, and whether the checkout advisory was disclosed. Reuse it only while repository, record/evidence and question type are unchanged. Re-enter Atlas for a repository/record change, suspected source/checkout change, the end of recorded coverage, or impact, ownership, conflict, standards, recovery or other cross-boundary work; carry still-valid context through internal handoffs. New conversations start cold and persist none of this state.

Trust rules: preserve ambiguity; disclose `not-verified` repository context in every answer that uses it; treat every `_curated/` page with `status: curated` as authoritative; treat `_staging/` as evidence only; disclose source fallback; and give one short non-blocking checkout advisory outside `main`/`master` or for modified/untracked pages.

Missing-Atlas instructions: if Atlas cannot be resolved or its manifest is invalid, state that Atlas was not consulted, tell the user to restart with `claude --add-dir <path-to-current-Atlas-checkout>`, and offer to continue with bounded repository evidence. Do not interpret an unavailable or moved Atlas checkout as absent coverage.

This repository owns its exact build, test, lint and local-development commands.
<!-- atlas:managed:end -->
