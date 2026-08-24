---
name: atlas-lint
description: Validate or safely repair an Atlas package when asked to lint Atlas, fix validation failures or broken links, clean contradictory or nonsensical Atlas documentation, or find likely missing Atlas links.
---

# atlas-lint

Read the shared persistence, runtime, provenance, handoff and clear-writing contracts. Run `python scripts/atlas_lint.py <ATLAS_ROOT> --format json` for deterministic frontmatter and relative-file-link validation. Use `atlas-humanize` for a requested bounded prose rewrite; lint remains the correctness and repair workflow.

Delegate broader semantic inspection to `atlas-lint-analyst`. Classify the likely root cause as page, template, generator, contract, shared workflow or repeated agent behavior. For a recurring mechanically decidable issue, propose the strongest structural fix—lint, template, contract or generator—without expanding the approved repair scope. When fixes are requested, apply only uniquely supported, meaning-preserving YAML/frontmatter, controlled-value, relative-path, spelling or grammar repairs, applying the clear-writing preservation rules to persisted prose. Treat missing links, connection changes and factual corrections as evidence-sensitive; use staging/curation or ask when support is incomplete. Never rewrite committed staging evidence or hand-edit generated artifacts.

Run generation only after structured/generated inputs change, then rerun lint and the freshness check. Do not run tests unless explicitly requested. For approved repairs, create one exact-path local commit after validation. Report branch/commit, root-cause class, structural follow-up, exact references, file hops, consulted paths, repairs, unresolved findings and validation. Never approve, push, merge, force-update or publish.
