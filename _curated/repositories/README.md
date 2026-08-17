# Curated repositories

Use a repository page to answer: **where does this source boundary begin and end, how is it organised, who owns it, and where should an engineer start reading?**

A repository page describes source organisation, not runtime behavior. For example, a logical project inside a monorepo may qualify when it has its own build, release, ownership, or product boundary. Its deployable worker still belongs on a component page, and the end-to-end execution path belongs on a flow page.

## Granularity

Create a `repo.*` page for an independently organised source boundary: a standalone Git repository, a useful physical monorepo root, an evidenced logical project root inside a monorepo, a genuinely nested project, or an explicitly classified mirror/alternative. A folder qualifies only when ownership, build/dependency, release/deployment, source/config/test, documentation, or child-product evidence makes the boundary useful.

A monorepo-root page is optional: create it only when the root carries useful evidenced context. Use `parent_repository` for a real enclosing source boundary, not ordinary folder containment. Infrastructure-only folders normally produce `infra.*` pages rather than duplicate repository pages.

Repository IDs are stable semantic identifiers. `repository_locator`, `repository_root`, checkout names, domains and paths are mutable routing values and never form identity. `repository_root` is `.` for a physical Git root or a relative POSIX-style path from that root for a logical/nested boundary.

## Domain placement

Store pages at `_curated/repositories/<primary-domain>/<record>.md`. `primary_domain` must be declared in `atlas-package.json` and match the folder. Use `related_domains` for secondary involvement; ask the user if a primary domain cannot be evidenced.

## Structured source facts

- `source_roots` records important paths, purposes and evidence, not every directory.
- `depends_on_repositories` records real repository-level source/build connections such as submodules, generated source or shared tooling. Each entry uses the repository-specific `dependency_type` qualifier.
- Component membership and cross-repository runtime dependencies are derived from component pages and must not be authored reciprocally.
- Use `runbooks`, `standards` and `incident_learnings` for governed context.

Connection entries use `id` for stable Atlas targets or `name` for external targets. The containing field supplies the meaning, so entries never repeat a generic relationship. The map derives only compact component IDs and one typed `used_by` list; other reverse and cross-repository views are query-time results.

The repository page should include an informative code-architecture summary: significant entrypoints, control flow and source-root responsibilities, without duplicating functions or exact operational commands. Component `repository_paths` are relative to the component's most-specific referenced repository boundary.

## Review

Before approving a repository page, confirm that:

- the boundary is independently useful, and the evidence names which signal makes it so;
- `repository_type` matches that evidence rather than the folder's appearance;
- the physical Git locator, `repository_root` and `parent_repository` describe real containment, not ordinary nesting;
- `primary_domain` is evidenced and registered, and `related_domains` records genuine secondary involvement;
- `source_roots` covers the roots that matter and omits directory noise;
- the component split is architectural — folders and job groups have not become components;
- `depends_on_repositories` records source/build connections only, with runtime dependencies left to component pages;
- unknown ownership, deployment and source areas are stated as open questions rather than omitted.

Generated tables and maps are compiled with `python scripts/rebuild_atlas.py` and are never hand-edited.

This README defines the repository page model and review rules. Repository onboarding and curation workflows own source scanning, approvals, staging, validation, and independent review.
