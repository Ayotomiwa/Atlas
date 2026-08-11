# `_intake/` — merged-change consideration state

`_intake/` records how far Atlas has **observed and considered** a registered source repository's default branch. It prevents repeated monorepo scans and makes deferred work visible. It is shared operational state, not staging evidence, curated knowledge, or semantic authority.

## Checkpoints

Store one checkpoint per source at `checkpoints/<source-key>.json`; nested checkpoint folders are not allowed. The source key is a stable lowercase slug chosen for the physical Git repository, not a URL or a repository path. The locator must use credential-free HTTPS, SSH or scp-style Git syntax. It must not contain URL user credentials, query parameters, fragments, or a machine-local absolute path. Checkpoints use `schema_version: atlas-intake/1.0` and contain:

- a credential-free source locator and default branch;
- the latest default-branch commit observed;
- the latest contiguous commit considered;
- a compact summary of the last inspected range and its dispositions;
- unresolved deferred or unassessed changes;
- updater and timezone-qualified update time.

Example shape:

```json
{
  "schema_version": "atlas-intake/1.0",
  "source": {
    "key": "datalens-monorepo",
    "locator": "https://example.invalid/datalens.git",
    "default_branch": "main"
  },
  "observed_through": {
    "commit": "89abcdef0123456789abcdef0123456789abcdef",
    "merge_request": "1420"
  },
  "considered_through": {
    "commit": "89abcdef0123456789abcdef0123456789abcdef",
    "merge_request": "1420"
  },
  "last_run": {
    "from_exclusive": "0123456789abcdef0123456789abcdef01234567",
    "through_inclusive": "89abcdef0123456789abcdef0123456789abcdef",
    "dispositions": [
      {
        "change_key": "mr:1420",
        "commit": "89abcdef0123456789abcdef0123456789abcdef",
        "merge_request": "1420",
        "outcome": "staged",
        "staging_ids": ["STG-20260811-example-change"]
      }
    ]
  },
  "unresolved": [],
  "updated_at": "2026-08-11T12:30:00+01:00",
  "updated_by": "Engineer name"
}
```

Allowed dispositions are `staged`, `no-stage`, `already-represented`, `deferred`, and `unassessed`. Every non-empty inspected range has at least one disposition. A `no-stage`, `deferred`, or `unassessed` disposition must explain why. Deferred and unassessed changes remain in `unresolved` with exactly matching change key, commit, merge request and staging IDs. An `unassessed` outcome leaves `considered_through.commit` equal to `last_run.from_exclusive`; both may be `null` only for an uncompleted first range. `consumed` is not an intake disposition: it is derived later from the referenced staging record's lifecycle.

## Cursor rules

- The first scan requires an explicit base commit or a locally provable merged-MR commit. Do not guess a historical cursor.
- `observed_through` records what the fetch exposed, even if assessment could not finish.
- Advance `considered_through` only across a contiguous range whose relevant changes have a recorded disposition. `deferred` may advance it while retaining an unresolved item; `unassessed` may not.
- Stop and request a rebaseline when the stored cursor is no longer an ancestor, history was rewritten, or the source/range is ambiguous. Git ancestry is checked by the change-staging workflow, not Atlas lint.
- A checkpoint may reference only one unambiguous existing `staging.change` ID with the same source key, branch, inclusive commit and matching MR/merge-commit provenance. The staging files remain immutable; later `consumed` state is read from their frontmatter.

## Safe updates and recovery

Inspect a checkpoint and obtain its digest:

```text
python scripts/atlas_intake.py --root . --format json show datalens-monorepo
```

Write a fully assembled checkpoint using the returned digest, or `missing` for the first write:

```text
python scripts/atlas_intake.py --root . --format json write --checkpoint datalens-monorepo --input checkpoint.json --expected-digest <sha256-or-missing>
```

The helper validates the document, holds an exclusive sibling lock across the digest comparison and atomic replace, and rejects concurrent changes. On updates it also keeps source identity and the default branch immutable, requires the next range to start at the previous considered cursor, and prevents unresolved work from disappearing unless a current `staged`, `no-stage`, or `already-represented` disposition explicitly resolves the same change. A lock left by an interrupted process must be removed only after confirming no writer is active. If staging succeeded but the checkpoint update failed, the next run must detect the existing staging evidence and classify the change as `already-represented` rather than duplicating it.

Checkpoint recovery and history come from Git. Do not store credentials, tokens, private URL user-info, source contents, or semantic engineering claims here.
