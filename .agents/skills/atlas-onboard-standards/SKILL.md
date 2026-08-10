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
5. For every material candidate, capture more than the rule text: record source authority, observed scope/category, stated rationale when evidenced, concrete examples, counterexamples/conflicting practice, known exceptions, and whether mandatory/recommended status is actually supported.
6. Never promote a tool default, generated template or one-repository habit to a team standard without evidence or user confirmation. Repetition is evidence of practice, not proof of mandate.
7. Compare candidates with existing curated standards and category indexes, including possible `extends`, supersession or conflict relationships that curation may later evaluate.
8. Ask the user to confirm scope/authority for ambiguous high-value candidates; do not ask for optional details merely to fill the template.
9. Stage a standards-discovery record using the richer standards template. One scan may contain multiple candidates when they form one coherent discovery context; preserve enough structure that curation can split them later if needed.
10. Do not create governed `must-follow` applicability relationships from pattern frequency alone and never write curated standards.
11. Run lint and report classifications, evidence strength, counterexamples/exceptions and unresolved scope/authority questions.
