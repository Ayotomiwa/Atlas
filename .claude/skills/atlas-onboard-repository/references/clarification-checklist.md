# Repository onboarding clarification checklist

Ask one consolidated round containing only material unresolved items:

- Which logical source boundary is being onboarded, and what physical Git root contains it?
- Which exact commit represents the knowledge snapshot when the checkout is dirty, historical or otherwise ambiguous? Confirm intentional use of an unmerged branch when applicable.
- What evidence makes this a standalone, monorepo-root, monorepo-project, nested-project, mirror or other useful boundary?
- What is its Git-relative `repository_root`, enclosing repository candidate, and explicit included/excluded path scope?
- Which primary domain owns the repository and each component candidate? Ask rather than infer when several are plausible.
- Which candidates are independently addressable runtime/reusable components rather than folders, modules, products or job groups?
- Where are authoritative infrastructure, shared-code or operational definitions when referenced outside the boundary?
- Which upstream/downstream systems and end-to-end flow boundaries are known but not provable from accessible source?
- Who is the evidenced operational/product owner, who is only a review or approval route, and who is a subject-matter expert? CODEOWNERS alone proves only review routing.
- Which explicitly referenced documents/repositories are inaccessible but necessary?

Ask a second targeted question only when safe staging is blocked. Present other lens gaps together as optional confirm-or-correct items; leave skipped gaps unknown or partial.
