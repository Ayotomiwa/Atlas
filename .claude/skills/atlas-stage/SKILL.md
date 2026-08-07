---
name: atlas-stage
description: Capture one reusable engineering fact as raw Atlas evidence without curating it.
allowed-tools: Read, Grep, Glob, Write, Edit
---

# atlas-stage

Use for a reusable fact discovered during normal engineering work when a full service onboarding crawl is unnecessary. The source may be a merged code change, an investigation, an engineer-supplied finding or another authorised evidence source; a code MR/PR is not required.

1. Identify the correct `_staging/` bucket from `_staging/index.md`.
2. Read `_staging/README.md`, then that bucket's `README.md` and `_template.md` before writing. The root staging README owns lifecycle/immutability rules; the bucket README owns local semantics; the template owns capture shape.
3. Apply the bucket's **domain-specific discovery/capture lenses** rather than flattening the evidence into a generic summary. For example, component evidence should preserve consumes/produces/flow/infra/operational detail when available; runbook evidence should preserve safety/validation/rollback distinctions; standards evidence should preserve authority/counterexamples/exceptions.
4. Ask only questions that block accurate evidence capture. Leave optional gaps explicit instead of manufacturing completeness.
5. Allocate an ID using `STG-YYYYMMDD-<slug>`; scan existing staging IDs and add `-2`, `-3`, and so on deterministically for same-day collisions.
6. Create the record with `status: new`. Capture source/evidence, what is known, what is possible/unconfirmed, suggested curated targets, open questions, and the relevant bucket-specific sections supported by evidence.
7. Preserve uncertainty; never create reviewed or authoritative relationships here.
8. Write exactly one staging evidence entry for this workflow invocation unless the evidence clearly contains materially independent reusable findings that belong in separate semantic boundaries.
9. Do not create empty linked staging records merely because another bucket is mentioned and do not list generated JSON maps as authoring targets.
10. After first commit, never revise an existing staging record's evidence, metadata, path or ID. Only the curation lifecycle may later change its top-level `status`; corrections are new staging records.
11. Run `python scripts/atlas_lint.py .` after writing.
12. Never write `_curated/`, generated maps, curation status, or an approval decision.

For `_staging/changes/`, code-derived capture should normally inspect the approved/merged default-branch state; MR/PR identifiers are optional provenance rather than the staging boundary.

If reusable knowledge originated from a private conversation or external source, obtain explicit user approval before persisting it.
