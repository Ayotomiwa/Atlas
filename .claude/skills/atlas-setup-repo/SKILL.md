---
name: atlas-setup-repo
description: Safely create or update an Atlas-managed block in a product repository CLAUDE.md.
allowed-tools: Read, Grep, Glob, Write, Edit
---

# atlas-setup-repo

Preserve all existing content outside `<!-- atlas:managed:start -->` and `<!-- atlas:managed:end -->`. If no CLAUDE.md exists, create one with a short repository heading and managed block. Never copy Atlas knowledge into the local file. Use package + curated component identity; if unresolved, write package-only routing and mark component unresolved. On rerun replace only the managed block. Show the diff before finishing.
