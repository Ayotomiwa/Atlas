# Curated index

## Route by question

- What source repository is this and what does it contain? Use the [repositories index](repositories/index.md), then the [repository/component map](maps/repository-component/repository-component-map.json).
- What does an architectural unit do? Use the [components index](components/index.md), then the [repository/component map](maps/repository-component/repository-component-map.json).
- How does an end-to-end path work? Use the [flows index](flows/index.md), then the [flow/component map](maps/flow-component/flow-component-map.json).
- What infrastructure exists or what directly uses it? Use the [infrastructure index](infra/index.md), then the [infrastructure map](maps/infra-dependency/infra-dependency-map.json).
- What does a durable data/interface asset mean? Use [schema information](schema-info/index.md); schemas remain pages and are routed from map I/O entries.
- What business term or boundary applies? Use [business concepts](business-concepts/index.md).
- Which engineering rule applies? Use [standards](standards/index.md).
- How is an operational problem handled? Use [runbooks](runbooks/index.md) and [incident learnings](incidents/index.md).

For direct and transitive routing, use `python scripts/atlas_query.py`. Maps should answer first; open linked pages only when narrative, evidence or unresolved context is necessary.

Local pages may be used for routing with their lifecycle status preserved. Treat only human-reviewed, merged `status: curated` content as authoritative. A query warning outside `main` or `master` is advisory and does not block local discovery.
