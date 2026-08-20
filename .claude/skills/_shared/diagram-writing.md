# Diagrams for Atlas pages and answers

Use a diagram only when it answers one engineering question more clearly than a short paragraph, plain-text route, tree, or compact table. A diagram is a projection of evidenced facts, never a new source of architectural meaning.

## Choose the smallest useful view

- Skip a diagram with fewer than three meaningful nodes; prose or a route is clearer.
- Prefer one view with three to eight nodes. Split a larger view by boundary or question rather than shrinking labels or showing every internal detail.
- Show architectural participants, material handoffs, and evidenced decisions. Do not turn source files or nearby functions into nodes unless the question is specifically about source structure.
- Use short labels that say what happens. Put explanation, evidence, and open questions in the surrounding page or answer.

## Preserve semantics

- Draw only facts already supported by the owning curated page or cited repository evidence.
- Preserve order, direction, conditions, confidence, external boundaries, and unresolved participants. Never infer a connection to make the layout look complete.
- Use labels, shapes, and line styles together. Never use color alone to communicate participant type, failure, or uncertainty.
- Label material success, conditional, failure, and retry paths. Leave a path absent when it is not known.
- Keep a table or prose fallback beside persisted Mermaid so the content remains usable in terminals, plain Markdown, and accessibility tools.

## Match the output surface

For a console or plain-text answer, default to a compact route such as `API -> queue -> worker`, a small tree, or a compact table. Do not print raw Mermaid unless the user explicitly asks for Mermaid or the active client is known to render it well.

For persisted Markdown, use stable Mermaid flowchart syntax. Include `accTitle` and `accDescr`, escape label text, avoid beta diagram types, and avoid decorative themes. Validate syntax with an available renderer when practical, then inspect readability separately; a syntactically valid diagram can still be confusing.

Never hand-edit a generated Mermaid block. Change the structured flow steps or `diagram` flag through the owning curation workflow and run `python scripts/rebuild_atlas.py`. A curator-authored component diagram may be edited only inside its approved authoring or curation scope.
