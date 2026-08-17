# Repository-component map

`repository-component-map.json` separates source topology from architectural behavior. Repositories answer where code is organised; components answer what independently addressable units do.

## When to use this map

Use it after selecting a repository or component ID when you need source membership, direct component dependencies, durable I/O, or infrastructure actions. Open the page for architectural explanation and coverage limits; use the query tool for reverse and multi-hop impact.

## Shape

The common `metadata` object is described in the maps overview. `repositories` and `components` are keyed by stable IDs.

Repository records may contain mutable locator/default-branch data, `repository_root`, `repository_type`, source roots, an authored `parent_repository`, authored `depends_on_repositories`, compact derived `components` IDs, one typed `used_by` reverse view, governed routes and compact question routes.

Component records may contain `component_type`, repository ID and paths, an authored `parent_component`, durable `consumes`/`produces`, `depends_on`, natural infrastructure fields, one typed `used_by` view, governed routes and compact question routes.

There are no child arrays, source-dependent arrays, cross-repository aggregates, descendant rollups or duplicated participating-flow lists. `atlas_query.py` derives those paths from canonical forward facts and flow steps. Optional empty fields are omitted.

## Example

```json
{
  "metadata": {
    "schema_version": "atlas-map/1.0",
    "generated": true,
    "generator": "scripts/rebuild_atlas.py",
    "package": "datalens",
    "map_type": "repository-component-routing-map",
    "description": "Repository topology and component-owned architecture dependencies.",
    "source_of_truth": [
      "_curated/repositories/**/*.md",
      "_curated/components/**/*.md"
    ],
    "related_maps": {
      "flow_component": "_curated/maps/flow-component/flow-component-map.json",
      "infra_dependency": "_curated/maps/infra-dependency/infra-dependency-map.json"
    }
  },
  "repositories": {
    "repo.orders-platform": {
      "title": "Orders platform",
      "page": "_curated/repositories/orders/orders-platform.md",
      "status": "curated",
      "coverage": "good",
      "primary_domain": "orders",
      "repository_locator": "https://example.invalid/orders-platform",
      "repository_root": "products/orders",
      "repository_type": "monorepo-project",
      "default_branch": "main",
      "source_roots": [
        {"path": "src/api", "purpose": "Order submission API", "evidence": ["products/orders/src/api/README.md"]},
        {"path": "src/worker", "purpose": "Order fulfilment worker", "evidence": ["products/orders/src/worker/README.md"]}
      ],
      "components": ["comp.orders-api", "comp.orders-worker"]
    }
  },
  "components": {
    "comp.orders-api": {
      "title": "Orders API",
      "page": "_curated/components/orders/orders-api.md",
      "status": "curated",
      "coverage": "good",
      "primary_domain": "orders",
      "component_type": "api",
      "repository": "repo.orders-platform",
      "repository_paths": ["src/api"],
      "produces": [
        {
          "id": "schema.order-request",
          "asset_type": "schema",
          "confidence": "reviewed",
          "evidence": ["contracts/order-request.json"]
        }
      ],
      "writes_to": [
        {
          "id": "resource.orders-queue",
          "confidence": "reviewed",
          "evidence": ["src/api/publisher.ts"]
        }
      ],
      "used_by": [
        {
          "id": "flow.order-fulfilment",
          "type": "flow",
          "via": "steps",
          "step_id": "accept-order",
          "order": 10,
          "role": "accepts and validates the request",
          "confidence": "reviewed",
          "evidence": ["src/api/routes.ts"]
        }
      ]
    },
    "comp.orders-worker": {
      "title": "Orders worker",
      "page": "_curated/components/orders/orders-worker.md",
      "status": "curated",
      "coverage": "good",
      "primary_domain": "orders",
      "component_type": "job",
      "repository": "repo.orders-platform",
      "repository_paths": ["src/worker"],
      "reads_from": [
        {
          "id": "resource.orders-queue",
          "confidence": "reviewed",
          "evidence": ["src/worker/handler.ts"]
        }
      ]
    }
  }
}
```

## Traversal and maintenance

Use repository `components` only as a compact membership route. Use component forward fields and `atlas_query.py` for dependency and impact traversal. Stable IDs do not encode repository paths. Edit curated pages and rebuild; never author reverse views or map JSON.
