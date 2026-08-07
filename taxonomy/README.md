# Taxonomy

TeamA Atlas uses deterministic vocabularies so humans, skills, lint, and generated maps share the same type system.

- `types.yaml` defines active and reserved page types, storage roots, and stable ID prefixes.
- `relationships.yaml` defines the approved relationship vocabulary, meaning, reciprocal display semantics, and type constraints where they are useful.
- `statuses.yaml` defines curated/staging states, relationship confidence, and map coverage vocabulary.
- `standard-categories.yaml` defines the organisational categories available to `atlas.standard` pages.

Reserved types are not active V1 features. Taxonomy changes require review; do not silently invent near-duplicate types, relationships, statuses, or standard categories.
