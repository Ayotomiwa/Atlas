# Curated index

## Route by stable ID first

When you have a stable ID, use `python scripts/atlas_query.py resolve <id>` and open the returned owner page. This is the direct route for pages, embedded data assets and promoted infrastructure resources; it does not make map absence evidence of absence.

When you have a question rather than an ID, use `python scripts/atlas_query.py find "<question>"` for deterministic candidate lookup, select the supported candidate, then resolve and open that page. Use the collection/domain routes below when search is weak, ambiguous or the task is exploratory.

- What source repository is this and what does it contain? Use the [repositories index](repositories/index.md). Use the [repository/component map](maps/repository-component/repository-component-map.json) for reverse ownership or multi-hop traversal.
- What does an architectural unit do? Use the [components index](components/index.md). Use the [repository/component map](maps/repository-component/repository-component-map.json) for reverse ownership or multi-hop traversal.
- How does an end-to-end path work? Use the [flows index](flows/index.md). Use the [flow/component map](maps/flow-component/flow-component-map.json) for reverse or multi-hop traversal.
- What infrastructure exists or what directly uses it? Use the [infrastructure index](infra/index.md). Use the [infrastructure map](maps/infra-dependency/infra-dependency-map.json) for reverse or multi-hop traversal.
- What does a durable data/interface asset mean? Use [schema information](schema-info/index.md); schemas remain pages and are routed from map I/O entries.
- What business term or boundary applies? Use [business concepts](business-concepts/index.md).
- Which engineering rule applies? Use [standards](standards/index.md).
- How is an operational problem handled? Use [runbooks](runbooks/index.md) and [incident learnings](incidents/index.md).

For direct and transitive routing, use `python scripts/atlas_query.py`. Maps are generated traversal aids for reverse and multi-hop questions; the resolved curated owner page carries the direct record, narrative, evidence and unresolved context.

Every `status: curated` page is authoritative. Query may add one concise checkout advisory for off-main, modified, untracked or detached work; it never blocks local discovery or requires a later status update.
