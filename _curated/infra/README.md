# Curated infrastructure

Infrastructure pages model a meaningful IaC/package boundary and selectively promote resources that need independent routing or impact identity.

## Domain and source routing

Store pages at `_curated/infra/<primary-domain>/<record>.md`. When source-controlled, `repository` uses a stable `repo.*` ID and `package_path` locates the package inside it. Paths and repository URLs never form Atlas identity.

## Package actions

Author infrastructure facts through explicit fields: `depends_on`, `uses_resources`, `reads_from`, `writes_to`, `triggers`, `scheduled_by`, `imports_values`, `exports_values`, `permissions`, `monitored_by` and `deployed_by`. Each entry uses `id` for a stable Atlas target or `name` for an external target, plus confidence and evidence/note. The field itself explains the connection.

## Resource promotion

Ordinary resources remain in page prose. Promote only a resource that materially improves routing, impact analysis, permissions/trigger understanding or operational navigation. Each embedded record requires a stable `resource.*` ID, resource type, definition path, environments, promotion reason, confidence, coverage and evidence. Resource-local actions use the same named fields as the package.

The compiler emits one typed `used_by` collection with `via` provenance instead of separate reverse arrays for each source type or action. Package `resources` is a compact derived ID list. All other reverse and transitive views are computed by `atlas_query.py`.

Keep narrative environment differences, monitoring detail and impact reasoning on the page. Run `python scripts/rebuild_atlas.py` after structured changes; never hand-edit map JSON or managed tables.
