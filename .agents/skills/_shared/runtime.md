# Atlas runtime contract for Codex

Resolve the live `ATLAS_ROOT` from the current skill location (three directories above an Atlas skill directory) and validate `atlas-package.json` with `schema_version: atlas-package/1.0`. Keep Atlas root, product Git root and current path separate. Use absolute internal paths but repository-relative paths in user-facing references.

For ordinary product questions, run `python <ATLAS_ROOT>/scripts/atlas_query.py --root <ATLAS_ROOT> --format json context <current-path>`. Treat results as candidates; preserve ambiguity and let the question/evidence determine the selection. Use exact stable IDs after path context. The manifest registers routes but is not a mandatory navigation hop.

Route through curated Atlas before broad source exploration, then continue with bounded product inspection when coverage ends. Distinguish reviewed Atlas, local/unmerged Atlas, repository-derived, user-confirmed, inferred, conflicting and unknown facts. Only human-reviewed, merged `status: curated` pages are authoritative. Warn outside `main` or `master` and continue.

Scripts resolve, traverse, compile and validate. They are never semantic authority and do not decide interpretation, further exploration or presentation.
