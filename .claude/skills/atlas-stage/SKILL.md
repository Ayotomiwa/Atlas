---
name: atlas-stage
description: Capture one reusable engineering fact as raw Atlas evidence without curating it.
allowed-tools: Read, Grep, Glob, Write, Edit
---

# atlas-stage

Use for a reusable fact discovered during normal engineering work when a full service onboarding crawl is unnecessary.

1. Identify the correct `_staging/` bucket from `_staging/index.md`.
2. Read that bucket's `README.md` and `_template.md` before writing. The README defines what the bucket means and the template defines its capture shape.
3. Apply the bucket's **domain-specific discovery/capture lenses** rather than flattening the evidence into a generic summary. For example, component evidence should preserve consumes/produces/flow/infra/operational detail when available; runbook evidence should preserve safety/validation/rollback distinctions; standards evidence should preserve authority/counterexamples/exceptions.
4. Ask only questions that block accurate evidence capture. Leave optional gaps explicit instead of manufacturing completeness.
5. Allocate an ID using `STG-YYYYMMDD-<slug>`; scan existing staging IDs and add `-2`, `-3`, and so on deterministically for same-day collisions.
6. Capture the source/evidence, what is known, what is possible/unconfirmed, suggested curated targets, open questions, and the relevant bucket-specific sections supported by evidence.
7. Preserve uncertainty; never create reviewed or authoritative relationships here.
8. Write exactly one staging evidence entry for this workflow invocation. Do not create empty linked staging records just because another bucket is mentioned.
9. Do not list generated JSON maps as authoring targets; staging may suggest future relationship changes that will regenerate maps during curation.
10. Run `python scripts/atlas_lint.py .` after writing.
11. Never write `_curated/`, generated maps, curation status, or a review decision.

If the reusable knowledge originated from a private conversation or external source, obtain explicit user approval before persisting it.
