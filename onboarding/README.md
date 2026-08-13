# New developer onboarding

Atlas is Datalens's governed engineering context layer. It helps engineers and agents find source boundaries, architectural components, ordered flows, infrastructure, schemas, operations and standards without pretending that recorded context is complete.

## Trust first

- `_staging/` contains attributable raw evidence and is never authoritative.
- `_curated/` is active authoritative or historical reusable knowledge. Query reports lifecycle trust separately from a compact checkout-state advisory; merge is distribution/audit, not an authority transition.
- Generated maps and query output route between facts; curated pages and source evidence explain them.
- Missing coverage remains unknown.

## Four everyday actions

| Action | Natural request | What Claude handles |
|---|---|---|
| Ask Atlas | “How does this work?” “What could this change affect?” | context selection, linked navigation, impact analysis and bounded source fallback |
| Teach Atlas | “Save this fact.” “What does Atlas need to know?” | provenance, duplicates, questions, bucket selection and an approved evidence write |
| Sync Atlas | “Onboard this repository.” “Update Atlas for this repo.” | full baseline discovery, standards comparison or merged-change intake |
| Curate Atlas | “Curate pending evidence for this domain.” | scoped reconciliation, generation and independent review |

You do not need to choose a skill, staging bucket or query command. Claude states its interpretation before an ambiguous write, shows one concrete persistence preview and asks once for that unchanged scope. The [advanced reference](advanced-reference.md) lists exact interfaces for maintainers.

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

Ask natural engineering questions. Claude resolves explicit IDs directly and otherwise uses deterministic type-directed candidate search. It opens the selected page, follows page links and uses maps only for reverse or multi-hop traversal. Relevant collection/domain indexes remain the fallback for weak, ambiguous or browsing-oriented searches. Change-risk and failure wording automatically selects deeper impact analysis.

The product repository's Atlas-managed `CLAUDE.md` block is the bootstrap signal even when a skill does not trigger. If Atlas cannot be resolved, Claude says it was not consulted and asks the user to restart with `claude --add-dir <path-to-current-Atlas-checkout>`; it may continue with bounded repository evidence. `not-verified` repository context remains usable but is disclosed in every answer that relies on it.

When a relevant product boundary lacks the managed block, discovery may offer setup once without writing. After approval, `atlas-setup-repo` merges the block into an existing `CLAUDE.md` or creates a minimal file only for a Git/curated boundary with a README. It never edits sibling products or stores absolute checkout paths.

Substantive answers cite the curated page or repository source for each material claim and disclose every answer-bearing map/source hop. Scripts are traversal tools, not factual sources.

## Teach Atlas

Say “What does Atlas still need to know about this repo?” to answer one useful curated question at a time. Name a repository, stable ID, domain or topic in the same request when you want a narrower session.

Claude cites the existing knowledge and evidence gap, accepts `skip`, `unsure`, `change topic` and `stop`, and treats answers as user-confirmed evidence. It previews the exact evidence to save and asks once. The internal staging handoff does not ask for the same approval again. A staged answer does not resolve the curated question; curation and independent review remain required.

Claude can optionally show a quiet reminder when it becomes idle and the current path has eligible questions. This is user-level opt-in because `--add-dir` loads Atlas skills but not hooks. The reminder only offers a Teach Atlas session; it never starts one or changes Atlas. Installation, checking and removal are documented in the [advanced reference](advanced-reference.md#optional-idle-reminder).

## Sync repositories and contribute evidence

Say “Save this to Atlas” for one reusable fact. Say “Onboard this repository” for initial coverage, “Update Atlas for this repository” for ongoing maintenance, or “Learn the standards used by these repositories” for standards comparison. Claude chooses the specialist internally. All routes create evidence, not curated knowledge.

Initial repository sync is a full baseline, not a lean placeholder. It assesses repository identity/ownership/domain, build/test/release, source roots, every real component and its causal behavior, flows, infrastructure, schemas and operations. A lens may honestly be unknown, inaccessible or not applicable; unsupported records are not created to fill it.

Onboarding analyses one immutable source snapshot. A clean current `HEAD` can be read in place. Dirty, historical or explicitly selected branch state requires an exact commit and may use a detached temporary worktree without altering the developer's checkout. Staging records the selected/default commits and merge base; an unmerged branch remains explicitly unmerged. Onboarding records a future intake anchor but does not write the shared checkpoint.

For a known baseline, “Update Atlas for this repository” assesses merged default-branch changes since the shared cursor. It fetches the source, accounts for every logical change, and previews evidence plus checkpoint effects together. The initial cursor must come from an explicit base, locally provable merged-MR commit or the exact future-intake anchor in approved onboarding evidence; it is never guessed. The workflow never depends on a hosting API.

`_intake/` is mutable operational state, separate from immutable-by-policy `_staging/` evidence. Its checkpoint distinguishes the latest commit observed from the latest contiguous commit considered. Deferred changes remain explicitly unresolved; an unreadable, ambiguous or unassessed change prevents cursor advancement. Git history recovers checkpoint edits, while structured `change_source` on merged-change staging records prevents a failed checkpoint update from producing duplicate evidence on the next run.

Claude can show one read-only queue across every staging bucket, scoped to active or historical records, bucket, candidate domain, date or suggested target. The result reports matches, not semantic duplicates or curation decisions.

## Reproducible evaluation

The sealed evaluation workflow keeps fixture source, personas, ground truth, frozen answers, baselines and results in an explicit external directory while Datalens Atlas retains only reusable tooling. The control arm has no Atlas or managed product instructions, both arms include impact questions, and only the independent judge opens ground truth after answer freeze. Exact evaluation interfaces are in the [advanced reference](advanced-reference.md#evaluation-and-maintenance).

## Curate Atlas

Say “Curate pending evidence for this repository/domain/topic.” Claude defaults to that context rather than exposing the whole package queue, shows proposed knowledge changes and material decisions, and asks once before writing. It then materialises supported knowledge, regenerates routing views and invokes an independent reviewer. A separate review invocation is mainly for audits, external diffs or second opinions. Later human review/merge publishes and audits the change without altering lifecycle authority.

Curation normally reads the staging record and its exact cited product evidence; it may browse Atlas broadly for existing targets and links. It does not silently repeat broad source discovery. A materially new fact returns through staging and a revised preview.

Ask Claude to lint Atlas for deterministic frontmatter/relative-link validation and requested safe repairs. It may delegate read-only semantic inspection for contradictions, garbled prose, sensitive-content risk or missing-link candidates, but evidence-sensitive knowledge changes still use staging and curation.

## Generated artifacts

Edit only curated Markdown structured fields and narrative. Never hand-edit JSON maps, generated catalogues, managed routing tables or generated flow diagrams. Atlas rebuilds them together during curation; exact maintenance commands are in the [advanced reference](advanced-reference.md#evaluation-and-maintenance).

## First contribution route

1. Load Claude with `--add-dir` and ask an ordinary engineering question.
2. Use Ask, Teach, Sync or Curate wording; Claude chooses the internal route.
3. Confirm whether the answer is authoritative curated Atlas, historical Atlas, repository-derived, user-confirmed, inferred or unknown; note checkout state once when it is not clean on `main`/`master`.
4. Approve a staging preview only when the new fact is reusable and correctly bounded.
5. Review the staged source references and coverage limits.
6. Ask to update the repository after default-branch changes and approve the combined evidence/checkpoint preview.
7. Ask to curate the relevant repository/domain/topic; independent review runs inside that workflow.

Workflow procedures, clarification checklists and managed-block assets live with their skills. Collection READMEs own semantic policy and templates own capture shape.
