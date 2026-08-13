<!-- atlas:managed:start -->
## Atlas context

Home Atlas package: `{{PACKAGE}}`
Repository seed: `{{REPOSITORY_SEED}}`
Repository seed verification: `{{SEED_VERIFICATION}}`

Use Atlas through ordinary language: **Ask Atlas** for engineering context/impact, **Teach Atlas** to save a fact or answer a gap, **Sync Atlas** to onboard or update the repository, and **Curate Atlas** to reconcile pending evidence. Codex selects the specialist workflow. A write gets one concrete scope preview and one approval; internal handoffs do not repeat it.

Atlas relevance triggers:

- Use `atlas-discover` when durable architecture or cross-system context can improve the answer, even without an explicit skill invocation.
- Use `atlas-impact` for explicit blast-radius, change-risk, migration, deletion or failure questions.
- Use `atlas-stage-changes` when the user asks to assess or stage reusable knowledge from merged default-branch changes since Atlas last considered the source.
- Use full repository onboarding when adequate baseline coverage does not yet exist; use incremental processing only after that baseline.

Typed search and index fallback: resolve exact stable IDs directly; otherwise use type-directed candidate search. If candidates are weak or ambiguous, use the relevant Atlas index. Open the selected curated page and follow its links; use maps only for reverse or multi-hop traversal.

Trust rules: preserve ambiguity; disclose `not-verified` repository context in every answer that uses it; treat every `_curated/` page with `status: curated` as authoritative; treat `_staging/` as evidence only; disclose source fallback; and give one short non-blocking checkout advisory outside `main`/`master` or for modified/untracked pages.

Missing-Atlas instructions: if Atlas cannot be resolved or its manifest is invalid, state that Atlas was not consulted, ask the user to make the current Atlas checkout available, and offer to continue with bounded repository evidence. Do not interpret unavailable or moved Atlas as absent coverage.

This repository owns its exact build, test, lint and local-development commands.
<!-- atlas:managed:end -->
