# Atlas runtime contract

Use `human-intents.md` for the user-facing action and keep this file's search, trust and fallback mechanics behind that conversation. Users do not select specialist workflows or query commands.

For automatic routing in a product repository, a valid managed Atlas block in its instructions is the binding signal. **Explicit Ask Atlas** always consults Atlas, whether the repository is bound or unbound. In an **unbound repository** without that explicit intent, do not invoke Atlas automatically. In a bound repository, one known local target may be read directly; an uncertain, broad, multi-hop, Git-history, or durable-context lookup routes through Atlas before broad source search. `ATLAS_ROOT` stored-knowledge and implementation modes remain governed by the classification below.

Use this three-way entrance after Atlas eligibility is established:

1. **Retained evidence** when the same repository, revision, question type and required confidence remain compatible and the evidence still supports every material claim.
2. **Exact source boundary** when a bound-repository question is genuinely local and identifies one known file, symbol or isolated edit. Explicit Ask Atlas does not use this bypass.
3. **Atlas first** for Explicit Ask Atlas and for uncertain, broad, multi-hop, Git-history, durable-context, impact, ownership, conflict, standards, recovery or readiness questions.

After selecting the entrance, open the selected curated page and follow its answer-bearing links. Use the relevant collection/domain index fallback when identity is weak or ambiguous, use maps only for reverse or multi-hop traversal after stable-ID selection, and perform the smallest bounded source check where Atlas coverage ends. Preserve an unresolved boundary when neither Atlas nor authorised source closes the question.

Resolve `ATLAS_ROOT` from `${CLAUDE_SKILL_DIR}`: the live package root is three directories above an Atlas skill directory. Canonicalise the absolute path and validate that `<ATLAS_ROOT>/atlas-package.json` exists, has `schema_version: atlas-package/1.0`, and identifies the expected package before using Atlas. If resolution or validation fails, state that Atlas was not consulted, tell the user to restart with `claude --add-dir <path-to-current-Atlas-checkout>`, explain that a moved checkout must be supplied again, and offer bounded product-source inspection.

Keep these locations distinct:

- `ATLAS_ROOT`: this context package and its scripts, maps, indexes and pages;
- product root: the physical Git root containing the source being discussed;
- current path: the user's immediate file or directory, which may identify a logical repository/component inside a monorepo.

The locations may overlap. When the current path is inside `ATLAS_ROOT`, classify the question before routing:

- **Stored-knowledge mode:** the question asks what Atlas knows about an engineering repository, component, flow, infrastructure, schema, standard, operation, concept, ownership route or stable ID. Resolve an explicit ID directly; otherwise run typed `find` without `--path`, then use the relevant curated collection/domain index and root index as fallback. Do not run product path context or offer product setup for Atlas itself.
- **Atlas-implementation mode:** the question asks about Atlas scripts, skills, contracts, templates, generation, lint, tests or repository behavior. Inspect the Atlas repository as ordinary local source. Do not force a curated lookup merely because the checkout is Atlas.

If stored knowledge needs repository fallback, use an explicitly supplied product path or the selected repository record's locator only when it resolves to an available separate checkout. Never treat `ATLAS_ROOT` as product evidence for an unrelated record. If no product checkout is available, state where Atlas coverage ended.

Pass absolute paths internally and to agents. In user-facing answers, cite paths relative to the applicable Atlas or product root.

Keep an ephemeral Atlas session state inside the current conversation only:

- validated Atlas root, product root and current path;
- selected IDs and already-opened pages;
- requested revision or range, when the question names one;
- resolved full commit or range for repository reads;
- product-source paths already inspected and the revision used for each inspected source path;
- the current coverage endpoint;
- the current route class: `retained-context`, `source-only`, `atlas-only`, `atlas-plus-source` or `unresolved`;
- whether the checkout advisory has already been disclosed.

A new conversation starts cold; never persist this ephemeral Atlas session state. Reuse it only while repository, revision, question type and required confidence remain compatible, the selected record still applies and no source or checkout change is suspected. For an unchanged local follow-up, do not repeat an Atlas query, page open or source read that retained context already answers. A revision change invalidates only the affected source evidence and re-enters routing for that scope. Git at that revision is authoritative for past implementation; current Atlas knowledge may locate the boundary but never becomes historical evidence.

Choose the route class from the evidence actually used: retained context only is `retained-context`; direct repository evidence without a current-question Atlas route is `source-only`; Atlas without source is `atlas-only`; Atlas followed by source at its coverage endpoint is `atlas-plus-source`; and an unclosed material gap is `unresolved`. Full ordered access events belong only in Atlas routing evaluation artifacts, never normal product-session state or a new persistent service.

Batch independent Atlas reads of already selected records, and batch Atlas-located source verification when the missing claims share one authorised boundary; do not widen scope merely to batch.

When already verified repository evidence remains current and supports every material follow-up claim at the required confidence, a follow-up may use it with zero new retrieval; do not force fallback merely because the original Atlas edge was possible; related evidence must not upgrade a different uncertain edge.

Re-enter the applicable Atlas routing mode when the repository, requested revision, selected record or question type changes; source or checkout state may have changed; the question crosses the recorded coverage endpoint; or the work concerns impact, ownership, conflicts, standards, recovery or another boundary. Re-entry opens only the routes needed for the new scope and carries still-valid session state into any specialist handoff.

For ordinary product questions outside `ATLAS_ROOT`, the typed hybrid entrance is eligible after direct Ask Atlas or when the current product repository contains a valid managed Atlas block. `matched`, `path-derived`, and `not-verified` managed bindings are eligible; only `not-verified` requires the routing-only advisory below. In an unbound repository without explicit intent, do not query Atlas. When eligible, resolve an explicit stable ID directly. Otherwise infer likely curated types and run:

```text
python <ATLAS_ROOT>/scripts/atlas_query.py --root <ATLAS_ROOT> --format json find <query> --type <type> --path <current-path>
```

Search returns candidates, not truth. Select using the question, match reasons, path specificity and curated evidence; preserve ambiguity. Consult the relevant collection/domain index when results are weak or ambiguous, then the curated root index. Open the selected page and follow its links. Use maps only after stable-ID selection for reverse or multi-hop traversal. Use `context` separately when repository/component path candidates need inspection.

Allow `locator_match: not-verified` product candidates, but include a visible routing-only advisory in every substantive answer that uses one: path context was routing evidence rather than proof of repository identity. If an Atlas-relevant product repository outside `ATLAS_ROOT` lacks a valid managed instructions block, make one non-blocking `atlas-setup-repo` offer per repository/session; discovery remains read-only.

Route through curated Atlas before broad product-source exploration. If Atlas is insufficient, state where coverage ended and continue with a bounded source inspection inside the user's scope. `_staging/` records are non-authoritative routing and completeness evidence, never factual authority. Never use generated maps, query output, generation or lint as semantic authority.

Lifecycle determines trust: every `status: curated` page is `authoritative`, while deprecated content is `deprecated` and non-authoritative. Query reports Git separately as `checkout_state`; mention a non-`main-clean` state once and briefly, without blocking or downgrading authority. Merge changes the checkout advisory automatically and requires no page-status mutation.

Use decision-weighted capture: preserve safety-critical lifecycle, compatibility, ownership, contracts, conflicts, recovery constraints and material impact behavior. Treat exact volatile values as source-authoritative, including commands, code, configuration, and IaC literals. Atlas may locate them; copy an exact value only when the value itself affects safety, compatibility, operation or blast radius. Never copy sensitive values.

Scripts resolve, traverse, compile and validate. They do not decide what a result means, whether more exploration is required, or how an answer should be presented.
