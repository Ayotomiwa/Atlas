# Atlas runtime contract

Resolve `ATLAS_ROOT` from `${CLAUDE_SKILL_DIR}`: the live package root is three directories above an Atlas skill directory. Canonicalise the absolute path and validate that `<ATLAS_ROOT>/atlas-package.json` exists, has `schema_version: atlas-package/1.0`, and identifies the expected package before using Atlas.

Keep these locations distinct:

- `ATLAS_ROOT`: this context package and its scripts, maps, indexes and pages;
- product root: the physical Git root containing the source being discussed;
- current path: the user's immediate file or directory, which may identify a logical repository/component inside a monorepo.

Pass absolute paths internally and to agents. In user-facing answers, cite paths relative to the applicable Atlas or product root.

For ordinary product questions, start with:

```text
python <ATLAS_ROOT>/scripts/atlas_query.py --root <ATLAS_ROOT> --format json context <current-path>
```

Use the returned repository/component candidates as candidates, not automatic truth. Select by the user's question, path specificity and evidence; preserve ties or ambiguity. Once context is selected, prefer exact stable IDs and map-provided page routes. Use `atlas-package.json` for registered maps, taxonomy, contracts, domains and entrypoints, but do not make it an obligatory navigation hop.

Route through curated Atlas before broad product-source exploration. If Atlas is insufficient, state where coverage ended and continue with a bounded source inspection inside the user's scope. Never use staging, generated maps, query output, generation or lint as semantic authority.

Distinguish facts as reviewed Atlas, unmerged/local Atlas, repository-derived, user-confirmed, inferred, conflicting, or unknown. Only human-reviewed, merged `status: curated` pages are authoritative. Outside `main` or `master`, warn that local Atlas may include unmerged work and continue; the warning is never a blocker.

Scripts resolve, traverse, compile and validate. They do not decide what a result means, whether more exploration is required, or how an answer should be presented.
