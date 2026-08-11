# Atlas runtime contract for Codex

Resolve the live `ATLAS_ROOT` from the current skill location (three directories above an Atlas skill directory) and validate `atlas-package.json` with `schema_version: atlas-package/1.0`. If unavailable, state that Atlas was not consulted, ask the user to make the current checkout available, and offer bounded repository inspection. Keep Atlas root, product Git root and current path separate. Use absolute internal paths but repository-relative paths in user-facing references.

Resolve explicit stable IDs directly. Otherwise infer likely types and run `python <ATLAS_ROOT>/scripts/atlas_query.py --root <ATLAS_ROOT> --format json find <query> --type <type> --path <current-path>`. Treat results as candidates; preserve ambiguity and let the question/evidence decide. Use the relevant collection/domain index when results are weak or ambiguous, then the curated root index. Open the selected page and use maps only for reverse or multi-hop traversal. The manifest registers routes but is not a mandatory navigation hop.

Allow `not-verified` repository candidates but include a visible routing-only advisory in every substantive answer that uses one. Discovery may offer `atlas-setup-repo` once per repository/session when the product instructions lack a managed Atlas block, but never writes automatically.

Route through curated Atlas before broad source exploration, then continue with bounded product inspection when coverage ends. Lifecycle determines trust: every `status: curated` page is authoritative and deprecated content is historical. Treat `checkout_state` as a separate, non-blocking advisory; mention it once and briefly only when it is not `main-clean`.

Use decision-weighted capture: preserve safety-critical lifecycle, compatibility, ownership, contracts, conflicts, recovery constraints and material impact behavior. Anchor volatile literals at source and copy an exact value only when the value itself affects safety, compatibility, operation or blast radius. Never copy sensitive values.

Scripts resolve, traverse, compile and validate. They are never semantic authority and do not decide interpretation, further exploration or presentation.
