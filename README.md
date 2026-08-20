# Datalens Atlas

Datalens Atlas gives engineers and AI agents a shared, traceable view of how Datalens systems are organised and connected. It helps answer questions about source boundaries, runtime components, flows, infrastructure, data contracts, operations, ownership, and standards without treating missing information as fact.

You can use Atlas through ordinary conversation. You do not need to learn its commands before asking a question.

Atlas is most useful for cold starts, cross-repository or cross-system questions, and context that must survive beyond one conversation. It is not expected to beat source code that Claude has already read for a narrow local follow-up. In that case Claude reuses the retained evidence or reads the exact source boundary directly; Atlas remains available when the question crosses a durable or uncertain boundary.

## What do you want to do?

| Intent | Example request | What happens |
|---|---|---|
| Ask Atlas | "How does this publish data?" or "What could this change affect?" | Claude finds the relevant reviewed knowledge, follows its links, and checks source files when coverage ends. |
| Teach Atlas | "Save this fact" or "What does Atlas still need to know?" | Claude checks provenance and duplicates, previews the evidence it could save, and writes only after approval. |
| Sync Atlas | "Onboard this repository", "Onboard this infrastructure portfolio", or "Update Atlas for this repo" | Claude builds a baseline, coordinates confirmed infrastructure boundaries, or examines merged changes since the last shared checkpoint. |
| Curate Atlas | "Curate pending evidence for payments" | Claude proposes reviewed knowledge changes, validates them, and sends them through independent semantic review. |

The workflow remains controlled behind the conversation: saved observations are not automatically trusted, uncertainty stays visible, writes require approval, and agents never merge or publish Atlas changes.

In a terminal, Atlas answers use concise prose, a plain-text route, a small tree, or a compact table. Mermaid source is shown only when you ask for it or the client can render it clearly.

## Find existing knowledge

- How is source code organised? Start with [repositories](_curated/repositories/index.md).
- What does a runtime or reusable unit do? Start with [components](_curated/components/index.md).
- What happens from start to finish? Start with [flows](_curated/flows/index.md).
- What infrastructure is used or affected? Start with [infrastructure](_curated/infra/index.md).
- What data or interface contract applies? Start with [schema information](_curated/schema-info/index.md).
- What evidence is waiting for review? Start with the [staging index](_staging/index.md).
- Not sure where to look? Ask Claude in natural language. It searches likely records first and uses these indexes when the match is weak or ambiguous.

Known-package navigation can open an index, map, stable ID, or page directly. It does not need to pass through the package manifest first.

## How to read Atlas

- Reviewed reusable knowledge lives in `_curated/`. A page with `status: curated` is authoritative Atlas knowledge.
- New observations live in `_staging/`. They are attributable evidence, not authority.
- Source-processing progress lives in `_intake/`. It records merged-change checkpoints and infrastructure portfolio queues; it is not engineering evidence.
- Generated maps and indexes help navigation. The curated page and cited source explain the fact.
- Git branch state is shown as a small checkout advisory. Being off `main` or `master` does not make a curated page non-authoritative, but it may mean the latest local change has not been shared yet.
- Missing coverage remains unknown. An absent link never proves that no dependency or impact exists.

Agents may stage and curate through the required evidence and independent-review workflows. They never merge or publish knowledge.

## Architecture boundaries

| Page type | Question it answers |
|---|---|
| Repository (`repo.*`) | How is this useful source boundary organised, owned, built, and released? |
| Component (`comp.*`) | What does this independently addressable runtime or reusable unit do, use, and produce? |
| Flow (`flow.*`) | Which ordered steps produce the outcome, including conditions and material handoffs? |
| Infrastructure (`infra.*`, `resource.*`) | What package or promoted resource exists, who uses it, and why does it matter operationally? |
| Schema (`schema.*`, `asset.*`) | What physical interface or data contract exists, and how is it related to other assets? |

A repository, folder, domain, or job group is not automatically a component. Stable IDs describe enduring concepts and must not encode repository paths; paths and domain folders may change without changing identity.

Architecture pages are grouped by one registered primary domain. Registering a domain is required before adding the first repository, component, flow, infrastructure, or schema page for that domain. It is not required merely to start using Atlas or to capture other evidence.

## Start using Atlas

For a first walkthrough, see [new developer onboarding](onboarding/README.md).

Claude loads the canonical Atlas workflows from this checkout:

```powershell
claude --add-dir <ATLAS_ROOT>
```

Codex adaptations live in `.agents/skills/` and `.codex/agents/`. Product repositories can contain a small managed `CLAUDE.md` or `AGENTS.md` block so the assistant knows when Atlas may help.

## Repository layout

| Path | Responsibility |
|---|---|
| `atlas-package.json` | Machine-readable package identity, domains, entry points, taxonomy, and compiler contracts |
| `index.md` | Root navigation for humans and agents |
| `_staging/` | Immutable-by-policy evidence waiting for curation |
| `_intake/` | Mutable, non-authoritative merged-change checkpoints and infrastructure onboarding campaigns |
| `_curated/` | Reviewed knowledge, collection policies, templates, and generated routes |
| `taxonomy/` | Controlled author-facing classifications and allowed values |
| `contracts/` | Compiler-only field and traversal rules |
| `.claude/` | Canonical Claude workflows and specialist roles |
| `.agents/`, `.codex/` | Codex workflow adaptations |
| `scripts/` | Deterministic search, validation, generation, intake, and evaluation tools used by workflows |

Do not hand-edit generated maps, catalogues, managed tables, or generated diagrams. Exact commands, lifecycle details, package federation, navigation mechanics, curation recovery, and evaluation procedures are in the [advanced reference](onboarding/advanced-reference.md).
