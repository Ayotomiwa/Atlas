# Curated infrastructure

Infrastructure pages model a meaningful IaC/package boundary and selectively promote resources that need independent routing or impact identity.

## Domain and source routing

Store pages at `_curated/infra/<primary-domain>/<record>.md`. When source-controlled, `repository` uses a stable `repo.*` ID and `package_path` locates the package inside it. Paths and repository URLs never form Atlas identity.

## Package actions

Author infrastructure facts through explicit fields: `depends_on`, `uses_resources`, `reads_from`, `writes_to`, `triggers`, `scheduled_by`, `imports_values`, `exports_values`, `permissions`, `monitored_by` and `deployed_by`. Each entry uses `id` for a stable Atlas target or `name` for an external target, plus confidence and evidence/note. The field itself explains the connection.

## Resource promotion

Promotion is the decision that admits a resource to the authoritative routing graph, so it is made here rather than in staging. Ordinary resources stay in page prose and receive no stable identity.

Promote a resource only when at least one of these is evidenced:

- shared by multiple components, flows or packages;
- independently operated, deployed or monitored;
- incident-relevant;
- security- or permission-sensitive;
- deletion- or change-sensitive;
- data-bearing or data-routing;
- orchestration- or flow-critical;
- attached to its own runbook;
- a meaningful blast-radius node an engineer would search for directly.

Evidence that a resource exists never justifies promotion on its own, and staging significance notes are input to this decision rather than the decision itself. Each promoted record requires a stable `resource.*` ID, `resource_type` from `taxonomy/concept-fields.yaml`, definition path, environments, promotion reason, confidence, coverage and evidence. Resource-local actions use the same named fields as the package.

The compiler emits one typed `used_by` collection with `via` provenance instead of separate reverse arrays for each source type or action. Package `resources` is a compact derived ID list. All other reverse and transitive views are computed by `atlas_query.py`.

Keep narrative environment differences, monitoring detail and impact reasoning on the page. Run `python scripts/rebuild_atlas.py` after structured changes; never hand-edit map JSON or managed tables.

## Review

Before approving an infrastructure page, confirm that:

- the package/module/template boundary is correct and evidenced;
- environment differences that change behaviour or risk are stated, and the rest are omitted;
- every promoted resource names which promotion criterion it meets, and unpromoted resources genuinely fail all of them;
- resource connections distinguish explicit definitions from inferred ones through confidence and note;
- claimed component and flow users are supported by those pages rather than asserted here;
- imports, exports, parameters and triggers match the source definitions;
- permissions are described without exposing secret values or sensitive configuration;
- change and deletion impact is marked known, possible or not covered — never absent-therefore-safe.
