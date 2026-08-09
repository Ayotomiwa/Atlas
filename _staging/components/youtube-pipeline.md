---
id: STG-20260808-youtube-pipeline
type: atlas.staging.component
package: teama
schema_version: atlas/1.0
timestamp: 2026-08-08
title: "Data Pipeline"
description: "End-to-End Data engineering project (YouTube data)"
status: curated
captured_by: "Antigravity AI"
source_type: "repository"
source_links: ["https://github.com/andreichiro/data_engineer_end2end.git"]
intended_curated_targets: ["_curated/components/youtube-pipeline.md"]
---

# Component evidence: data_engineer_end2end

> Capture attributable discovery, not a polished component page. Keep observed/user-confirmed facts separate from possible relationships and do not create linked evidence files solely to make this record look complete.

## Summary

This repository contains an end-to-end data engineering pipeline that extracts YouTube videos via Airflow, processes them via Databricks and AWS Lambda, and serves an LLM via Django. User clarified it should be treated as a single unified component.

### Component identity and location

- Component name: Data Pipeline
- Observed type/scope: End-to-end pipeline / Repository
- Repository: data_engineer_end2end
- Monorepo path: `/`
- Main README / local `CLAUDE.md`: `README.md`
- Build/dependency file: `handlers-airflow/requirements.txt`
- Important source/config/schema paths: `handlers-airflow/`, `databricks/`, `aws/`

### Responsibility / boundary

Extract YouTube data via API, process it (ELT), and serve insights through an LLM.

## Evidence

- Repository/path: `data_engineer_end2end`
- README/docs: `README.md`
- Code/config path: `aws/lambda.py`

## What is known

### Internal units

| Unit | Type | Purpose/role | Path | Source | State |
|---|---|---|---|---|---|
| Airflow DAGs | orchestrator | Extract youtube data | `handlers-airflow/` | `README.md` | observed |
| Databricks | transformer | Transform data in S3 | `databricks/` | `README.md` | observed |
| Kinesis Lambda | serverless-function | Stream processing | `aws/lambda_kinesis.py` | codebase | observed |
| Django App | serving | Serve LLM predictions | `application/` | `README.md` | observed |
| dbt models | transformation | Build facts/dims | `app_dbt/` | `README.md` | observed |

### Consumes

| Kind | Name/target | From/source | Evidence | State |
|---|---|---|---|---|
| api | youtube-data-api | YouTube | `README.md` | observed |

### Produces

| Kind | Name/target | Known consumer/use | Evidence | State |
|---|---|---|---|---|
| api | llm-predictions | data analysts | `README.md` | observed |

### Related flows

| Flow/candidate flow | Role in flow | Evidence | State |
|---|---|---|---|
| YouTube Data Flow | core-pipeline | `README.md` | user-confirmed |

### Related infrastructure

| Package/resource | Relationship to component | Evidence | State |
|---|---|---|---|
| AWS Kinesis | deployed-by | `README.md` | observed |
| AWS Lambda | deployed-by | `README.md` | observed |
| AWS S3 | deployed-by | `README.md` | observed |
| Databricks Cluster | deployed-by | `README.md` | observed |
| AWS ECS | deployed-by | `README.md` | observed |

### Local repository references

- Local README/build guidance: `README.md`
- Test guidance: *Not covered*
- Runtime/deployment guidance: `handlers-airflow/docker-compose.yaml`
- Other stable reference: *Not covered*

### Operational notes

- *Not covered — no evidence in current staging material.*

### Runbooks, standards and incident learnings

- Runbook evidence/reference: *Not covered*
- Standard/convention evidence/reference: *Not covered*
- Incident/near-miss learning reference: *Not covered*

### Other known findings

| Finding | Source | State (`observed` / `user-confirmed`) |
|---|---|---|
| User confirmed ownership | User input | user-confirmed |

## What is possible / unconfirmed

| Possible finding/relationship | Why plausible | Evidence needed |
|---|---|---|
| *Not covered* | *Not covered* | *Not covered* |

## Suggested curated targets

- `_curated/components/youtube-pipeline.md`

## Open questions

- Are there specific runbooks or failure operational patterns? (Not covered)
