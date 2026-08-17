# Advanced Atlas workflow reference

Most engineers can use Atlas through ordinary language: ask a question, teach it a fact, sync a repository or curate pending evidence. This page exposes the internal interfaces for maintainers, debugging and audit.

| Human intent | Internal workflow | Typical deterministic tools |
|---|---|---|
| Ask Atlas | `atlas-discover`, `atlas-impact` | `atlas_query.py find`, `resolve`, `context`, `neighbors`, `impact` |
| Teach Atlas | `atlas-stage`, `atlas-questions` | `atlas_query.py questions`, `staging`; `atlas_lint.py` |
| Sync Atlas | `atlas-onboard-repository`, `atlas-onboard-standards`, `atlas-stage-changes` | `atlas_source_snapshot.py`, `atlas_query.py context`, `atlas_intake.py` |
| Curate Atlas | `atlas-curate`; `atlas-review` for an audit/second opinion | Git commit ranges, `rebuild_atlas.py`, `atlas_lint.py`; `atlas_review_snapshot.py` only for an uncommitted audit |
| Improve Atlas prose | `atlas-humanize`; `atlas-lint` for correctness/contradictions | Atlas lint plus focused parser/freshness checks when relevant |

These names are useful for explicit invocation but are not a prerequisite for normal use. Claude chooses among them from the user's request and current context.

## Package identity, domains and federation

[`atlas-package.json`](../atlas-package.json) is the machine-only manifest. It declares package identity, ownership, aliases, controlled domains, entry points, map paths, taxonomy paths, and compiler-contract paths. Once a package is known, normal navigation opens its indexes, maps, stable IDs, or pages directly; the manifest is configuration, not a mandatory human navigation hop.

Register a domain before adding the first domain-routed repository, component, flow, infrastructure, or schema page:

```json
{
  "id": "orders",
  "title": "Orders",
  "aliases": ["order-processing"],
  "routing_description": "Order capture, validation and fulfilment architecture."
}
```

The page folder and `primary_domain` must match a registered domain. Domain registration is not required merely to begin using Atlas or to capture evidence that is not yet a curated architecture page. Domains and paths route records; stable IDs remain unchanged when those locators move.

A future Atlas-core registry needs only the package ID, aliases, authorised manifest location, and package status. The Datalens package aliases include `datalens`, `data-lens`, and `clearwater`.

## Navigation model

`find` performs deterministic candidate retrieval over curated frontmatter, embedded data assets, and promoted resources. It searches identifiers, titles, descriptions, aliases, optional keywords, types, domains, conflict text, and low-weight locators. It has no embeddings, vector store, or language model. Claude selects from the candidates using the question and evidence, or preserves ambiguity.

After a stable ID is selected, pages and their direct links remain the main semantic navigation surface. Maps are used for reverse or multi-hop traversal. Lifecycle determines semantic trust; Git reports a separate checkout advisory and does not downgrade a curated page. A `not-verified` path match stays available but must be disclosed as routing rather than identity proof.

When Claude or Codex runs inside the Atlas checkout, questions about stored engineering knowledge search curated records without treating the Atlas repository itself as product-path evidence. Questions about Atlas scripts, contracts, or workflow implementation use local source instead.

## Persisted writing

The shared `clear-writing.md` contract applies while Atlas skills and agents draft pages or durable reports. It requires plain technical language while preserving evidence, confidence, coverage, controlled terms, safety requirements, parser-owned headings, tables, links, and generated markers.

Use `atlas-humanize` for an approved, bounded prose cleanup. It separates style problems from semantic contradictions, refuses generated content and committed staging evidence, previews once, and verifies that no material claim changed or disappeared. Use `atlas-lint` for validation failures, broken links, contradictions, and evidence-sensitive repair routing.

## Source snapshots

Repository onboarding analyses one selected immutable source state:

```powershell
python scripts/atlas_source_snapshot.py prepare --repository <path>
python scripts/atlas_source_snapshot.py prepare --repository <path> --commit <revision> --default-ref origin/main --format json
python scripts/atlas_source_snapshot.py cleanup --manifest <temporary-manifest>
```

Without `--commit`, preparation accepts only the exact clean current `HEAD`. Dirty or historical/unmerged analysis uses an explicit revision and, when needed, a detached worktree below the operating-system temporary directory. Cleanup never switches, resets, stashes, cleans or force-removes the active checkout. A dirty temporary worktree is left in place and reported.

