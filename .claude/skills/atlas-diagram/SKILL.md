---
name: atlas-diagram
description: Use when an Atlas answer or page needs a clearer architecture or flow diagram, or when an existing Atlas Mermaid diagram must be reviewed without changing unsupported meaning.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

# atlas-diagram

Read `../_shared/diagram-writing.md`, `../_shared/answer-provenance.md`, `../_shared/persistence-approval.md`, and `../_shared/curation-safety.md` before persisted work.

1. Identify the single engineering question and output surface. For a console answer, prefer a plain-text route, tree, or table; use Mermaid only when requested or reliably rendered.
2. Classify the target as an answer-time view, generated flow diagram, or curator-authored component diagram. Read the owning page, its collection README/template, and the smallest evidence set supporting every node and edge.
3. Apply the shared size, evidence, accessibility, uncertainty, and fallback rules. If the view needs more than eight nodes, split it by a meaningful boundary. If it has fewer than three, use prose instead.
4. For generated flows, never hand-edit a generated Mermaid block. Report or apply changes only to evidenced structured steps or the `diagram` flag within the owning approved curation scope, then rebuild Atlas.
5. For a curator-authored component diagram, preserve facts, confidence, direction, and boundaries. A new or changed semantic connection requires staging/curation evidence; this skill cannot invent or self-approve it.
6. Check Mermaid syntax with an available renderer when practical and inspect readability separately. Do not install a renderer or browser dependency without approval.
7. For persisted changes, reuse the owning workflow's existing scope-bound approval. If no approved scope exists, show one preview and route the change through the appropriate authoring or curation workflow.

Report the question answered, evidence used, diagram or fallback chosen, syntax/readability checks, protected generated content, and unresolved gaps. Never treat visual adjacency as causality.
