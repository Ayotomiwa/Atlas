---
name: atlas-setup-repo
description: Safely create or update only the Atlas-managed block in a product repository AGENTS.md while preserving all local instructions.
---

# atlas-setup-repo

Read shared runtime/provenance and `assets/managed-block.md`.

1. Resolve Atlas, discover the physical Git root, and run path context. If Atlas is unavailable, state that it was not consulted, ask the user to make the current checkout available, and offer bounded repository inspection.
2. Select one target boundary. Prefer the selected curated repository's `repository_root`; otherwise use the Git root. Merge an existing `AGENTS.md`. Create a minimal file only when Git or a curated record supports the boundary and it contains a README. Never create files across sibling products.
3. Use `path-derived` at a monorepo root. At a logical boundary record the selected `repo.*` ID with `matched` or `not-verified`; never silently choose ambiguity.
4. Run `scripts/manage_agent_block.py inspect` and `dry-run` with the Codex asset. Stop on malformed markers and apply only after direct invocation or an accepted setup offer.
5. Preserve every byte outside markers, omit absolute checkout paths and unrelated instructions, and show the exact repository-relative diff. Require an advisory whenever a `not-verified` seed is used.
