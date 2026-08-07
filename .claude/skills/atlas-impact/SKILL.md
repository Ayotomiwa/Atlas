---
name: atlas-impact
description: Use for blast-radius questions such as what breaks if a TeamA component, flow or infrastructure concept changes, is deleted or fails.
allowed-tools: Read, Grep, Glob
---

# atlas-impact

1. Resolve the starting concept from package/index routing.
2. Traverse page relationships and the relevant generated map, including reverse edges.
3. Resolve linked flows/components/infra.
4. Bucket results as **known affected / possibly affected / unknown or not covered** and cite evidence.
5. Never claim “not affected” merely because an edge is absent.
6. Never write files.
