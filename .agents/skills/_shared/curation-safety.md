# Curation safety and scoped validation

Read this contract before Atlas authoring, staging handoff or curation. The curation parent owns guards, generation, validation, repair, review and lifecycle changes; the curator agent only materialises approved pages.

## Authoring prerequisites

Before staging or curating, read `atlas-package.json` and follow its registered taxonomy/contract paths. Always read registered `types` and `statuses`; read `concept_fields` only for controlled concept/asset/resource fields, `standard_categories` for standards, and the registered `map_fields` contract before map-bound fields/relationships. Do not load unrelated taxonomy. Then read the destination README/template/index: use staging root/bucket files for staging and the target collection's files for curation.

- Coverage states included scope; confidence states evidence strength for a fact. Never substitute one for the other.
- Keep reviewed evidence distinct from a non-reviewed explanatory note; a note cannot upgrade a claim.
- Use `consumes`/`produces` only for component, schema or data-asset contracts; use resource fields such as `reads_from`/`writes_to` for infrastructure/resource interaction; put flow participation only in ordered `steps`.

## Scoped curation sequence

After one approved preview: start the guard with `python scripts/atlas_work_guard.py start --root . --path <approved-existing-file> --missing-path <approved-new-file> --generated-path <approved-generated-file> --id <active-staging-id> --format json` (repeat or omit selectors as needed, but pass exact files rather than directories); retain both returned OS-temporary `state` and `key_file` paths in the parent and never pass the key to the curator; a changed active record or approved scope stops for a revised preview; mark only approved evidence `curating`; materialise; run `python scripts/atlas_work_guard.py checkpoint --root . --state <state-dir> --key-file <key-file>`; aggregate full lint; classify current/shared/new/unexpected findings as blocking and demonstrably unrelated pre-existing findings as advisory; make at most two uniquely determined meaning-preserving in-scope mechanical repair passes; run `python scripts/atlas_work_guard.py validate --root . --state <state-dir> --key-file <key-file>`; rebuild/check; independently review and re-fingerprint after permitted follow-up repair; consume successful evidence; then run `python scripts/atlas_work_guard.py cleanup --root . --state <state-dir> --key-file <key-file>` only after completion to remove the authenticated state directory and key file.

Threat model: the guard provides operational integrity/recovery, not an OS security sandbox. Trust the parent to preserve approved scope and never pass the bearer key to the curator. Anyone under the same account who can read the key can authenticate actions. The guard detects accidental/cross-agent state alteration and authenticates restore/cleanup; it does not cryptographically constrain the parent or another key holder.

Never fix an unrelated baseline issue or let it block staging/semantic curation. Never use `sed`, regex replacement, line deletion, minimal-frontmatter rewrites, resource/relation/evidence deletion or emptying, ID/type renaming or global confidence downgrade. Consolidate semantic ambiguity for the user.

An unrelated pre-existing generator or freshness failure may be discovered by lint, generation, or the freshness check itself. Do not repair unrelated records. Disclose generated freshness as deferred, then allow independent semantic review and consumption when the approved current scope is semantically complete. A current-cause failure or an unexplained lint/compiler inconsistency stops the batch in `curating`; do not consume evidence.

Global lint and CI remain strict.

## Recovery and completion

Already-consumed evidence uses a repair-only/recovery entry path: preview and approve the exact damaged curated pages/claims, evidence, repair and generated effects; start a target-specific guard; then materialise, checkpoint, validate/generate and independently review without lifecycle mutation. Consumed records remain `consumed` throughout. A current-scope failure stops active/new records from this batch in `curating`; a recovery failure leaves consumed evidence `consumed`.

Restore only exact guarded targets from a verified revision, with `python scripts/atlas_work_guard.py restore --root . --state <state-dir> --key-file <key-file> --to pre`, or with `python scripts/atlas_work_guard.py restore --root . --state <state-dir> --key-file <key-file> --to materialized`; never guard or restore all `_curated/` in a mixed checkout. Preserve tracked/untracked work. The state directory and key file stay OS-temporary; retain them while recovery may be needed, and run `python scripts/atlas_work_guard.py cleanup --root . --state <state-dir> --key-file <key-file>` only after completion to remove both. Report **Current work**, **Scope validation**, **Generated freshness**, and **Package health** separately.
