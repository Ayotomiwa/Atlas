---
name: atlas-setup-repo
description: Use to safely create or update the Atlas-managed block in a product repository CLAUDE.md while preserving repository-owned instructions.
allowed-tools: Read, Grep, Glob, Write, Edit
---

# atlas-setup-repo

1. Preserve every existing user line outside `<!-- atlas:managed:start -->` and `<!-- atlas:managed:end -->`.
2. If no `CLAUDE.md` exists, create one with a short repository heading plus the managed block from `onboarding/local-CLAUDE.template.md`.
3. Never copy Atlas knowledge into the local file.
4. Use package + curated component identity, not an absolute Atlas path. If no curated component ID exists, write package-only routing and `unresolved`; never point to staging as authoritative.
5. On rerun replace only the managed block.
6. Show the diff before finishing. The product repo owns build/test/run commands.
