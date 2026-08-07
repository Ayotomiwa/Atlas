---
name: atlas-onboard-standards
description: Discover candidate reusable TeamA standards from repositories while separating team policy from repo-local conventions and tool defaults.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

# atlas-onboard-standards

1. Read `_staging/standards/README.md`, `_staging/standards/_template.md`, `taxonomy/standard-categories.yaml`, and the curated standards indexes.
2. Use `atlas-repo-analyst` in `standards-discovery` mode for deep read-only scanning when useful.
3. Inspect evidence such as CONTRIBUTING/README guidance, CI templates, parent POM/shared Gradle configuration, lint/format/test config, PR templates, documented Jira conventions, IaC conventions, security checks, common scripts, and repeated patterns across accessible repositories.
4. Classify each finding as `team-standard-candidate`, `repo-local-convention`, `tool-default`, or `unknown-scope`.
5. Never promote a tool default or one-repository habit to a team standard without evidence or user confirmation.
6. Compare candidates with existing curated standards and category indexes.
7. Ask the user to confirm scope/authority for ambiguous high-value candidates.
8. Stage one standards-discovery record that can contain multiple candidates, including category, rule, source paths, scope evidence, exceptions/unknowns, and suggested curated targets.
9. Curation may later split candidates into separate `atlas.standard` pages; this skill never writes curated standards.
10. Run lint and report the classifications and unresolved scope questions.
