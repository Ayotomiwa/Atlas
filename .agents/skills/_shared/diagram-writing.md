# Diagrams for Atlas pages and answers

Use a diagram only when it answers one engineering question more clearly than a short paragraph, plain-text route, tree, or compact table. A diagram projects evidenced facts; it does not create architectural meaning.

- Skip diagrams with fewer than three meaningful nodes. Prefer three to eight nodes and split a larger view by boundary or question.
- Show architectural participants, material handoffs, and evidenced decisions. Avoid file/function nodes unless source structure is the question.
- Preserve direction, order, conditions, confidence, external boundaries, and unresolved participants. Never invent a connection for visual completeness.
- Use labels, shapes, and line styles together; never use color alone. Label material success, conditional, failure, and retry paths.
- Keep a table or prose fallback with persisted Mermaid.

For a console or plain-text answer, default to a compact `A -> B` route, small tree, or compact table. Do not print raw Mermaid unless the user asks for it or the client is known to render it well.

Persisted Mermaid uses stable flowchart syntax, `accTitle`, `accDescr`, escaped labels, and no beta diagram types or decorative themes. Check syntax and readability separately when a renderer is available.

Never hand-edit a generated Mermaid block. Change structured flow steps or the `diagram` flag through the owning curation workflow, then rebuild Atlas. A curator-authored component diagram may change only inside its approved authoring or curation scope.
