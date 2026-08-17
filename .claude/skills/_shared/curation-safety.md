# Curation safety and scoped validation

Read this contract before any Atlas authoring, staging handoff or curation. The curation parent owns guards, generation, validation, repair, review and lifecycle changes; a curator agent only materialises its approved pages.

## Authoring prerequisites

Before staging or curating, read `atlas-package.json` and resolve taxonomy/contracts through its registered paths. Always read the registered `types` and `statuses`. Read registered `concept_fields` only when selecting controlled concept, asset, or resource fields; read registered `standard_categories` for standards; and read the registered `map_fields` contract before selecting map-bound fields or relationships. Do not load unrelated taxonomy merely because it is registered. Then read the destination's `README.md`, `_template.md`, and `index.md`: use the staging root/bucket files for staging and the target collection's three files for curation. Complete the relevant reads before selecting fields, IDs, lifecycle values, or relationship forms.

Author relationships exactly where they mean something:

- Coverage says what the record or map is known to include; confidence says how well each claimed fact is evidenced. Do not use one to stand in for the other.
- Keep reviewed evidence distinct from a non-reviewed explanatory note; a note cannot upgrade an evidence-backed claim.
- Use `consumes` and `produces` only for component, schema, or data-asset contracts. Use resource fields such as `reads_from` and `writes_to` only for infrastructure/resource interaction. Put participation in a flow only in its ordered `steps`.

## Scoped curation sequence

After the one approved preview, perform this order without skipping or reordering it:

1. Start a work guard: record the approved files, claims, staging statuses, expected generated effects, tracked diff, and relevant untracked pages. Use `python scripts/atlas_work_guard.py start --root . --path <approved-existing-file> --missing-path <approved-new-file> --generated-path <approved-generated-file> --id <active-staging-id> --format json`; repeat or omit selectors as needed, but pass exact file targets rather than directories. Retain both returned OS-temporary paths, `state` and `key_file`. The parent keeps both and never passes the key file to the curator. A changed active record or changed scope stops the batch for a revised preview.
2. Mark only the approved staging records `curating` and have the curator materialise only its matrix.
3. Make an automatic materialized checkpoint with `python scripts/atlas_work_guard.py checkpoint --root . --state <state-dir> --key-file <key-file>` before validation or repair. It covers only the exact guarded curated pages and status changes; it is not permission to restore all `_curated/`.
4. Run one aggregate full `python scripts/atlas_lint.py .` and classify each finding: current/shared/new/unexpected findings block; a demonstrably pre-existing unrelated baseline finding is advisory. Never repair unrelated baseline findings and never let them block staging or semantic curation.
5. Make at most two aggregate passes of uniquely determined, meaning-preserving, in-scope mechanical repairs. Never use `sed`, regex replacement, line deletion, minimal-frontmatter rewrites, resource/relation/evidence deletion or emptying, ID/type renaming, or a global confidence downgrade. Consolidate semantic ambiguity for the user instead of guessing.
6. Verify the approved scope with `python scripts/atlas_work_guard.py validate --root . --state <state-dir> --key-file <key-file>`, then run `python scripts/rebuild_atlas.py` and `python scripts/rebuild_atlas.py --check`. Run review only from that clean, materialized scope.
7. Independently review, apply only allowed meaning-preserving follow-up repairs with a new fingerprint/re-review, then mark successful staging evidence `consumed`. Run `python scripts/atlas_work_guard.py cleanup --root . --state <state-dir> --key-file <key-file>` only after completion; authenticated cleanup removes both the state directory and key file.

Threat model: the work guard is an operational integrity and recovery mechanism, not an operating-system security sandbox. The parent process is trusted to preserve the approved scope; never pass the bearer key to the curator. Anyone running as the same account who can read that key can authenticate guard actions. The guard detects accidental or cross-agent alteration of guarded state and authenticates restore/cleanup, but it does not cryptographically constrain the parent or another key holder.

An unrelated pre-existing generator or freshness failure may be discovered by lint, generation, or the freshness check itself. Do not repair unrelated records. Disclose generated freshness as deferred, then allow independent semantic review and consumption when the approved current scope is semantically complete. A current-cause failure or an unexplained lint/compiler inconsistency stops the batch in `curating`; do not consume evidence.

Global `atlas_lint.py` and CI remain strict: classification limits this workflow's repair/blocking decision and does not redefine package health.

## Recovery and completion

Already-consumed evidence uses a repair-only/recovery entry path. Preview the exact damaged curated pages and claims, evidence source, intended repair and generated effects; obtain approval for that exact repair scope; then start a target-specific guard and follow the materialize/checkpoint/validate/generate/review sequence. Consumed records remain `consumed` throughout: do not mutate lifecycle. A current-scope failure stops active/new records that entered the current batch in `curating`; a recovery failure leaves previously consumed records `consumed`.

Recover only an exact guarded damaged curated page from its verified revision or with `python scripts/atlas_work_guard.py restore --root . --state <state-dir> --key-file <key-file> --to pre` or `python scripts/atlas_work_guard.py restore --root . --state <state-dir> --key-file <key-file> --to materialized`. The guard must contain only the intended recovery targets; never guard or restore all `_curated/` when the checkout has mixed work. Preserve both the tracked diff and untracked pages. The state directory and key file stay in the operating-system temporary directory; retain both while recovery may still be needed, and run authenticated cleanup only after completion.

Completion reports use these headings: **Current work**, **Scope validation**, **Generated freshness**, and **Package health**. Separate current blockers from unrelated baseline advisories and list any deferred freshness check.
