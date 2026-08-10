# Curated repositories

Repository pages describe useful source boundaries and topology. They answer where code lives, how a source boundary is organised, which domain owns it, and which independently addressable components it contains. Runtime responsibility belongs on component pages; end-to-end execution belongs on flow pages.

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

Confirm the boundary evidence, repository type, physical Git locator, logical root, enclosing repository, domain, important roots and component split. Keep unknown ownership, deployment and source areas explicit. Generated tables and maps are compiled with `python scripts/rebuild_atlas.py` and are never hand-edited.
