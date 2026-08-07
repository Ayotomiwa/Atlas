---
name: atlas-stage
description: Capture one reusable fact as raw Atlas evidence without performing a full onboarding crawl.
allowed-tools: Read, Grep, Glob, Write, Edit
---

# atlas-stage

Identify the staging bucket; read its README and template; ask only blocking questions; allocate a deterministic `STG-YYYYMMDD-<slug>` ID; capture source, evidence and uncertainty; write one staging entry; run staging lint. Never write curated content. If knowledge came from a private conversation/external source, require explicit user approval before persisting it.
