# Advanced Atlas workflow reference

Most engineers can use Atlas through ordinary language: ask a question, teach it a fact, sync a repository or curate pending evidence. This page exposes the internal interfaces for maintainers, debugging and audit.

| Human intent | Internal workflow | Typical deterministic tools |
|---|---|---|
| Ask Atlas | `atlas-discover`, `atlas-impact` | `atlas_query.py find`, `resolve`, `context`, `neighbors`, `impact` |
| Teach Atlas | `atlas-stage`, `atlas-questions` | `atlas_query.py questions`, `staging`; `atlas_lint.py` |
| Sync Atlas | `atlas-onboard-repository`, `atlas-onboard-standards`, `atlas-stage-changes` | `atlas_source_snapshot.py`, `atlas_query.py context`, `atlas_intake.py` |
| Curate Atlas | `atlas-curate`; `atlas-review` for an audit/second opinion | `rebuild_atlas.py`, `atlas_review_snapshot.py`, `atlas_lint.py` |

These names are useful for explicit invocation but are not a prerequisite for normal use. Claude chooses among them from the user's request and current context.

## Source snapshots

Repository onboarding analyses one selected immutable source state:

```powershell
python scripts/atlas_source_snapshot.py prepare --repository <path>
python scripts/atlas_source_snapshot.py prepare --repository <path> --commit <revision> --default-ref origin/main --format json
python scripts/atlas_source_snapshot.py cleanup --manifest <temporary-manifest>
```

Without `--commit`, preparation accepts only the exact clean current `HEAD`. Dirty or historical/unmerged analysis uses an explicit revision and, when needed, a detached worktree below the operating-system temporary directory. Cleanup never switches, resets, stashes, cleans or force-removes the active checkout. A dirty temporary worktree is left in place and reported.

The snapshot manifest is ephemeral operational state. It is never Atlas evidence and never advances `_intake/`. For an unmerged branch snapshot, onboarding records the branch commit as the knowledge snapshot and the merge base with the default branch as the future intake anchor; it does not pretend the branch has merged.

## Power-user query routes

```powershell
python scripts/atlas_query.py resolve comp.example
python scripts/atlas_query.py find "component that enriches orders" --type component
python scripts/atlas_query.py find "order processing" --type component --type flow --path .
python scripts/atlas_query.py context .
python scripts/atlas_query.py route orders
python scripts/atlas_query.py questions repo.orders-platform
python scripts/atlas_query.py questions --path .
python scripts/atlas_query.py questions orders --scope domain
python scripts/atlas_query.py questions --scope package --format json
python scripts/atlas_query.py staging
python scripts/atlas_query.py staging --status deferred --target comp.example
python scripts/atlas_query.py staging --include-terminal --format json
python scripts/atlas_query.py neighbors comp.example
python scripts/atlas_query.py impact comp.example --direction downstream
python scripts/atlas_query.py --format json impact comp.example --max-depth 4
```

Query output and generated maps route to evidence but are not semantic authority. Candidate search is deterministic and preserves ambiguity.

## Optional idle reminder

```powershell
python <ATLAS_ROOT>/.claude/skills/atlas-questions/scripts/manage_idle_reminder.py install
python <ATLAS_ROOT>/.claude/skills/atlas-questions/scripts/manage_idle_reminder.py check
python <ATLAS_ROOT>/.claude/skills/atlas-questions/scripts/manage_idle_reminder.py remove
```

Use `--dry-run` before installation or removal. The hook is user-level, suggests a Teach Atlas session only when relevant questions exist, and never starts a conversation or writes Atlas. Reinstall it if the Atlas checkout moves.

## Evaluation and maintenance

```powershell
python scripts/atlas_lint.py .
python scripts/rebuild_atlas.py
python scripts/rebuild_atlas.py --check
```

## Scoped curation and recovery

Before authoring, read `atlas-package.json` and follow its registered paths: load `types` and `statuses` always, `concept_fields` when selecting controlled concept/asset/resource fields, `standard_categories` for standards, and `map_fields` before map-bound fields or relationships. Also read the destination README, template and index. After the approved curation preview, use this fixed sequence:

1. Record the work guard: exact approved files, claims, staging status effects, expected generated effects, tracked diff and relevant untracked pages.
2. Mark only approved evidence `curating`, materialise the decision matrix, then preserve a materialized checkpoint of only the exact curated pages and status changes.
3. Run `python scripts/atlas_lint.py .` once across the package. Current/shared/new/unexpected findings block; demonstrably unrelated pre-existing baseline findings are advisory. Do not repair baseline issues or let them block staging/semantic curation.
4. Make no more than two aggregate passes of uniquely determined, meaning-preserving, in-scope mechanical repairs. Do not use regex or line deletion; do not empty/delete resources, relations or evidence; do not rename an ID/type, rewrite minimal frontmatter, or globally lower confidence. Bring semantic ambiguity to the user.
5. Verify the approved scope is clean; run rebuild and rebuild check; fingerprint and independently review; re-fingerprint after every permitted follow-up repair; then consume successful evidence.

The work guard is an operational integrity and recovery mechanism, not an OS security sandbox. The parent remains trusted to preserve approved scope and must never pass the bearer key to the curator. Anyone under the same account who can read the key can authenticate guard actions. The guard detects accidental or cross-agent state alteration and authenticates cleanup/restore; it does not cryptographically constrain the parent or another key holder.

A current-cause problem or a lint/compiler mismatch leaves evidence `curating`. If freshness is blocked solely by an unrelated baseline issue, semantic curation may complete and consume with generated freshness explicitly deferred. This does not relax strict global lint or CI.

Completion reports separate **Current work**, **Scope validation**, **Generated freshness**, and **Package health**. A consumed staging record remains consumed. Restore only an identified damaged curated page from the automatic materialized checkpoint or verified revision; never restore all `_curated/` in a mixed checkout, and preserve both tracked diff and untracked pages.

Use `/atlas-evaluate prepare|run|score` only for a sealed end-to-end benchmark. Keep its fixture, personas, ground truth, frozen answers and results in the selected external sealed directory.
