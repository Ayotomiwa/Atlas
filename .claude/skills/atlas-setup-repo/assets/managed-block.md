<!-- atlas:managed:start -->
## Atlas context

Home Atlas package: `{{PACKAGE}}`
Repository seed: `{{REPOSITORY_SEED}}`
Repository seed verification: `{{SEED_VERIFICATION}}`

This repository uses Datalens Atlas for reviewed architecture, ownership, dependencies, flows, infrastructure, schemas, operations and standards.

Atlas relevance triggers:

- Use `atlas-discover` when durable architecture or cross-system context can improve the answer, even without an explicit slash command.
- Use `atlas-impact` for explicit blast-radius, change-risk, migration, deletion or failure questions.

Typed search and index fallback: resolve exact stable IDs directly; otherwise use type-directed candidate search. If candidates are weak or ambiguous, use the relevant Atlas index. Open the selected curated page and follow its links; use maps only for reverse or multi-hop traversal.

Trust rules: preserve ambiguity; disclose `not-verified` repository context in every answer that uses it; treat every `_curated/` page with `status: curated` as authoritative; treat `_staging/` as evidence only; disclose source fallback; and give one short non-blocking checkout advisory outside `main`/`master` or for modified/untracked pages.

Missing-Atlas instructions: if Atlas cannot be resolved or its manifest is invalid, state that Atlas was not consulted, tell the user to restart with `claude --add-dir <path-to-current-Atlas-checkout>`, and offer to continue with bounded repository evidence. Do not interpret an unavailable or moved Atlas checkout as absent coverage.

This repository owns its exact build, test, lint and local-development commands.
<!-- atlas:managed:end -->
