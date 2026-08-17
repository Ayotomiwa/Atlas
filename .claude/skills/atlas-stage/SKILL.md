---
name: atlas-stage
description: Use only after an explicit request to capture one coherent reusable datalens engineering fact as attributable staging evidence without curating it.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

# atlas-stage

Read `../_shared/human-intents.md`, `../_shared/persistence-approval.md`, `../_shared/runtime.md`, `../_shared/answer-provenance.md`, `../_shared/curation-safety.md`, `_staging/README.md`, then the selected bucket README/template/index. This is the persistence step behind **Teach Atlas**. Do not use a subagent.

1. Determine whether this is a direct request or an approved internal handoff. For a direct request, show the shared concrete staging preview and obtain explicit scope-bound approval. For a handoff, verify that the passed approval covers the exact claims, files and targets; do not ask again. Re-preview if the scope changed.
2. Search staging plus typed curated `find`, exact routes and relevant indexes for semantic duplicates. Treat find results as candidates and never silently select ambiguity. Choose the bucket by the primary reusable fact; split only independent semantic boundaries. Route broad investigation to `atlas-onboard-repository` and incremental merged-default-branch ranges to `atlas-stage-changes`.
3. Complete the shared taxonomy/contract and destination-contract reads before authoring. Allocate a deterministic `STG-YYYYMMDD-<slug>` ID. Capture one coherent, curation-ready record using the common envelope and bucket-specific body: explain the reusable meaning, cite exact evidence, distinguish causality from adjacency, preserve known/possible states, evidence gaps and suggested curated targets. When evidence answers an Atlas open question, cite every originating qualified `<record-id>#<question-id>` in the body so active evidence can be detected without creating a new frontmatter field.
4. Flag sensitive artifacts without copying values. Never revise committed evidence; corrections are new staging records and only lifecycle may later alter top-level `status`.
5. Never write curated knowledge or generated artifacts. Run permitted validation unless explicitly deferred.
6. Use the shared plain-language completion summary, then include the new record, source evidence, duplicate-search routes and lifecycle as audit detail.
