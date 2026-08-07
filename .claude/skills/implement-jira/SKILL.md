---
name: implement-jira
description: Use to implement a Jira work item while resolving TeamA engineering standards from Atlas instead of hard-coding team policy in the skill.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

# implement-jira

1. Resolve the home package via local `CLAUDE.md`/Atlas `package.md`.
2. Resolve the applicable Jira standard from `_curated/standards/jira/index.md`; follow `atlas.extends` when specialised.
3. Resolve relevant component/flow context.
4. Inspect the product repository's own build/test instructions.
5. Implement in small steps and run local required validation.
6. Report Atlas standards/pages used.
7. If reusable new context is discovered, ask user approval before staging via `atlas-stage`.
8. Never mutate curated Atlas knowledge as a side effect.
