# Atlas runtime contract

Use `human-intents.md` for the user-facing action and keep this file's search, trust and fallback mechanics behind that conversation. Users do not select specialist workflows or query commands.

Resolve `ATLAS_ROOT` from `${CLAUDE_SKILL_DIR}`: the live package root is three directories above an Atlas skill directory. Canonicalise the absolute path and validate that `<ATLAS_ROOT>/atlas-package.json` exists, has `schema_version: atlas-package/1.0`, and identifies the expected package before using Atlas. If resolution or validation fails, state that Atlas was not consulted, tell the user to restart with `claude --add-dir <path-to-current-Atlas-checkout>`, explain that a moved checkout must be supplied again, and offer bounded product-source inspection.

Keep these locations distinct:

- `ATLAS_ROOT`: this context package and its scripts, maps, indexes and pages;
- product root: the physical Git root containing the source being discussed;
- current path: the user's immediate file or directory, which may identify a logical repository/component inside a monorepo.

Pass absolute paths internally and to agents. In user-facing answers, cite paths relative to the applicable Atlas or product root.

For ordinary product questions, use a typed hybrid entrance. Resolve an explicit stable ID directly. Otherwise infer likely curated types and run:

```text
python <ATLAS_ROOT>/scripts/atlas_query.py --root <ATLAS_ROOT> --format json find <query> --type <type> --path <current-path>
```

Search returns candidates, not truth. Select using the question, match reasons, path specificity and curated evidence; preserve ambiguity. Consult the relevant collection/domain index when results are weak or ambiguous, then the curated root index. Open the selected page and follow its links. Use maps only after stable-ID selection for reverse or multi-hop traversal. Use `context` separately when repository/component path candidates need inspection.

Allow `locator_match: not-verified` candidates, but state in every substantive answer that uses one that path context was routing evidence rather than proof of repository identity. If an Atlas-relevant product repository lacks a valid managed instructions block, make one non-blocking `atlas-setup-repo` offer per repository/session; discovery remains read-only.

Route through curated Atlas before broad product-source exploration. If Atlas is insufficient, state where coverage ended and continue with a bounded source inspection inside the user's scope. Never use staging, generated maps, query output, generation or lint as semantic authority.

Lifecycle determines trust: every `status: curated` page is `authoritative`, while deprecated content is `historical`. Query reports Git separately as `checkout_state`; mention a non-`main-clean` state once and briefly, without blocking or downgrading authority. Merge changes the checkout advisory automatically and requires no page-status mutation.

Use decision-weighted capture: preserve safety-critical lifecycle, compatibility, ownership, contracts, conflicts, recovery constraints and material impact behavior. Keep precise source anchors for volatile literals; copy an exact value only when the value itself affects safety, compatibility, operation or blast radius. Never copy sensitive values.

Scripts resolve, traverse, compile and validate. They do not decide what a result means, whether more exploration is required, or how an answer should be presented.
