---
name: atlas-onboard-standards
description: Use to discover candidate reusable TeamA engineering standards from one or more repositories without mistaking repo-local config or tool defaults for team policy.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

# atlas-onboard-standards

1. Read `_staging/standards/README.md`, its template and `taxonomy/standard-categories.yaml`.
2. Inspect policy/config evidence such as CONTRIBUTING/README guidance, CI templates, parent POM/shared Gradle config, lint/format/test config, PR templates, Jira conventions, IaC conventions, security checks, common scripts and repeated patterns.
3. Classify each finding as `team-standard-candidate`, `repo-local-convention`, `tool-default`, or `unknown-scope`.
4. Never upgrade a tool default or one-repo habit into team policy without evidence/user confirmation.
5. Compare candidates with existing curated standards/category indexes.
6. Ask the user to confirm scope/authority for ambiguous high-value candidates.
7. Stage a standards discovery record with candidate category, rule, source paths, scope evidence, exceptions/unknowns and suggested curated target. One scan may hold several candidates.
8. Never write curated standards.
