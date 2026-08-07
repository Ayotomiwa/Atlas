---
id: atlas-package.teama
type: atlas.package
package: teama
schema_version: atlas/1.0
title: TeamA Atlas
description: Governed engineering context for TeamA humans and AI agents.
status: active
owners:
  team: team-a-engineering
  maintainers: []
domains: []
entrypoints:
  root: index.md
  curated: _curated/index.md
  staging: _staging/index.md
  components: _curated/components/index.md
  flows: _curated/flows/index.md
  infra: _curated/infra/index.md
  schema_info: _curated/schema-info/index.md
  business_concepts: _curated/business-concepts/index.md
  standards: _curated/standards/index.md
  runbooks: _curated/runbooks/index.md
  incidents: _curated/incidents/index.md
  maps: _curated/maps/index.md
  status: _curated/status/curation-status.md
  onboarding: onboarding/index.md
maps:
  flow_component: _curated/maps/flow-component-map.json
  repo_dependency: _curated/maps/repo-dependency-map.json
  infra_dependency: _curated/maps/infra-dependency-map.json
taxonomy:
  types: taxonomy/types.yaml
  relationships: taxonomy/relationships.yaml
  statuses: taxonomy/statuses.yaml
  standard_categories: taxonomy/standard-categories.yaml
routing:
  aliases: [teama, team-a, "team a"]
  questions:
    - What does this TeamA service do and depend on?
    - How does this TeamA flow work end to end?
    - What could be affected by this infrastructure change?
    - Which TeamA standard applies?
---

# Responsibility
TeamA Atlas stores governed engineering context. `_staging/` is evidence; `_curated/` is reviewed knowledge; maps are generated from curated relationships.
