# Persistence preview and approval contract

Every write-capable Atlas workflow uses one preview and one explicit approval for one unchanged persistence scope.

## Git preflight

Apply this to the repository that will receive the write: normally the Atlas package, or the product repository for managed-instruction setup.

1. Resolve the current branch and the remote default branch. Refresh the remote ref when available; an unavailable refresh is a non-blocking staleness advisory.
2. Require content-clean staged and unstaged state plus no non-ignored untracked files. Determine content changes with Git diffs and `git ls-files --others --exclude-standard`, not stat-only `git status` markers that can be caused by Windows line-ending normalization.
3. When already on a non-default branch with shared default-branch history, state `Using feature branch <name>` once and continue. Reuse it for subsequent related Atlas writes; do not create a branch per record, batch, or repair. Warn without blocking when it is behind the refreshed default branch.
4. On the resolved default branch (commonly `main` or `master`), detached HEAD, or unrelated history, stop before writing. Ask the user to confirm a suggested branch, choose an existing branch, or enter a custom branch. Suggest `feature/atlas-curate-<scope>-YYYYMMDD` for curation and `feature/atlas-<intent>-<scope>-YYYYMMDD` otherwise; validate with `git check-ref-format --branch`.

Branch confirmation authorises only creating or switching the branch. The persistence preview below remains required for content writes.

## Required preview

Show, in compact plain language:

1. what Claude found;
2. what will be saved or changed;
3. evidence and provenance;
4. scope, confidence and remaining uncertainty;
5. existing, pending or conflicting Atlas knowledge;
6. decisions only the user can make;
7. what will not be saved;
8. validation and operational-state effects, including any intake checkpoint update;
9. the feature branch and planned local commit boundaries.

The preview identifies the concrete files or records to be written. Approval such as “yes”, “save it” or “proceed” is valid only for that displayed scope.

## Handoffs

- Pass the approval and exact preview scope through internal skill/agent handoffs.
- Do not ask again merely because another Atlas skill performs the write.
- If the proposed claims, target records, files, evidence boundary, destructive effect or checkpoint range changes materially, stop and show a revised preview.
- A request to keep investigating, answer another question or inspect a diff is not persistence approval.

## Local commit contract

- After approval and successful scope validation, the parent workflow may create the previewed local commits on the current feature branch. This is not permission to push, merge, force-update, approve, or publish.
- Stage only exact approved paths with `git add -- <paths>`; never use `git add .`, broad resets, or unrelated files.
- Ordinary staging, onboarding, standards, repair, or setup writes use one validated commit. Merged-change intake commits its staging evidence and checkpoint update atomically. Curation uses the checkpoint/validated/finalization sequence in `curation-safety.md`.
- If a commit fails, stop and leave the scoped diff inspectable. Never bypass repository hooks automatically.
- A later related write may reuse the same feature branch but still needs its own persistence preview when its content scope is new.

## Completion summary

For curation, report **Current work**, **Scope validation**, **Generated freshness**, and **Package health** separately. State current blockers, unrelated baseline advisories, and deferred freshness without weakening global lint/CI requirements. Then report saved or changed; already covered; left unknown; deferred for human input; excluded; and next publication step. Audit details may add staging IDs, lifecycle codes and internal dispositions without making them prerequisites for ordinary use.
