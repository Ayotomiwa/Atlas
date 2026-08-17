# Curation safety and scoped validation

Read this contract before Atlas authoring, staging handoff or curation. The parent owns the feature branch, local commits, validation, generation, repair, review and lifecycle; the curator only materialises approved pages.

## Authoring prerequisites

Read `atlas-package.json` and its registered taxonomy/contracts. Always read `types` and `statuses`; read `concept_fields` for controlled concept/asset/resource fields, `standard_categories` for standards, and `map_fields` before map-bound fields/relationships. Read the destination README/template/index and no unrelated taxonomy.

- Coverage is included scope; confidence is evidence strength. Never substitute them.
- Keep reviewed evidence distinct from notes.
- Use `consumes`/`produces` for component, schema or data-asset contracts, resource fields for infra/resource interaction, and flow `steps` as the sole participation source.

Before staging or curation writes, record full lint JSON from the clean branch and compare it with post-write lint. New/touched-page, changed-shared or newly introduced findings block; an unchanged unrelated finding is advisory, is not repaired, and does not block the scoped write. Report non-zero package health separately rather than calling the package clean.

## Git-backed curation

Reuse the feature branch chosen by the persistence contract. Before preview, record `HEAD`, the shared lint baseline and rebuild-check diagnostics. An unrelated existing issue is package health, not current-scope repair work.

After approval: recheck branch/HEAD/content-clean state, eligibility and paths; changed scope requires a new preview. Mark approved records `curating`, materialise, inspect the exact diff, and create `atlas: curate checkpoint <scope>` from exact paths before repair. Do not bypass hooks. Run aggregate lint; current/changed-shared/new/unexplained findings block while unchanged unrelated baseline findings are advisory. Make at most two uniquely determined meaning-preserving repair passes. Never use regex/line surgery, minimal-frontmatter rewrites, claim/resource/relation/evidence deletion, ID/type renaming or global confidence downgrades.

When current-scope structure is clean, rebuild/check. An unchanged unrelated generator failure may defer freshness without blocking semantic review; a current failure or unexplained lint/compiler mismatch leaves the batch `curating`. Verify approved paths, commit changed repair/generated files as `atlas: curate validated <scope>` or use the checkpoint as proposal when unchanged, then review immutable `<starting-sha>..<proposal-sha>` with clean state before/after. Drift invalidates review. Commit supported fixes as `atlas: curate review fixes <scope>` and re-review the full range.

After clean review, apply approved terminal statuses, compact checkpoint and deterministic generated effects in `atlas: curate finalize <scope>`. Its diff must be lifecycle/checkpoint/generated only; semantic changes require full validation and review. Global lint/CI remain strict.

For recovery, inspect the diff and restore only approved paths from the checkpoint commit; never reset broadly or restore all `_curated/`. Consumed repair work keeps lifecycle unchanged and uses the same commit/range review. Report Current work, Scope validation, Generated freshness and Package health separately. Never push, merge, approve or publish.
