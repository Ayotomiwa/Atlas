# Clear writing for persisted Atlas prose

Apply this contract while drafting or revising Atlas prose that will be saved. It does not change the evidence, trust, review, or publication rules of the owning workflow.

## Write for the engineer's question

- Start with what the page helps an engineer understand or do.
- Explain the plain meaning before introducing an Atlas term.
- Give each paragraph one job. Prefer short paragraphs and useful lists over dense walls of text.
- Name the actor, action, and result. State causal links only when the evidence supports them.
- Use one exact term for each Atlas concept. Do not rotate through synonyms for variety.
- Put rules beside the action they govern. Move implementation detail to an advanced section when it is not needed for the first decision.

For architecture pages:

- Repository prose explains source organisation, ownership, boundaries, and where to begin reading.
- Component prose explains an independently addressable runtime or reusable unit: what it does, what it uses, and what it produces.
- Flow prose explains the ordered path, including conditions and handoffs; a step may be a component, infrastructure item, external system, manual action, or unresolved participant.
- Infrastructure prose explains the package or resource, why it matters, how it is used, and its operational boundary.

## Preserve meaning and interfaces

Never change wording at the cost of precision. Preserve:

- frontmatter, YAML keys and controlled values;
- stable IDs, lifecycle, confidence, coverage, evidence, and source references;
- technical names, commands, code, link targets, paths, and generated markers;
- structured table columns and parser-owned headings;
- `must`, `never`, `only`, safety limits, unknowns, conflicts, and explicit exclusions;
- every material claim and the distinction between direct evidence and inference.

Do not edit generated content by hand. Do not rewrite committed staging evidence. A factual correction, new connection, changed scope, or softened requirement belongs in the relevant evidence/curation workflow, not in a prose cleanup.

## Drafting check

Before returning persisted prose, verify:

1. The opening tells the reader why the page exists.
2. An engineer can understand the first screen without prior Atlas vocabulary.
3. Every material claim still has the same meaning and support.
4. No new fact, certainty, relationship, or requirement was introduced.
5. Protected structures and link targets are unchanged unless the owning workflow explicitly approved them.
6. Remaining unknowns and contradictions are still visible.
