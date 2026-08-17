# Atlas runtime contract for Codex

Use `human-intents.md` for the user-facing action and keep specialist/query mechanics behind the conversation.

Resolve the live `ATLAS_ROOT` from the current skill location (three directories above an Atlas skill directory) and validate `atlas-package.json` with `schema_version: atlas-package/1.0`. If unavailable, state that Atlas was not consulted, ask the user to make the current checkout available, and offer bounded repository inspection. Keep Atlas root, product Git root and current path separate. Use absolute internal paths but repository-relative paths in user-facing references.

Keep an ephemeral Atlas session state inside the current conversation only: validated Atlas/product roots and current path; selected stable IDs and opened curated pages; inspected product-source paths; the current coverage endpoint; and whether the checkout advisory was already disclosed. A new conversation starts cold; never persist this state.

Reuse the state only while the product repository, selected record and evidence, and question type remain unchanged and no source or checkout change is suspected. An unchanged local follow-up does not repeat an Atlas query, page open or source read that retained context already answers. Re-enter Atlas when the repository or selected record changes, source or checkout state may have changed, the question crosses the coverage endpoint, or the work concerns impact, ownership, conflicts, standards, recovery or another boundary. Open only the routes needed for the new scope and carry still-valid state into specialist handoffs.

Resolve explicit stable IDs directly. Otherwise infer likely types and run `python <ATLAS_ROOT>/scripts/atlas_query.py --root <ATLAS_ROOT> --format json find <query> --type <type> --path <current-path>`. Treat results as candidates; preserve ambiguity and let the question/evidence decide. Use the relevant collection/domain index when results are weak or ambiguous, then the curated root index. Open the selected page and use maps only for reverse or multi-hop traversal. The manifest registers routes but is not a mandatory navigation hop.

Allow `not-verified` repository candidates but include a visible routing-only advisory in every substantive answer that uses one. Discovery may offer `atlas-setup-repo` once per repository/session when the product instructions lack a managed Atlas block, but never writes automatically.

Route through curated Atlas before broad source exploration, then continue with bounded product inspection when coverage ends. Lifecycle determines trust: every `status: curated` page is authoritative and deprecated content is historical. Treat `checkout_state` as a separate, non-blocking advisory; mention it once and briefly only when it is not `main-clean`.

Use decision-weighted capture: preserve safety-critical lifecycle, compatibility, ownership, contracts, conflicts, recovery constraints and material impact behavior. Anchor volatile literals at source and copy an exact value only when the value itself affects safety, compatibility, operation or blast radius. Never copy sensitive values.

Scripts resolve, traverse, compile and validate. They are never semantic authority and do not decide interpretation, further exploration or presentation.
