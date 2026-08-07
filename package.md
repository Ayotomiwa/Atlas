---
id: atlas.datalens
type: atlas.package
package: datalens
schema_version: atlas/1.0
title: DataLens Atlas Package
description: Governed engineering and data context for DataLens.
status: active
owners:
  team: datalens-engineering
  maintainers: []
domains: [sds, data-ingestion, data-processing, data-quality]
entrypoints:
  root: index.md
  curated: _curated/index.md
  components: _curated/components/index.md
  flows: _curated/flows/index.md
  infra: _curated/infra/index.md
  schema_info: _curated/schema-info/index.md
  business_concepts: _curated/business-concepts/index.md
  standards: _curated/standards/index.md
  runbooks: _curated/runbooks/index.md
  incidents: _curated/incidents/index.md
  domains: _curated/domains/index.md
  maps: _curated/maps/index.md
  status: _curated/status/curation-status.md
maps:
  repo_dependency_map: _curated/maps/repo-dependency-map.json
  infra_dependency_map: _curated/maps/infra-dependency-map.json
  flow_component_map: _curated/maps/flow-component-map.json
taxonomy:
  types: taxonomy/types.yaml
  relationships: taxonomy/relationships.yaml
  statuses: taxonomy/statuses.yaml
routing:
  aliases: [datalens, data lens, dl]
  questions:
    - How does DataLens ingest data?
    - Which DataLens component owns this table?
    - What breaks if this DataLens resource changes?
dependencies:
  required: []
  contextual: []
---

# Responsibility

Governed operating context for DataLens: components, flows, infrastructure, schema information, business concepts, standards, runbooks and incident learnings.

# Main entry points

- [Curated knowledge](_curated/index.md)
- [Domains](_curated/domains/index.md)
- [Dependency maps](_curated/maps/index.md)
- [Curation status](_curated/status/curation-status.md)
