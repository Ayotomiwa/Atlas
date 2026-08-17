---
name: atlas-lint
description: Validate or safely repair an Atlas package when the user asks to lint Atlas, fix Atlas validation failures, repair broken Atlas links, clean up contradictory or nonsensical Atlas documentation, or find likely missing Atlas links. Use deterministic lint for frontmatter and relative file links, and delegate broader semantic inspection when needed.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Agent
---

# atlas-lint

Read `../_shared/persistence-approval.md`, `../_shared/runtime.md`, `../_shared/answer-provenance.md`, and `../_shared/agent-handoffs.md`. Scripts validate structure; they are not semantic authority.

1. Resolve the requested paths or diff. Default an unqualified Atlas-wide request to the package root, but keep semantic inspection bounded to changed/requested files and their material routes.
2. Run `python scripts/atlas_lint.py <ATLAS_ROOT> --format json`. Treat it as the deterministic frontmatter and relative-file-link result only.
3. Delegate to `atlas-lint-analyst` when the request includes prose quality, contradictions, suspected sensitive content, unclear broken-link intent, stale guidance, or potentially missing semantic links. Supply the lint output, scope, contracts, exclusions, and write prohibition.
4. If the user requested fixes, apply only meaning-preserving repairs whose intended result is uniquely supported: frontmatter/YAML syntax, controlled values, exact relative paths, and spelling/grammar. Never invent a target or silently change a claim.
5. Treat missing links, connection changes, and factual corrections as evidence-sensitive. Use the proper staging/curation workflow or ask for the missing decision. Never rewrite committed staging evidence beyond its permitted lifecycle status.
6. Run `python scripts/rebuild_atlas.py` only when a structured or generated input changed; never hand-edit generated artifacts. Re-run lint and, when generation was relevant, `python scripts/rebuild_atlas.py --check`. Do not run tests unless explicitly requested.
7. When repairs were approved, create one exact-path local commit after validation. Report branch/commit, repaired files, unresolved findings, validation state, exact references, consulted paths, and material file hops. Do not cite lint output as the source of an engineering claim.

Never self-approve curated knowledge, push, merge, force-update, or publish.
