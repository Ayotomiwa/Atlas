---
name: atlas-setup-repo
description: Safely create or update only the Atlas-managed block in a product repository CLAUDE.md while preserving all local instructions.
allowed-tools: Read, Grep, Glob, Write, Edit
---

# atlas-setup-repo

Read `../_shared/runtime.md`, `../_shared/answer-provenance.md`, and `assets/managed-block.md`.

1. Inspect the requested `CLAUDE.md`. Stop on duplicate, nested, reversed or malformed Atlas markers.
2. At a physical monorepo root, record package `teama` and path-derived context behavior. In an existing nested `CLAUDE.md`, a specific reviewed `repo.*` seed may be recorded when it resolves exactly.
3. If the file does not exist, create only a minimal file containing the managed block. Do not discover or author unrelated build/test/style instructions and do not create managed files across every product folder.
4. Replace only content between the markers; preserve every byte outside them. Do not commit an absolute Atlas path or copy Atlas knowledge into the product repository.
5. Use reviewed-and-merged trust wording and make the non-`main`/`master` warning advisory. Show the exact repository-relative file and diff changed.
