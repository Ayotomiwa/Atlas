# Merged-change intake workflow

Match checkpoints by credential-free Git identity rather than checkout path. Treat `considered_through.commit` as the exclusive cursor and the refreshed remote default-branch tip as the inclusive endpoint. `observed_through` is not proof of assessment. A missing checkpoint requires a confirmed stable source key plus an explicit base, locally provable merged-MR commit or exact future-intake anchor from approved onboarding evidence. Verify it; never guess. Stop on non-ancestry, rewritten history, ambiguous source identity or checkpoint digest change.

Read with `python <ATLAS_ROOT>/scripts/atlas_intake.py --root <ATLAS_ROOT> --format json show <source-key>`. Atomically update with `python <ATLAS_ROOT>/scripts/atlas_intake.py --root <ATLAS_ROOT> --format json write --checkpoint <source-key> --input <temporary-json> --expected-digest <digest-or-missing>`. Use `missing` only after `show` confirms absence; exit code 2 means stop and re-read. Never edit checkpoint JSON directly.

Inspect first-parent merges and direct commits without switching the user's checkout. Capture commits and MR identity from local Git evidence or explicit user confirmation tied to the relevant default-branch commit; label the latter `user-confirmed` and preserve its supporting statement. Capture renames/deletions, changed paths, endpoint state, material before/after evidence, Atlas candidates, reusable dependency/contract/compatibility/ownership/operational/safety findings and coverage limits. Flag likely sensitive paths without opening them. Use `python <ATLAS_ROOT>/scripts/atlas_query.py --root <ATLAS_ROOT> staging --include-terminal --format json` to detect exact structured provenance overlap. Never query a hosting API to fill a missing MR identity.

Delegate read-only interpretation to `atlas-change-analyst`; the skill owns decisions, interaction, staging and checkpoint advancement. Preview plain-language outcome groups, then an audit matrix of logical change, commit/MR, affected candidates, finding, outcome, staging boundary and gap. One approval covers the exact staging files and checkpoint compare-and-swap.

Outcomes are `staged`, `no-stage`, `already-represented`, `deferred` and `unassessed`. The first four may advance the cursor; `deferred` must remain in unresolved state and `unassessed` blocks advancement. Record reasons for `no-stage`, `deferred` and `unassessed`.

For `source_type: merged-change`, write `change_source` with source key, branch, exclusive/inclusive full-SHA range and unique MR IDs/merge commits. Direct commits use an empty MR list. Store resulting staging IDs in the checkpoint.

Safe order: recheck checkpoint digest, write approved staging, lint, record the refreshed observed tip and eligible considered cursor through one compare-and-swap, then lint again. Do not delete staged evidence after a checkpoint race; reconcile it as already represented on the next run.
