# New developer onboarding

Atlas is Datalens's governed engineering context layer. It helps engineers and agents find source boundaries, architectural components, ordered flows, infrastructure, schemas, operations and standards without pretending that recorded context is complete.

## Trust first

- `_staging/` contains attributable raw evidence and is never authoritative.
- `_curated/` is active authoritative or historical reusable knowledge. Query reports lifecycle trust separately from a compact checkout-state advisory; merge is distribution/audit, not an authority transition.
- Generated maps and query output route between facts; curated pages and source evidence explain them.
- Missing coverage remains unknown.

## Learn the record boundaries

| Record | Responsibility |
|---|---|
| `repo.*` | Physical or logical source organisation, ownership and build/release topology |
| `comp.*` | Independently addressable runtime or reusable behavior |
| `flow.*` | Ordered execution, participants, handoffs and material boundary I/O |
| `infra.*` / `resource.*` | Infrastructure packages, promoted resources and natural actions |
| `schema.*` | Physical API/event/data contracts and compatibility |

A domain or path groups records but never establishes identity. A logical project inside a monorepo may be a repository when evidence shows a meaningful boundary.

## Load and use Atlas with Claude

Load the live checkout so Claude uses the canonical skills and agents:

```powershell
claude --add-dir <ATLAS_ROOT>
```

Ask natural engineering questions. `atlas-discover` resolves explicit IDs directly and otherwise uses deterministic type-directed candidate search. It opens the selected page, follows page links and uses maps only for reverse or multi-hop traversal. Relevant collection/domain indexes are the fallback for weak, ambiguous or browsing-oriented searches. Use `atlas-impact` for explicit change-risk or failure questions.

The product repository's Atlas-managed `CLAUDE.md` block is the bootstrap signal even when a skill does not trigger. If Atlas cannot be resolved, Claude says it was not consulted and asks the user to restart with `claude --add-dir <path-to-current-Atlas-checkout>`; it may continue with bounded repository evidence. `not-verified` repository context remains usable but is disclosed in every answer that relies on it.

When a relevant product boundary lacks the managed block, discovery may offer setup once without writing. After approval, `atlas-setup-repo` merges the block into an existing `CLAUDE.md` or creates a minimal file only for a Git/curated boundary with a README. It never edits sibling products or stores absolute checkout paths.

Substantive answers cite the curated page or repository source for each material claim and disclose every answer-bearing map/source hop. Scripts are traversal tools, not factual sources.

## Answer open Atlas questions

Use `/atlas-questions` to answer one useful curated question at a time. With no argument it starts from the current product path; pass a stable ID, domain or topic to narrow the session:

```text
/atlas-questions
/atlas-questions repo.orders-platform
/atlas-questions orders
/atlas-questions ownership
```

The skill cites the existing knowledge and evidence gap, accepts `skip`, `unsure`, `change topic` and `stop`, and treats answers as user-confirmed evidence. It may preview a coherent staging record, but it writes nothing until the user explicitly approves and the `atlas-stage` workflow takes over. A staged answer does not resolve or remove the curated question; normal curation and independent review remain required.

Claude can optionally show a quiet reminder when it becomes idle and the current path has eligible questions. This is user-level opt-in because `--add-dir` loads Atlas skills but not hooks:

```powershell
python <ATLAS_ROOT>/.claude/skills/atlas-questions/scripts/manage_idle_reminder.py install
python <ATLAS_ROOT>/.claude/skills/atlas-questions/scripts/manage_idle_reminder.py check
python <ATLAS_ROOT>/.claude/skills/atlas-questions/scripts/manage_idle_reminder.py remove
```

The reminder only suggests `/atlas-questions`; it never starts a conversation or changes Atlas. Re-run `install` if the Atlas checkout moves. Use `--dry-run` with install or remove to inspect the intended action.

## Contribute evidence

Use `atlas-stage` to capture one explicitly requested reusable fact. Use `atlas-onboard-repository` for one logical source-boundary investigation and `atlas-onboard-standards` for explicit standards discovery. Onboarding creates staging evidence, not curated knowledge.

## Reproducible evaluation

Use `/atlas-evaluate prepare|run|score` only for a sealed end-to-end benchmark. It keeps fixture source, personas, ground truth, frozen answers, baselines and results in an explicit external directory while Datalens Atlas retains only reusable tooling. The control arm has no Atlas or managed product instructions, both arms include impact questions, and only the independent judge opens ground truth after answer freeze. Missing telemetry is recorded as unavailable rather than estimated.

`atlas-curate` reconciles eligible evidence into authoritative curated knowledge and invokes independent review. A later human review/merge may publish and audit the change without altering its lifecycle authority. `atlas-review` can inspect evidence, pages, diffs or commit ranges without editing.

Use `atlas-lint` for deterministic frontmatter/relative-link validation and requested safe repairs. It may delegate read-only semantic inspection for contradictions, garbled prose, sensitive-content risk or missing-link candidates, but evidence-sensitive knowledge changes still use staging and curation.

## Generated artifacts

Edit only curated Markdown structured fields and narrative. Never hand-edit JSON maps, generated catalogues, managed routing tables or generated flow diagrams. Rebuild them together with:

```powershell
python scripts/rebuild_atlas.py
```

## First contribution route

1. Start from [`../index.md`](../index.md) and the relevant collection README.
2. Load Claude with `--add-dir` and ask a natural discovery question or run `/atlas-questions` from the product path.
3. Confirm whether the answer is authoritative curated Atlas, historical Atlas, repository-derived, user-confirmed, inferred or unknown; note checkout state once when it is not clean on `main`/`master`.
4. Approve a staging preview only when the new fact is reusable and correctly bounded.
5. Review the staged source references and coverage limits.
6. Curate through evidence reconciliation and independent review; later merge/publication does not require a lifecycle update.

Workflow procedures, clarification checklists and managed-block assets live with their skills. Collection READMEs own semantic policy and templates own capture shape.
