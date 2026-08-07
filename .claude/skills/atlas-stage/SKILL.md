---
name: atlas-stage
description: Capture one reusable engineering fact as raw Atlas evidence without curating it.
allowed-tools: Read, Grep, Glob, Write, Edit
---

# atlas-stage

Use for a reusable fact discovered during normal engineering work when a full service onboarding crawl is unnecessary.

1. Identify the correct `_staging/` bucket from `_staging/index.md`.
2. Read that bucket's `README.md` and `_template.md` before writing.
3. Ask only questions that block accurate evidence capture.
4. Allocate an ID using `STG-YYYYMMDD-<slug>`; scan existing staging IDs and add `-2`, `-3`, and so on deterministically for same-day collisions.
5. Capture the source, what is known, what is possible/unconfirmed, suggested curated targets, and open questions.
6. Preserve uncertainty; never create reviewed or authoritative relationships here.
7. Write exactly one staging evidence entry for this workflow invocation.
8. Run `python scripts/atlas_lint.py .` after writing.
9. Never write `_curated/`, generated maps, curation status, or a review decision.

If the reusable knowledge originated from a private conversation or external source, obtain explicit user approval before persisting it.
