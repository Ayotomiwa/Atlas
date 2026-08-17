---
name: atlas-setup-repo
description: Safely create or update only the Atlas-managed block in a product repository CLAUDE.md while preserving all local instructions.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

# atlas-setup-repo

Read `../_shared/persistence-approval.md`, `../_shared/runtime.md`, `../_shared/answer-provenance.md`, and `assets/managed-block.md`.

1. Resolve and validate `ATLAS_ROOT`, discover the physical Git root, and run path context. If Atlas cannot be resolved, state that it was not consulted and tell the user to restart with `claude --add-dir <path-to-current-Atlas-checkout>`.
2. Select one target boundary only. Prefer the selected curated repository's `repository_root`; otherwise use the physical Git root. Merge an existing `CLAUDE.md` there. Create a minimal file only when Git or a curated repository record supports the boundary and that directory contains a README. Never create files across sibling products.
3. At a physical monorepo root use `path-derived`. At a logical boundary record the selected `repo.*` ID with `matched` or `not-verified`; preserve ambiguity rather than choosing a seed silently.
4. Complete Git preflight in the selected product repository. Run `scripts/manage_agent_block.py inspect`, then `dry-run` with this skill's asset. Stop on malformed markers. Preview branch, target, diff and local commit; apply only after direct invocation or the user's accepted setup offer.
5. Preserve every byte outside the managed markers. Do not commit absolute Atlas/product paths, copy Atlas knowledge, or author unrelated build/test/style instructions.
6. Create one exact-path local commit, then show branch/commit, repository-relative target and exact diff. Explain that a `not-verified` seed remains a routing candidate and requires an advisory in every answer that uses it.
