# Curated repositories

Repository pages describe source boundaries and topology. They answer where code lives, how a repository is organised, which domain owns it, and which independently addressable components it contains. Runtime responsibility belongs on component pages; end-to-end execution belongs on flow pages.

## Granularity

Create one `repo.*` page per actual source repository. Use `parent_repository` only for a real nested repository or submodule, never for an ordinary folder. A monorepo remains one repository page and contains multiple component pages.

Repository IDs are stable semantic identifiers. `repository_locator`, checkout names, domains and paths are mutable routing values and never form identity.

## Domain placement

Store pages at `_curated/repositories/<primary-domain>/<record>.md`. `primary_domain` must be declared in `atlas-package.json` and match the folder. Use `related_domains` for secondary involvement; ask the user if a primary domain cannot be evidenced.

## Structured source facts

- `source_roots` records important paths, purposes and evidence, not every directory.
- `depends_on_repositories` records real repository-level source/build connections such as submodules, generated source or shared tooling. Each entry uses the repository-specific `dependency_type` qualifier.
- Component membership and cross-repository runtime dependencies are derived from component pages and must not be authored reciprocally.
- Use `runbooks`, `standards` and `incident_learnings` for governed context.

Connection entries use `id` for stable Atlas targets or `name` for external targets. The containing field supplies the meaning, so entries never repeat a generic relationship. The map derives only compact component IDs and one typed `used_by` list; other reverse and cross-repository views are query-time results.

The repository page should include an informative code-architecture summary: significant entrypoints, control flow and source-root responsibilities, without duplicating functions or exact operational commands.

## Review

Confirm the repository boundary, domain, mutable locator, important roots and component split. Keep unknown ownership, deployment and source areas explicit. Generated tables and maps are compiled with `python scripts/rebuild_atlas.py` and are never hand-edited.
