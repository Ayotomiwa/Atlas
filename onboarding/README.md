# New developer onboarding

Atlas is TeamA's governed engineering context layer. It helps engineers and agents find source boundaries, architectural components, ordered flows, infrastructure, schemas, operations and standards without pretending that recorded context is complete.

## Trust first

- `_staging/` contains attributable raw evidence and is never authoritative.
- `_curated/` is reusable knowledge, but authority requires `status: curated` plus human-reviewed merge.
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

Ask natural engineering questions. `atlas-discover` treats Atlas as a smart cache: it derives candidate context from the current path, routes by stable IDs internally, and continues with bounded source inspection when coverage ends. Use `atlas-impact` for explicit change-risk or failure questions.

Substantive answers cite the curated page or repository source for each material claim and disclose every answer-bearing map/source hop. Scripts are traversal tools, not factual sources.

## Contribute evidence

Use `atlas-stage` to capture one explicitly requested reusable fact. Use `atlas-onboard-repository` for one logical source-boundary investigation and `atlas-onboard-standards` for explicit standards discovery. Onboarding creates staging evidence, not curated knowledge.

`atlas-curate` reconciles eligible evidence into a proposal and invokes independent review. A human reviews and merges the change. `atlas-review` can inspect evidence, pages, diffs or commit ranges without editing.

## Generated artifacts

Edit only curated Markdown structured fields and narrative. Never hand-edit JSON maps, generated catalogues, managed routing tables or generated flow diagrams. Rebuild them together with:

```powershell
python scripts/rebuild_atlas.py
```

## First contribution route

1. Start from [`../index.md`](../index.md) and the relevant collection README.
2. Load Claude with `--add-dir` and ask a natural discovery question from the product path.
3. Confirm whether the answer is reviewed Atlas, local/unmerged Atlas, repository-derived, inferred or unknown.
4. Explicitly request staging if the new fact is reusable.
5. Review the staged source references and coverage limits.
6. Curate only through a human-reviewable proposal; never self-approve.

Workflow procedures, clarification checklists and managed-block assets live with their skills. Collection READMEs own semantic policy and templates own capture shape.
