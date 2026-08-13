# Merged-change intake workflow

## Range and checkpoint

- Match an existing checkpoint by its credential-free source locator and physical Git identity, not by the current checkout path. When none exists, propose a stable lowercase source key from the remote repository identity and confirm it in the same round as the required base; never store credentials or a machine-local path.
- Prefer the remote and default branch evidenced by Git configuration. Use `origin/main` only as the fallback when it exists; preserve ambiguity instead of fetching an assumed source.
- Treat `considered_through.commit` as the exclusive cursor and the refreshed remote default-branch tip as the inclusive endpoint.
- Treat `observed_through` as observation only; it does not prove that every intervening change was assessed.
- On a missing checkpoint, accept an explicit base commit, a merge commit locally evidenced as belonging to the selected source, or the exact future-intake anchor recorded in approved full-onboarding evidence. Verify the anchor against the selected source and default history. Record the base as the initial exclusive cursor; do not stage the base itself.
- Stop all checkpoint writes when the cursor is not an ancestor of the endpoint, history was rewritten, source identity is ambiguous, or another process changes the checkpoint after it was read. When source/range identity remains valid but assessment is incomplete, a successfully fetched endpoint may be recorded as observed after approval without claiming it was considered.
- A `deferred` change may be considered for cursor continuity only when it remains in the checkpoint's unresolved list. An `unassessed` change blocks the cursor.

Use the intake helper for reading and atomic updates:

```text
python <ATLAS_ROOT>/scripts/atlas_intake.py --root <ATLAS_ROOT> --format json show <source-key>
python <ATLAS_ROOT>/scripts/atlas_intake.py --root <ATLAS_ROOT> --format json write --checkpoint <source-key> --input <temporary-json> --expected-digest <digest-or-missing>
```

Retain the digest returned by `show` and supply it to `write`; use the literal `missing` only when `show` confirmed that no checkpoint exists. Build the validated candidate payload in the operating-system temporary directory and remove it after the command. Exit code 2 means the checkpoint changed or is locked: stop and re-read rather than retrying with a new digest. Never directly edit committed checkpoint JSON.

## Change discovery

Inspect the first-parent history so merge boundaries remain readable, but include direct commits. For each candidate capture:

- commit and MR identity from local Git evidence or explicit user confirmation tied to that default-branch commit;
- changed paths, rename/delete state and final default-branch contents;
- before/after evidence needed to explain durable behavior;
- most-specific `repo.*` candidate and any affected component, flow, schema, asset or infrastructure routes;
- reusable dependency, contract, compatibility, ownership, operational or safety implications;
- areas checked unsuccessfully when that limits the conclusion.

Do not switch the user's checkout. Read final-state content from the frozen fetched endpoint with read-only Git commands; use working-tree files only when their identity relative to that endpoint is explicit. Include renames and deletions in the changed-path manifest. Flag paths likely to contain secrets, credentials, customer data or raw sensitive logs from metadata only; do not open their contents.

Use `python <ATLAS_ROOT>/scripts/atlas_query.py --root <ATLAS_ROOT> staging --include-terminal --format json` to detect overlapping `change_source` commit ranges and merge requests. A matching immutable record can yield `already-represented`; similarity alone cannot.

## Delegation

Give `atlas-change-analyst` the absolute Atlas/product roots, frozen range endpoints, read-only Git references, changed-path manifest, Atlas candidates, scan boundary, exclusions and known user-confirmed facts. The analyst interprets evidence; the skill owns user interaction, disposition decisions, writes and checkpoint advancement.

Treat an explicitly supplied MR identity as `user-confirmed` evidence, not as locally observed Git metadata. Preserve its supporting user statement in the staging evidence and require an unambiguous association with the relevant default-branch commit. Never query a hosting API to fill a missing MR identity.

## Reconciliation and preview

Use these outcomes:

| Outcome | Meaning | Cursor effect |
|---|---|---|
| `staged` | Approved reusable evidence was captured | May advance |
| `no-stage` | Assessed change had no durable Atlas value | May advance |
| `already-represented` | Existing attributable staging covers the same merged change | May advance |
| `deferred` | Assessed but a material gap remains | May advance only with an unresolved entry |
| `unassessed` | Evidence could not be evaluated | Blocks advancement |

Record a reason for every `no-stage`, `deferred`, or `unassessed` outcome. Before any write, present plain-language groups first: new evidence to save, already covered, no durable Atlas impact, needs human information, and could not safely assess. Then provide the compact audit matrix with logical change, commit/MR, affected candidates, reusable finding, internal outcome, proposed staging boundary and gap. Clarify all blocking ambiguity together. One approval covers both exact staging writes and the checkpoint compare-and-swap.

## Staging provenance

Every created `staging.change` record with `source_type: merged-change` includes:

```yaml
change_source:
  source_key: datalens-monorepo
  branch: main
  commit_range:
    from_exclusive: "<full-sha>"
    through_inclusive: "<full-sha>"
  merge_requests:
    - id: "1420"
      merged_commit: "<full-sha>"
```

Use `from_exclusive: null` only for an explicitly bounded first range; otherwise use the full prior SHA. Use an empty `merge_requests` list for direct commits. Keep resulting staging IDs in the checkpoint disposition, not inside other staging records. Cite exact repository paths/commits in the body and preserve possible, conflicting and not-covered findings.

## Safe write order

1. Re-read the checkpoint and confirm its digest is unchanged.
2. Write only approved new staging records.
3. Run `python <ATLAS_ROOT>/scripts/atlas_lint.py <ATLAS_ROOT>`.
4. If lint passes, record the refreshed endpoint as observed; advance considered only when no change is unassessed. Perform both through one compare-and-swap checkpoint update.
5. Run lint again and report the new cursor/digest.

Never remove successfully written staging records merely because checkpoint advancement loses a race. The records remain attributable evidence and are reconciled on the next run.
