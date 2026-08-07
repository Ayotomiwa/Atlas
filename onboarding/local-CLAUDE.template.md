<!-- atlas:managed:start -->
## Atlas context

Home Atlas package: `teama`
Atlas component: `<curated component id or unresolved>`

When TeamA Atlas is available (for example through `claude --add-dir <atlas-path>`):
1. use the `atlas-discover` skill before broad platform-context scanning;
2. use `atlas-impact` for blast-radius questions;
3. treat `_curated/` as authoritative only for pages with `status: curated`;
4. treat `_staging/` as evidence only;
5. if Atlas does not cover the question, continue with normal repository discovery and label the result as not Atlas-backed.

This repository owns its exact build, test, lint and local-development commands.
<!-- atlas:managed:end -->
