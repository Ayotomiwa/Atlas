---
name: implement-jira
description: Implement a Jira item using reusable engineering procedure while resolving TeamA standards from Atlas instead of hard-coding them in the skill.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

# implement-jira

1. Resolve the home Atlas package from the product repo's managed `CLAUDE.md` block and Atlas `package.md`.
2. Start from `_curated/standards/jira/index.md` and resolve the applicable curated Jira implementation standard.
3. Follow `atlas.extends` relationships when the selected standard specialises another standard.
4. Resolve relevant curated component and flow context using Atlas routing.
5. Read the product repository's own build/test/local-development instructions; those remain repository-owned.
6. Implement the Jira item in small, reviewable steps.
7. Run the local validation required by the product repository and applicable curated standards.
8. Report the Atlas standard/page IDs and paths used.
9. If reusable new engineering context is discovered, ask for explicit user approval before staging it with `atlas-stage`.
10. Never modify curated Atlas knowledge as a side effect of implementing the Jira item and never self-merge the product change.
