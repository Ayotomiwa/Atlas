# Curation safety and scoped validation

Read this contract before Atlas authoring, staging handoff or curation. The parent owns the feature branch, local commits, generation, validation, repair, review and lifecycle changes; a curator agent only materialises approved pages.

## Authoring prerequisites

Before staging or curating, read `atlas-package.json` and resolve taxonomy/contracts through its registered paths. Always read registered `types` and `statuses`. Read `concept_fields` only when selecting controlled concept, asset or resource fields; `standard_categories` for standards; and `map_fields` before map-bound fields or relationships. Do not load unrelated taxonomy. Then read the destination `README.md`, `_template.md`, and `index.md`: staging root/bucket files for staging and the target collection's files for curation.

- Coverage says what the record includes; confidence says how well a fact is evidenced. Never substitute one for the other.
- Keep reviewed evidence distinct from a non-reviewed explanatory note.
- Use `consumes` and `produces` only for component, schema or data-asset contracts. Use resource fields such as `reads_from` and `writes_to` for infrastructure/resource interaction. Put flow participation only in ordered `steps`.

## Scoped validation for authoring

Before an approved staging or curation write, record full lint JSON from the clean branch. After writing, run full lint again. Findings owned by a new/touched page, a changed shared contract/configuration, or newly introduced package behavior block that write. An unchanged finding on an unrelated page is reported after the scoped result and is not repaired or allowed to block staging/semantic curation. The global command may therefore remain non-zero while the scoped write is valid; report package health separately and never describe the whole package as clean.

## Git-backed curation sequence

Use the feature branch selected by `persistence-approval.md`. A branch is reused for related work; curation does not create one branch per batch.

Before the preview, record the starting `HEAD`, the shared lint baseline, and `python scripts/rebuild_atlas.py --check`. Retain page/record diagnostics. An unrelated existing failure is visible package health, not permission to repair it or a reason to block the current preview.

After the one approved preview, perform this order:

1. Recheck the branch, starting `HEAD`, actual content-clean state, queue eligibility and approved paths. A changed record, branch, or scope stops for a revised preview. Mark only approved evidence `curating`, then have the curator materialise only its matrix.
2. Inspect the complete exact-path diff. If it matches the preview, stage only those paths and create `atlas: curate checkpoint <scope>` before any validation repair. Do not bypass hooks. If the checkpoint cannot be committed, stop with the diff intact.
3. Run aggregate full lint once. Compare findings with the recorded baseline by owning path/record and message. Current-scope, changed-shared, new or unexplained findings block; demonstrably unchanged unrelated findings are advisory. Make at most two aggregate passes of uniquely determined, meaning-preserving in-scope repairs.
4. Never use `sed`, regex replacement, line deletion, minimal-frontmatter rewrites, resource/relation/evidence deletion or emptying, ID/type renaming, or global confidence downgrades to satisfy validation. Bring semantic ambiguity to the user.
5. After current-scope structured findings are clean, run `python scripts/rebuild_atlas.py` and `python scripts/rebuild_atlas.py --check`. If only an unchanged unrelated baseline generator/freshness problem prevents this, disclose freshness as deferred and continue semantic review without touching the unrelated record. A current-cause failure or unexplained lint/compiler inconsistency stops the batch in `curating`.
6. Verify every changed path remains approved. Stage exact repair/generated paths and create `atlas: curate validated <scope>` when anything changed after the checkpoint; otherwise the checkpoint commit is the proposal commit.
7. Give the independent reviewer the immutable range `<starting-sha>..<proposal-sha>`, exact staging/source evidence and source checkout commits. Require the same proposal `HEAD` and content-clean state before and immediately after review. Drift invalidates the review. Supported fixes use an exact-path `atlas: curate review fixes <scope>` commit and a fresh review of the full range.
8. After clean semantic review, mark successful evidence `consumed`, apply other approved terminal outcomes, update the compact checkpoint, and rebuild when available. Create `atlas: curate finalize <scope>` from exact paths. The finalization diff may contain only planned lifecycle/checkpoint and deterministic generated effects; any semantic change requires validation and full re-review.

Global lint and CI remain strict. Scoped classification controls only whether this workflow repairs or blocks; it never reclassifies package health.

## Recovery and completion

Already-consumed evidence uses a repair-only entry path with an exact preview and no lifecycle mutation. Record its starting SHA, commit the supported repair, validate, generate when possible, and independently review the immutable range.

For a damaged in-progress page, inspect the diff and restore only approved paths from the local checkpoint commit with `git restore --source=<checkpoint-sha> -- <paths>`. Never restore all `_curated/`, run a broad reset, or overwrite unrelated tracked/untracked work.

Completion reports use **Current work**, **Scope validation**, **Generated freshness**, and **Package health**. Separate current blockers from unrelated baseline advisories and deferred freshness. Local commits do not authorise push, merge, approval or publication.
