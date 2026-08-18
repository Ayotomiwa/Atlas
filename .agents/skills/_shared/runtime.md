# Atlas runtime contract for Codex

Use `human-intents.md` for the user-facing action and keep specialist/query mechanics behind the conversation.

For automatic routing in a product repository, a valid managed Atlas block in its instructions is the binding signal. **Explicit Ask Atlas** always consults Atlas, whether the repository is bound or unbound. In an **unbound repository** without that explicit intent, do not invoke Atlas automatically. In a bound repository, one known local target may be read directly; an uncertain, broad, multi-hop, Git-history, or durable-context lookup routes through Atlas before broad source search. `ATLAS_ROOT` stored-knowledge and implementation modes remain governed by the classification below.

Use this ordered retrieval ladder for a bound repository or Explicit Ask Atlas; direct Ask enters Atlas no later than step 3:

1. **Retained context** that still answers the unchanged question.
2. **One known targeted source read** for a clearly local question or local isolated edit.
3. **Atlas before uncertain** or broad, multi-hop, Git-history, durable-context, impact, ownership, conflict, standards or recovery lookup.
4. **Complete Atlas answer** when curated evidence fully supports the result.
5. **Partial Atlas answer** plus the smallest source fallback where coverage ends.
6. **Atlas-guided source route** when Atlas identifies the next evidence boundary but cannot answer.
7. **Bounded source and unresolved gap** when neither Atlas nor the authorised source boundary closes the question.

Resolve the live `ATLAS_ROOT` from the current skill location (three directories above an Atlas skill directory) and validate `atlas-package.json` with `schema_version: atlas-package/1.0`. If unavailable, state that Atlas was not consulted, ask the user to make the current checkout available, and offer bounded repository inspection. Keep Atlas root, product Git root and current path distinct even when paths overlap. Use absolute internal paths but repository-relative paths in user-facing references.

When the current path is inside `ATLAS_ROOT`, choose one mode. A question about an explicit stable ID resolves that ID directly. Other questions about stored engineering repositories/components/flows/infra/schemas/standards/operations/concepts/ownership use typed `find` without `--path`, then relevant curated indexes; do not run product context or offer setup for Atlas. A question about Atlas scripts/skills/contracts/templates/generation/lint/tests uses ordinary local source inspection. Stored-knowledge source fallback requires an explicitly available separate product checkout or resolved repository locator; never inspect Atlas implementation as product evidence.

Keep an ephemeral Atlas session state inside the current conversation only: validated Atlas/product roots and current path; selected stable IDs and opened curated pages; inspected product-source paths; the current coverage endpoint; and whether the checkout advisory was already disclosed. A new conversation starts cold; never persist this state.

Reuse the state only while the selected routing mode, product repository where applicable, selected record and evidence, and question type remain unchanged and no source or checkout change is suspected. An unchanged local follow-up does not repeat an Atlas query, page open or source read that retained context already answers. Re-enter the applicable Atlas routing mode when the repository or selected record changes, source or checkout state may have changed, the question crosses the coverage endpoint, or the work concerns impact, ownership, conflicts, standards, recovery or another boundary. Open only the routes needed for the new scope and carry still-valid state into specialist handoffs.

Outside `ATLAS_ROOT`, this entrance is eligible only after direct Ask Atlas or a verified bound-repository handoff. In an unbound repository without explicit intent, do not query Atlas. When eligible, resolve explicit stable IDs directly; otherwise infer likely types and run `python <ATLAS_ROOT>/scripts/atlas_query.py --root <ATLAS_ROOT> --format json find <query> --type <type> --path <current-path>`. Treat results as candidates; preserve ambiguity and let the question/evidence decide. Use the relevant collection/domain index when results are weak or ambiguous, then the curated root index. Open the selected page and use maps only for reverse or multi-hop traversal. The manifest registers routes but is not a mandatory navigation hop.

Allow `not-verified` repository candidates but include a visible routing-only advisory in every substantive answer that uses one. Discovery may offer `atlas-setup-repo` once per external product repository/session when its instructions lack a managed Atlas block, but never for `ATLAS_ROOT` and never writes automatically.

Route through curated Atlas before broad source exploration, then continue with bounded product inspection when coverage ends. `_staging/` records are non-authoritative routing and completeness evidence, never factual authority. Lifecycle determines trust: every `status: curated` page is authoritative and deprecated content is historical. Treat `checkout_state` as a separate, non-blocking advisory; mention it once and briefly only when it is not `main-clean`.

Use decision-weighted capture: preserve safety-critical lifecycle, compatibility, ownership, contracts, conflicts, recovery constraints and material impact behavior. Anchor volatile literals at source and copy an exact value only when the value itself affects safety, compatibility, operation or blast radius. Never copy sensitive values.

Scripts resolve, traverse, compile and validate. They are never semantic authority and do not decide interpretation, further exploration or presentation.
