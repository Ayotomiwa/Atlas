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

Use `/atlas-evaluate prepare|run|score` only for a sealed end-to-end benchmark. Keep its fixture, personas, ground truth, frozen answers and results in the selected external sealed directory.
