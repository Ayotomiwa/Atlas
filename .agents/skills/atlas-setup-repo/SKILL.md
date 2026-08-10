---
name: atlas-setup-repo
description: Safely create or update the Atlas-managed block in a product repository AGENTS.md without replacing local instructions.
allowed-tools: Read, Grep, Glob, Write, Edit
---

# atlas-setup-repo

Preserve all existing content outside the Atlas-managed markers.

1. Read the product repository's existing `AGENTS.md` if present.
2. Resolve home package `teama` and the curated component ID when one exists.
3. If no curated component ID exists, use package-only routing and set the component identity to `unresolved`; never point the product repo to staging as authoritative.
4. If no `AGENTS.md` exists, initialize it normally by discovering and documenting the repository's build, test, lint, and run commands, along with any local code style rules. Then, append the Atlas-managed block.
5. On rerun, replace only the content between the two markers below.
6. Do not copy Atlas knowledge into the product repository. The product repository continues to own its exact build/test/run instructions.
7. Show the resulting diff before finishing.

```markdown
<!-- atlas:managed:start -->
## Atlas context

Home Atlas package: `teama`
Atlas component: `<curated component id or unresolved>`

When TeamA Atlas is available (for example through `Codex --add-dir <atlas-path>`):
1. use the `atlas-discover` skill before broad platform-context scanning;
2. use `atlas-impact` for blast-radius questions;
3. treat `_curated/` as authoritative only for pages with `status: curated`;
4. treat `_staging/` as evidence only;
5. if Atlas does not cover the question, continue with normal repository discovery and label the result as not Atlas-backed.

This repository owns its exact build, test, lint and local-development commands.
<!-- atlas:managed:end -->
```
