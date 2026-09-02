# Atlas knowledge plugin distribution plan

Status: agreed design, implementation not started
Date: 2026-09-02

## Goal

Let another engineering team install the Atlas read-only knowledge capability through Claude Code without manually cloning Atlas. Installing the plugin must not distribute `_staging/`, `_intake/`, curation workflows, tests, or other Atlas authoring files.

The `ops` plugin will depend on this knowledge plugin so that one `ops` installation also installs the tested Atlas knowledge version.

## Decision

Create a self-contained Claude Code plugin below `plugins/atlas-knowledge/` in the Atlas repository.

The plugin directory is the distribution boundary:

```text
Atlas/
├── _staging/
├── _intake/
├── evaluation/
├── tests/
└── plugins/
    └── atlas-knowledge/
        ├── .claude-plugin/
        │   └── plugin.json
        ├── atlas-package.json
        ├── index.md
        ├── _curated/
        ├── skills/
        ├── agents/
        └── scripts/
```

A marketplace entry will use the `git-subdir` source type and point to `plugins/atlas-knowledge`. Claude Code can then use a sparse Git checkout for that directory instead of installing the whole Atlas repository.

The plugin will contain only read-only Ask Atlas capabilities. Teach Atlas, Sync Atlas, Curate Atlas, staging records, intake state, linting, generation, and evaluation remain in the authoring repository.

Do not use symlinks. Do not use the Atlas repository root as the plugin source. Do not introduce a generated release branch for the first implementation.

Use the existing Nexus pipeline only as a fallback if moving the canonical consumer files into one subtree proves too disruptive.

## Why the plugin must be self-contained

`plugin.json` controls which skills, agents, hooks, and servers Claude registers. It does not filter the files downloaded from the configured plugin source.

If the marketplace points to the Atlas repository root, Claude can download the whole repository even when the manifest registers only one skill. That arrangement hides commands from the user interface, but it does not keep `_staging/` or other files off the consuming machine.

A `git-subdir` source gives the required file boundary, but every runtime dependency must live below that directory. A skill in `plugins/atlas-knowledge/` cannot rely on `../../_curated`, `../../scripts`, or another path outside the plugin root after installation.

## Current Atlas constraints

The current repository is not yet arranged around this boundary:

- Authoritative knowledge lives in root `_curated/`.
- The package identity and entry points live in root `atlas-package.json` and `index.md`.
- `atlas-discover` and `atlas-impact` live under `.claude/skills/`.
- Both skills read several files from `.claude/skills/_shared/`.
- The runtime contract calculates `ATLAS_ROOT` from the current `.claude/skills/<skill>` layout and expects `atlas-package.json` at that root.
- `_curated/index.md` invokes `scripts/atlas_query.py` for deterministic lookup and traversal.
- `scripts/atlas_query.py` imports both read-only query code and staging query code at startup.

Creating only a new manifest below `plugins/atlas-knowledge/` would therefore produce a plugin that installs but cannot perform the existing Atlas discovery flow. The implementation must move or refactor the complete read-only runtime into the plugin boundary.

## Content boundary

The first implementation must confirm the exact dependency list. The expected boundary is:

| Include | Reason |
|---|---|
| `.claude-plugin/plugin.json` | Defines the plugin and its version |
| `atlas-package.json` | Identifies and validates the installed Atlas package |
| `index.md` and `_curated/**` | Supplies read-only navigation, records, indexes, and generated maps |
| `skills/atlas-discover/**` | Provides normal Ask Atlas retrieval |
| `skills/atlas-impact/**` | Provides change-impact traversal when `ops` needs it |
| Required shared skill contracts | Preserves routing, provenance, uncertainty, and bounded source fallback |
| Required read-only agents | Supports delegated discovery and impact synthesis |
| A read-only query command and its imports | Preserves deterministic ID resolution, search, and map traversal |

The plugin must exclude:

- `_staging/**` and `_intake/**`;
- curation, staging, onboarding, and repository setup skills;
- authoring-only taxonomy and contracts unless the dependency audit proves that read-only lookup needs them;
- lint, rebuild, intake, and evaluation commands;
- tests, fixtures, CI files, repository instructions, and historical artifacts;
- credentials, local paths, and machine-specific configuration.

