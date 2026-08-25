---
name: atlas-humanize
description: Use when an Atlas README, template, staging draft, curated-page draft, or other persisted Atlas prose is generic, vague, jargon-heavy, repetitive, awkward, garbled, or difficult for engineers to understand without changing its technical meaning.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Agent
---

# atlas-humanize

Read `../_shared/clear-writing.md`, `../_shared/persistence-approval.md`, `../_shared/runtime.md`, and `references/atlas-prose.md`. This workflow improves persisted Atlas prose; it does not humanize ordinary chat answers.

1. Resolve the requested path or diff and read its governing README/template plus the smallest relevant semantic contracts. Identify generated blocks, parser-owned headings, structured tables, links, commands, controlled terms, and material claims before proposing edits.
2. Run the shared page-specificity scan across the requested prose. For each generic or vague sentence, identify the exact sentence and propose either an evidence-supported replacement or deletion. If a specific replacement needs a new fact, report the knowledge gap instead of inventing detail. Separate other writing problems from semantic problems. Awkward, dense, repetitive, or garbled prose may be rewritten without changing meaning. Contradictions, unsupported claims, missing evidence, relationship changes, and unclear policy are semantic findings: report them separately and use `atlas-lint-analyst` when a bounded read-only investigation is useful.
3. Refuse direct edits to generated content and committed staging evidence. For a governed draft already owned by staging or curation, return the wording proposal to that workflow unless the user explicitly requested this standalone edit.
4. Show one persistence preview: the readability problem, proposed files and changes, protected content, semantic findings excluded from the edit, validation, branch, and commit boundary. Obtain explicit scope-bound approval before writing.
5. Apply only approved, meaning-preserving prose edits. Do not change frontmatter, facts, certainty, scope, evidence, links, IDs, commands, tables, headings used by parsers, or generated markers merely to improve style.
6. Review the diff claim by claim. Confirm that no material claim disappeared, no new claim appeared, and every unknown, conflict, safety condition, and requirement kept its force. Run Atlas lint and any focused parser/freshness check required by the changed surfaces.
7. Create the approved exact-path local commit on the selected feature branch. Report changed wording, protected content, unresolved semantic findings, validation, branch, and commit. Never push, merge, approve, or publish.
