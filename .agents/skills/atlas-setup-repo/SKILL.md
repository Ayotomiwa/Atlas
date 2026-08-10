---
name: atlas-setup-repo
description: Safely create or update only the Atlas-managed block in a product repository AGENTS.md while preserving all local instructions.
---

# atlas-setup-repo

Read shared runtime/provenance and `assets/managed-block.md`.

1. Inspect the requested `AGENTS.md`; stop on malformed/duplicate markers.
2. At monorepo root record package and path-derived context. In an existing nested file, include a specific reviewed `repo.*` seed only when exact.
3. If absent, create only a minimal managed block. Do not author unrelated build/test/style guidance or create files across all product folders.
4. Replace only the managed block, preserve everything else, never commit absolute Atlas paths, and show the exact repository-relative diff.
