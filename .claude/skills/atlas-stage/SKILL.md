---
name: atlas-stage
description: Use only after an explicit request to capture one coherent reusable datalens engineering fact as attributable staging evidence without curating it.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

# atlas-stage

Read `../_shared/human-intents.md`, `../_shared/persistence-approval.md`, `../_shared/runtime.md`, `../_shared/answer-provenance.md`, `_staging/README.md`, then the selected bucket README/template. This is the persistence step behind **Teach Atlas**. Do not use a subagent.

1. Determine whether this is a direct request or an approved internal handoff. For a direct request, show the shared concrete staging preview and obtain explicit scope-bound approval. For a handoff, verify that the passed approval covers the exact claims, files and targets; do not ask again. A reusable Questions handoff also contains a complete duplicate-search ledger: staging statuses/buckets and curated types/indexes searched; qualified question IDs; matching staging IDs/paths/statuses; curated candidate IDs/pages/ambiguity; selected targets; and unresolved candidates. Re-preview if the scope changed.
2. For a direct request, incomplete ledger or changed handoff, search staging plus typed curated `find`, exact routes and relevant indexes for semantic duplicates. For a complete unchanged Questions handoff, recheck only output-path uniqueness, exact qualified-question references, known duplicate states, and the selected target ID/page/status. Any new match, target change, ambiguity or material scope change invalidates the narrow path: repeat full duplicate discovery and return a revised preview. Treat find results as candidates and never silently select ambiguity. Choose the bucket by the primary reusable fact; split only independent semantic boundaries. Route broad investigation to `atlas-onboard-repository` and incremental merged-default-branch ranges to `atlas-stage-changes`.
3. Allocate a deterministic `STG-YYYYMMDD-<slug>` ID. Capture one coherent, curation-ready record using the common envelope and bucket-specific body: explain the reusable meaning, cite exact evidence, distinguish causality from adjacency, preserve known/possible states, evidence gaps and suggested curated targets. When evidence answers an Atlas open question, cite every originating qualified `<record-id>#<question-id>` in the body so active evidence can be detected without creating a new frontmatter field.
4. Flag sensitive artifacts without copying values. Never revise committed evidence; corrections are new staging records and only lifecycle may later alter top-level `status`.
5. Never write curated knowledge or generated artifacts. Run permitted validation unless explicitly deferred.
6. Use the shared plain-language completion summary, then include the new record, source evidence, duplicate-search routes and lifecycle as audit detail.
