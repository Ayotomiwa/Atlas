# Atlas taxonomy

These files are the machine-readable contract used by lint and map generation:

- `types.yaml` declares active and reserved page types and storage folders.
- `relationships.yaml` declares relationship vocabulary and map verb mappings.
- `statuses.yaml` declares curated/staging status, relationship confidence and map coverage enums.

## Proposing a taxonomy change

1. Change the relevant YAML contract on a feature branch.
2. Update affected templates or scripts.
3. Add/update validation fixtures.
4. Run `python scripts/atlas_lint.py . --self-test`, `python scripts/rebuild_maps.py --check`, and `python scripts/atlas_lint.py .`.
5. Submit for human review. Reserved v1 types (`join-path`, `query-pattern`, `decision`) must not have pages.
