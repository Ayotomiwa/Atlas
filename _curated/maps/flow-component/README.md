# Flow-component map

`flow-component-map.json` is the generated ordered-flow interface. Flow `steps` are the only participant representation: a step may name a component, infrastructure package/resource, external system, manual actor or unknown actor. The map never repeats those steps as a later component or infrastructure roster.

## Shape

`metadata` contains `schema_version`, `generated`, `generator`, `package`, `map_type`, `description`, `source_of_truth` and `related_maps`. It contains no timestamps, relationship enum dump or embedded author taxonomy.

`flows` is keyed by stable `flow.*` ID. A record may contain:

| Field | Meaning |
|---|---|
| `page`, `status`, `coverage`, domain fields | Routing and trust context |
| `entry_points` | Named boundary starts classified by `entry_point_type` |
| `inputs`, `outputs` | Whole-flow durable boundary assets |
| `steps` | Ordered participants, roles, confidence/evidence, material handoffs and optional transitions |
| `upstream_flows` | Authored prerequisites |
| `downstream_flows` | The one generated reverse flow view, with `via` provenance |
| `runbooks`, `standards`, `incident_learnings` | Direct governed routes |
| `open_questions` | Compact qualified question routes; page prose owns the question text |

Every natural connection entry uses `id` for a stable local target or `name` for an external target. The containing field supplies the meaning; entries do not repeat `relationship`, target page/status/type or reciprocal facts. Optional empty fields are omitted.

## Example

This example belongs to the same fictional Orders system used by the other map READMEs.

```json
{
  "metadata": {
    "schema_version": "atlas-map/1.0",
    "generated": true,
    "generator": "scripts/rebuild_atlas.py",
    "package": "teama",
    "map_type": "flow-component-routing-map",
    "description": "Ordered flow steps, boundary I/O and operational routes.",
    "source_of_truth": ["_curated/flows/**/*.md"],
    "related_maps": {
      "repository_component": "_curated/maps/repository-component/repository-component-map.json",
      "infra_dependency": "_curated/maps/infra-dependency/infra-dependency-map.json"
    }
  },
  "flows": {
    "flow.order-fulfilment": {
      "title": "Order fulfilment",
      "page": "_curated/flows/orders/order-fulfilment.md",
      "status": "curated",
      "coverage": "good",
      "primary_domain": "orders",
      "entry_points": [
        {
          "entry_point_type": "api",
          "name": "Submit order",
          "confidence": "reviewed",
          "evidence": ["src/api/routes.ts"]
        }
      ],
      "inputs": [
        {
          "id": "schema.order-request",
          "asset_type": "schema",
          "confidence": "reviewed",
          "evidence": ["contracts/order-request.json"]
        }
      ],
      "steps": [
        {
          "step_id": "accept-order",
          "order": 10,
          "name": "Accept order",
          "participant": {"type": "component", "id": "comp.orders-api", "name": "Orders API"},
          "role": "accepts and validates the request",
          "confidence": "reviewed",
          "evidence": ["src/api/routes.ts"]
        },
        {
          "step_id": "queue-order",
          "order": 20,
          "name": "Buffer order command",
          "participant": {"type": "infra-resource", "id": "resource.orders-queue", "name": "Orders queue"},
          "role": "durable handoff",
          "confidence": "reviewed",
          "evidence": ["infra/orders/queue.tf"]
        },
        {
          "step_id": "fulfil-order",
          "order": 30,
          "name": "Fulfil order",
          "participant": {"type": "component", "id": "comp.orders-worker", "name": "Orders worker"},
          "role": "processes the command",
          "confidence": "reviewed",
          "evidence": ["src/worker/handler.ts"],
          "emits": [
            {
              "id": "schema.order-fulfilled",
              "asset_type": "event",
              "confidence": "reviewed",
              "evidence": ["contracts/order-fulfilled.json"]
            }
          ]
        }
      ],
      "outputs": [
        {
          "id": "schema.order-fulfilled",
          "asset_type": "event",
          "confidence": "reviewed",
          "evidence": ["contracts/order-fulfilled.json"]
        }
      ],
      "downstream_flows": [
        {
          "id": "flow.order-notification",
          "type": "flow",
          "via": "upstream_flows",
          "confidence": "reviewed",
          "evidence": ["notifications/workflow.yaml"]
        }
      ]
    }
  }
}
```

## Traversal and maintenance

Use `steps` for “who/what performs this flow?” and `atlas_query.py` for reverse or transitive impact. Trust only `status: curated` records on the governed branch. Edit the flow Markdown and run `python scripts/rebuild_atlas.py`; never edit this JSON directly.