The snapshot manifest is ephemeral operational state. It is never Atlas evidence and never advances `_intake/`. For an unmerged branch snapshot, onboarding records the branch commit as the knowledge snapshot and the merge base with the default branch as the future intake anchor; it does not pretend the branch has merged.

## Power-user query routes

```powershell
python scripts/atlas_query.py resolve comp.example
python scripts/atlas_query.py find "component that enriches orders" --type component
python scripts/atlas_query.py find "order processing" --type component --type flow --path .
python scripts/atlas_query.py context .
python scripts/atlas_query.py route orders
python scripts/atlas_query.py questions repo.orders-platform
python scripts/atlas_query.py questions --path .
python scripts/atlas_query.py questions orders --scope domain
python scripts/atlas_query.py questions --scope package --format json
python scripts/atlas_query.py staging
python scripts/atlas_query.py staging --status deferred --target comp.example
python scripts/atlas_query.py staging --include-terminal --format json
python scripts/atlas_query.py neighbors comp.example
python scripts/atlas_query.py impact comp.example --direction downstream
python scripts/atlas_query.py --format json impact comp.example --max-depth 4
```

Query output and generated maps route to evidence but are not semantic authority. Candidate search is deterministic and preserves ambiguity.

## Optional idle reminder

```powershell
python <ATLAS_ROOT>/.claude/skills/atlas-questions/scripts/manage_idle_reminder.py install
python <ATLAS_ROOT>/.claude/skills/atlas-questions/scripts/manage_idle_reminder.py check
python <ATLAS_ROOT>/.claude/skills/atlas-questions/scripts/manage_idle_reminder.py remove
```

Use `--dry-run` before installation or removal. The hook is user-level, suggests a Teach Atlas session only when relevant questions exist, and never starts a conversation or writes Atlas. Reinstall it if the Atlas checkout moves.

## Evaluation and maintenance

```powershell
python scripts/atlas_lint.py .
python scripts/rebuild_atlas.py
python scripts/rebuild_atlas.py --check
```

## Feature branches, scoped curation and recovery

Before any repo-tracked write, reuse an existing non-default branch with shared default-branch history and state its name. Do not make a branch per write. On the default branch, detached HEAD or unrelated history, ask the user to confirm a suggested branch, select an existing branch or supply a custom name. Require actual content-clean diffs and no non-ignored untracked files. One persistence approval may include the exact local commits shown in its preview; it never includes push or merge.

Before authoring, read `atlas-package.json` and follow its registered paths: load `types` and `statuses` always, `concept_fields` when selecting controlled concept/asset/resource fields, `standard_categories` for standards, and `map_fields` before map-bound fields or relationships. Also read the destination README, template and index. Use this curation sequence:

1. Record starting `HEAD`, aggregate lint JSON and rebuild-check diagnostics as the baseline; preview exact paths, claims, lifecycle effects, generated effects, branch and commit boundaries.
2. After approval, mark only approved evidence `curating`, materialise the matrix, inspect the exact diff and create `atlas: curate checkpoint <scope>` before repair.
3. Run `python scripts/atlas_lint.py .` once across the package. Current, changed-shared, new or unexplained findings block; demonstrably unchanged unrelated baseline findings are advisory. Do not repair baseline issues or let them block staging/semantic curation.
4. Make no more than two aggregate passes of uniquely determined, meaning-preserving, in-scope mechanical repairs. Do not use regex or line deletion; do not empty/delete resources, relations or evidence; do not rename an ID/type, rewrite minimal frontmatter, or globally lower confidence. Bring semantic ambiguity to the user.
5. Verify exact paths, rebuild/check and create the validated commit. Independently review the immutable starting-to-proposal range with the same clean `HEAD` before/after; commit supported fixes and re-review the full range.
6. Consume successful evidence, update the compact checkpoint/generated effects and create the exact finalization commit. Semantic changes in finalization require full validation and review.

A current-cause problem or a lint/compiler mismatch leaves evidence `curating`. If freshness is blocked solely by an unrelated baseline issue, semantic curation may complete and consume with generated freshness explicitly deferred. This does not relax strict global lint or CI.

Completion reports separate **Current work**, **Scope validation**, **Generated freshness**, and **Package health**. A consumed staging record remains consumed. Restore only approved paths from the local checkpoint commit or a verified revision; never reset broadly or restore all `_curated/`.

Use `/atlas-evaluate prepare|run|score` only for a sealed end-to-end benchmark. Keep its fixture, personas, ground truth, frozen answers and results in the selected external sealed directory.
