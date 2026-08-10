<!-- atlas:managed:start -->
## Atlas context

Home Atlas package: `teama`
Atlas repository seed: `<reviewed repo.* ID when exact, otherwise path-derived>`

When TeamA Atlas is loaded with `claude --add-dir <ATLAS_ROOT>`:

1. use `atlas-discover` when durable architecture or cross-system context can improve the answer;
2. use `atlas-impact` for explicit blast-radius, change-risk, migration, deletion or failure questions;
3. resolve ordinary source context from the current path and preserve ambiguous candidates;
4. treat only human-reviewed, merged `_curated/` pages with `status: curated` as authoritative;
5. treat `_staging/` as evidence only;
6. continue with bounded repository discovery when Atlas coverage ends and disclose that boundary;
7. warn outside `main` or `master` without blocking the task.

This repository owns its exact build, test, lint and local-development commands.
<!-- atlas:managed:end -->