## Marketplace shape

Keep the marketplace catalog in the existing plugin marketplace repository or another small catalog location. Do not require consumers to add Atlas itself as a marketplace.

Illustrative marketplace entry:

```json
{
  "name": "atlas-knowledge",
  "source": {
    "source": "git-subdir",
    "url": "git@gitlab.company.example:team/atlas.git",
    "path": "plugins/atlas-knowledge",
    "ref": "main"
  }
}
```

The production URL must use the internal GitLab repository and the team's existing Git authentication method. The public GitHub repository remains a development reference unless the team explicitly chooses it as a source.

The `ops` plugin declares the dependency in its own manifest:

```json
{
  "name": "ops",
  "dependencies": [
    { "name": "atlas-knowledge", "version": "~1.0.0" }
  ]
}
```

Both plugins should remain in the same marketplace. This avoids cross-marketplace trust configuration and allows Claude Code to resolve the dependency during the `ops` installation.

## Versioning and releases

Use semantic versions in `plugins/atlas-knowledge/.claude-plugin/plugin.json`.

Tag a tested Git-backed release as `atlas-knowledge--v<version>`, for example `atlas-knowledge--v1.0.0`. Update the `ops` dependency only after its workflows pass against that knowledge release.

A patch release changes compatible knowledge or fixes retrieval behavior. A minor release adds compatible knowledge types or capabilities. A major release changes paths, IDs, retrieval contracts, or behavior that may break `ops`.

Do not make `ops` depend on an untested moving `main` version in production.

## Implementation plan

### 1. Prove the dependency boundary

1. Trace every file read by `atlas-discover`, `atlas-impact`, their shared contracts, and their delegated agents.
2. Trace the imports and data paths used by `scripts/atlas_query.py` for `find`, `resolve`, `route`, and map traversal.
3. Record which taxonomy and contract files the read-only commands actually require.
4. Add a failing boundary test that reports any runtime path outside `plugins/atlas-knowledge/`.

Deliverable: an exact, test-backed list of files required by the read-only plugin.

### 2. Separate read-only query behavior

1. Split read-only query commands from staging and intake commands.
2. Remove import-time dependencies on staging code from the consumer entry point.
3. Keep the existing absence and uncertainty rules. A missing match must not become evidence that no record exists.
4. Preserve deterministic stable-ID resolution and generated-map traversal.

Deliverable: a read-only query entry point that runs with no `_staging/` or `_intake/` directory.

### 3. Establish the canonical plugin subtree

1. Create `plugins/atlas-knowledge/`.
2. Move the confirmed consumer runtime into that directory as its canonical location.
3. Update Atlas authoring workflows, scripts, documentation, and tests to use the new paths in the same change.
4. Do not maintain a hand-copied second `_curated/` tree.
5. Keep root authoring entry points small if humans still need convenient links into the package.

Deliverable: one canonical copy of each consumer file, all below the plugin root.

### 4. Adapt the Claude runtime

1. Add `.claude-plugin/plugin.json` at the plugin root.
2. Register only the read-only skills and required agents.
3. Replace assumptions tied to the old `.claude/skills/` depth with plugin-root-aware resolution.
4. Change recovery guidance so installed-plugin users are not told to restart with `claude --add-dir <ATLAS_ROOT>`.
5. Keep authoring guidance outside the consumer plugin.

Deliverable: the plugin can answer an Ask Atlas question from another repository without an Atlas checkout.

### 5. Wire the marketplace and `ops` dependency

1. Add the `git-subdir` marketplace entry.
2. Add the versioned `atlas-knowledge` dependency to `ops`.
3. Confirm that both entries resolve within the same marketplace.
4. Test with the same GitLab authentication method used by the target team.

Deliverable: installing `ops` also installs and enables the approved Atlas knowledge plugin.

### 6. Add release checks

Add CI checks that:

- validate the Atlas repository and generated maps;
- validate the Claude plugin manifest;
- run read-only query tests against the plugin directory alone;
- reject paths that escape the plugin root;
- reject `_staging`, `_intake`, write skills, and secrets inside the plugin subtree;
- install the marketplace and plugin in an isolated Claude configuration;
- verify the dependency and version before creating a release tag.

