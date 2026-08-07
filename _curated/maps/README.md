# Generated maps

Curated Markdown `relationships:` are the source of truth. The JSON files in this directory are committed, deterministic projections produced by `scripts/rebuild_maps.py`.

- `flow-component-map.json` projects flow participation and flow dependencies.
- `repo-dependency-map.json` projects component consumes/produces/depends-on relationships.
- `infra-dependency-map.json` projects infrastructure dependencies/deployment/resource-use relationships.

Generated maps include forward edges and derived reverse views. Never hand-author relationship data in these JSON files. Run `python scripts/rebuild_maps.py` after relationship changes and `python scripts/rebuild_maps.py --check` before proposing a change.
