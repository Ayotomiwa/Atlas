# Curated index

## Route by question

Use `python scripts/atlas_query.py find "<question>"` for deterministic candidate lookup, then open the selected page and follow its links. Use the collection/domain routes below when search is weak, ambiguous or the task is exploratory.

- What source repository is this and what does it contain? Use the [repositories index](repositories/index.md), then the [repository/component map](maps/repository-component/repository-component-map.json).
- What does an architectural unit do? Use the [components index](components/index.md), then the [repository/component map](maps/repository-component/repository-component-map.json).
- How does an end-to-end path work? Use the [flows index](flows/index.md), then the [flow/component map](maps/flow-component/flow-component-map.json).
- What infrastructure exists or what directly uses it? Use the [infrastructure index](infra/index.md), then the [infrastructure map](maps/infra-dependency/infra-dependency-map.json).
- What does a durable data/interface asset mean? Use [schema information](schema-info/index.md); schemas remain pages and are routed from map I/O entries.
- What business term or boundary applies? Use [business concepts](business-concepts/index.md).
- Which engineering rule applies? Use [standards](standards/index.md).
- How is an operational problem handled? Use [runbooks](runbooks/index.md) and [incident learnings](incidents/index.md).

For direct and transitive routing, use `python scripts/atlas_query.py`. Maps should answer first; open linked pages only when narrative, evidence or unresolved context is necessary.

Every `status: curated` page is authoritative. Query may add one concise checkout advisory for off-main, modified, untracked or detached work; it never blocks local discovery or requires a later status update.
