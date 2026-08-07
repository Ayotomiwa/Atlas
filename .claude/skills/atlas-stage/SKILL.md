---
name: atlas-stage
description: Use when a reusable fact is discovered during normal work and should enter Atlas without a full onboarding crawl.
allowed-tools: Read, Grep, Glob, Write, Edit
---

# atlas-stage

1. Identify the correct staging bucket.
2. Read its `README.md` and `_template.md`.
3. Ask only blocking questions; if knowledge came from a private conversation/external source, require explicit user approval before persisting it.
4. Allocate a deterministic `STG-YYYYMMDD-<slug>` ID, scanning for same-day collisions.
5. Capture source/evidence, uncertainty and suggested curated targets in one staging entry.
6. Run staging lint.
7. Never write curated content.
