# Staging repository and component evidence

This bucket captures one bounded repository discovery record that can support one curated `repo.*` page and zero or more `comp.*` pages. Do not force the repository-to-component split before the evidence is gathered.

Store a record at `_staging/components/<domain>/<STG-ID>.md` only when its candidate primary domain is evidenced or user-confirmed. Otherwise use `unassigned`. A committed staging path is immutable by policy, so folder neatness is not evidence.

## What a useful scan captures

- Physical Git locator, logical repository root, observed repository type, ownership evidence and scan boundary, including exact selected commit, default-ref commit, merge base/relationship and future intake anchor.
- Evidence that the candidate is a meaningful standalone, monorepo-root, monorepo-project, nested-project, mirror or other source boundary; its enclosing repository candidate; and included/excluded paths.
- Monorepo, nested-repository or submodule topology; important source roots; explicit source/build repository dependencies.
- Source-owned setup, build, test and deployment documentation routes.
- Every plausible independently addressable component, its responsibility/boundary evidence, candidate parent and candidate domain. Record its paths relative to the candidate repository root.
- Per-candidate entrypoints and control flow, durable I/O, dependencies, infrastructure interactions, configuration, deployment, failure and operational context.
- One readable causal walkthrough for every component candidate: how it is entered or triggered, what material work it performs, which dependencies/state it uses, what it emits, and how failure or completion is observed.
- Known facts separately from possible conclusions, plus explicit questions for missing boundaries, domains and external context.

Use a single record even for a monorepo with several domains or deployables. Put a candidate-component column on detailed evidence so curation can split facts without guessing. Do not promote folders, domains or job groups into components unless they represent an independently addressable architectural boundary.

## Curation readiness

A repository page can be proposed when the source boundary, physical locator, logical root, important source structure and primary domain are evidenced. A component page can be proposed only when responsibility, repository membership, an independent architectural boundary and causal behavior are evidenced. Tables route facts; they do not replace the per-component explanation. It is valid to curate the repository and defer some or all component candidates.

Use `python scripts/atlas_query.py staging --bucket components` to inspect this evidence; add `--domain <domain>` when needed. README policy and staging evidence are never generated.
