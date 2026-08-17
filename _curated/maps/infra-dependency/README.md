# Infrastructure dependency map

`infra-dependency-map.json` exposes meaningful infrastructure packages and only the resources explicitly promoted for independent routing or impact analysis.

## When to use this map

Use it after selecting an infrastructure package or promoted resource ID when you need its direct actions, package membership, or known users. Open the infrastructure page for ordinary resources, operational meaning, promotion evidence, and coverage gaps; use the query tool for broader impact traversal.

## Shape

`packages` and `resources` are keyed by stable `infra.*` and `resource.*` IDs. Package records route to a repository and mutable `package_path` when source-controlled, expose a compact derived `resources` ID list, keep natural authored dependency/action fields and one typed `used_by` array.

Resource records expose `resource_type`, canonical `parent_package`, definition path, environments, promotion reason, confidence, coverage and evidence, plus the same natural dependency/action fields and one typed `used_by` array. Ordinary unpromoted resources remain on the Markdown page.

`used_by` entries contain source `id`, node `type`, the natural `via` field, confidence/evidence and optional step data. Separate `used_by_components`, `used_by_flows`, schedules, monitors and other reciprocal arrays are intentionally absent. Optional empty fields are omitted.

## Example

```json
{
  "metadata": {
    "schema_version": "atlas-map/1.0",
    "generated": true,
    "generator": "scripts/rebuild_atlas.py",
    "package": "datalens",
    "map_type": "package-resource-impact-map",
    "description": "Infrastructure packages, promoted resources and direct users.",
    "source_of_truth": [
      "_curated/infra/**/*.md",
      "_curated/components/**/*.md",
      "_curated/flows/**/*.md"
    ],
    "related_maps": {
      "flow_component": "_curated/maps/flow-component/flow-component-map.json",
      "repository_component": "_curated/maps/repository-component/repository-component-map.json"
    }
  },
  "packages": {
    "infra.orders-runtime": {
      "title": "Orders runtime infrastructure",
      "page": "_curated/infra/orders/orders-runtime.md",
      "status": "curated",
      "coverage": "good",
      "primary_domain": "orders",
      "infra_package": "orders-runtime",
      "repository": "repo.orders-platform",
      "package_path": "infra/orders",
      "environments": ["prod", "staging"],
      "resources": ["resource.orders-queue"]
    }
  },
  "resources": {
    "resource.orders-queue": {
      "name": "Orders queue",
      "resource_type": "sqs-queue",
      "parent_package": "infra.orders-runtime",
      "page": "_curated/infra/orders/orders-runtime.md",
      "status": "curated",
      "defined_in_path": "infra/orders/queue.tf",
      "environments": ["prod", "staging"],
      "promotion_reason": "Independent failure and backlog impact boundary.",
      "confidence": "reviewed",
      "coverage": "good",
      "evidence": ["infra/orders/queue.tf"],
      "used_by": [
        {
          "id": "comp.orders-api",
          "type": "component",
          "via": "writes_to",
          "confidence": "reviewed",
          "evidence": ["src/api/publisher.ts"]
        },
        {
          "id": "comp.orders-worker",
          "type": "component",
          "via": "reads_from",
          "confidence": "reviewed",
          "evidence": ["src/worker/handler.ts"]
        },
        {
          "id": "flow.order-fulfilment",
          "type": "flow",
          "via": "steps",
          "step_id": "queue-order",
          "order": 20,
          "role": "durable handoff",
          "confidence": "reviewed",
          "evidence": ["infra/orders/queue.tf"]
        }
      ]
    }
  }
}
```

## Traversal and maintenance

Use forward fields for direct meaning, `used_by` for quick reverse impact and `atlas_query.py` for complete reverse/transitive traversal. Edit package/resource frontmatter and rebuild; never hand-edit generated JSON.