Test on Windows with `core.symlinks=false`. The installation must pass because the design uses ordinary files rather than symlinks.

## Acceptance criteria

The design is complete when all of the following statements are true:

- A user adds the existing marketplace and installs `ops` without manually cloning Atlas.
- Claude Code installs `atlas-knowledge` automatically as the `ops` dependency.
- The installed Atlas plugin contains only files below `plugins/atlas-knowledge/`.
- The installed plugin contains no `_staging`, `_intake`, write workflow, or repository-maintenance content.
- Ask Atlas resolves stable IDs, searches curated records, follows indexes, and traverses generated maps.
- Impact analysis reports confirmed, possible, external, and unknown impact without treating an absent edge as proof of safety.
- The Atlas authoring checkout still supports Ask Atlas, Teach Atlas, Sync Atlas, and Curate Atlas.
- Atlas lint, map freshness checks, and tests pass after the path migration.
- A prior plugin version can be restored by selecting its release tag.

## Options considered

| Option | Advantages | Disadvantages | Decision |
|---|---|---|---|
| Self-contained Atlas subdirectory with `git-subdir` | Same repository, one install, sparse checkout, clear distribution boundary, normal Git authentication, Git-backed versions | Requires a path migration and a read-only runtime split | Selected |
| Atlas repository root as plugin source with a limited manifest | Almost no restructuring; current paths keep working | Downloads the whole repository; the manifest is not a file allowlist; authoring data reaches consumers | Rejected for production |
| Symlinks from a plugin directory to root knowledge | Keeps current source paths and avoids copied files | Windows has `core.symlinks=false`; local checkout and plugin-cache behavior are fragile; links can escape the intended boundary | Rejected |
| CI-built ZIP published to Nexus | Strong allowlist; keeps the current Atlas layout; existing Nexus pipeline can publish versions | Adds a build product, update logic, archive authentication, and a second representation to test | Fallback |
| Generated Git release branch | Keeps Git-based installation and can publish a filtered tree | Adds bot push permissions, generated history, and release-branch maintenance without an advantage over the existing Nexus path | Rejected |
| Separate knowledge repository | Strong repository boundary and independent permissions | Creates source synchronization and ownership overhead; conflicts with the same-repository goal | Rejected |

## Benefits

- Consumers receive only reviewed, read-only Atlas knowledge and its retrieval runtime.
- The `ops` plugin can depend on a tested knowledge version.
- Git remains the source and release history.
- Users do not manage an Atlas checkout or local symlinks.
- The directory structure enforces the distribution boundary more reliably than manifest instructions.

## Costs and risks

- Moving `_curated/` and read-only runtime files will touch many paths in documentation, tests, and scripts.
- The current discovery runtime assumes an Atlas checkout and must distinguish plugin installation from authoring checkout.
- A poor dependency audit could omit a shared contract or Python module and produce a plugin that installs but fails at runtime.
- Publishing every knowledge update as a plugin release may create version noise. Release policy must separate normal source commits from consumer releases.
- Consumers still need GitLab read permission. Sparse checkout reduces downloaded content but does not bypass repository authorization.
- A self-contained subtree is an organisational boundary, not a replacement for secret scanning or repository access control.

## Rollback

Before moving canonical paths, tag or record the last pre-plugin commit. Keep the migration in one reviewable change so that reverting it restores the original layout.

If the self-contained migration proves too disruptive, stop before publishing `atlas-knowledge` 1.0.0. Keep the existing Atlas layout and implement the Nexus ZIP fallback with a CI allowlist. Do not fall back to symlinks or silently expose the Atlas repository root.

## Open implementation decisions

- Confirm whether the first release needs both `atlas-discover` and `atlas-impact`, or only discovery.
- Confirm the minimal read-only agent set.
- Choose the exact internal GitLab URL and marketplace repository.
- Decide who owns release approval and version bumps.
- Measure the plugin size and install time before setting a release cadence.

## External references

- Claude Code plugin marketplace and `git-subdir`: https://code.claude.com/docs/en/plugin-marketplaces#git-subdirectories
- Claude Code plugin dependencies and release tags: https://code.claude.com/docs/en/plugin-dependencies
