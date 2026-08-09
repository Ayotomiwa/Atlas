---
id: STG-20260808-data-engineer-end2end-repo-scan
type: atlas.staging.component
package: teama
schema_version: atlas/1.0
timestamp: 2026-08-08
title: "Data Pipeline — deep repository scan (corrective/supplementary evidence)"
description: "Bounded read-only repo inspection of data_engineer_end2end via atlas-onboard-service; corrects and deepens STG-20260808-youtube-pipeline"
status: curated
captured_by: "Claude Code (atlas-onboard-service)"
source_type: "repository"
source_links: ["https://github.com/andreichiro/data_engineer_end2end.git"]
intended_curated_targets: ["_curated/components/youtube-pipeline.md"]
---

# Component evidence: data_engineer_end2end (corrective/supplementary scan)

> This record supplements `STG-20260808-youtube-pipeline` (captured_by "Antigravity AI", already referenced by the proposed curated page `_curated/components/youtube-pipeline.md`, status `proposed`). Per immutability rules that prior record is not altered here. This entry was produced by a materially deeper, code-level (not README-only) inspection and surfaces several corrections a curator should apply before approving the existing proposal.

## Summary

Personal/portfolio end-to-end data engineering project (owner-confirmed: session user Ayotomiwa, treated as a solo-maintained project — see Owner note below). Extracts YouTube video metadata/transcripts, moves it through raw→staging→mart layers, with an aspirational (not-yet-implemented) LLM-serving Django application. This evidence was gathered via direct inspection of source/config/IaC files, not just the root README, and corrects several claims the prior staging/curated pair took from README prose at face value.

### Component identity and location

- Component name: Data Pipeline (same candidate identity as `STG-20260808-youtube-pipeline` / `atlas-comp.youtube.pipeline`)
- Observed type/scope: personal/portfolio end-to-end pipeline, monorepo
- Repository: `data_engineer_end2end` (https://github.com/andreichiro/data_engineer_end2end.git)
- Monorepo path: `/`
- Main README: `README.md` (root); subdirectory READMEs also exist: `app_dbt/README.md`, `aws/README.md`, `databricks/README.md`, `handlers-airflow/README.md`
- Local `CLAUDE.md`: not present. Only `.claude/settings.local.json` exists (disables an MCP server, `gemini-api-docs-mcp`) — not a standards/ownership document.
- Build/dependency files: `handlers-airflow/airflow-project/requirements.txt` (or equivalent), `app_dbt/packages.yml`, `application/requirements.txt`
- Important source/config/schema paths: `handlers-airflow/airflow-project/dags/`, `app_dbt/models/`, `app_dbt/models/intermediate/sources.yml`, `application/apps/alunos/`, `application/infra/`, `aws/lambda.py`, `aws/lambda_kinesis.py`, `databricks/`

### Owner

- User-confirmed (this session, 2026-08-08): treat the current session's identity (git user `Ayotomiwa`) as owner for Atlas purposes.
- Correction/open item: the repository itself contains four distinct, unreconciled identity strings that a curator should be aware of: README author "Andre Ichiro" (LinkedIn-linked), Dockerfile maintainer label `andreichiro@gmail.com` (`application/Dockerfile`), dbt Cloud run kicked off by `larycampanoo@gmail.com` (`samples/dbt_lineage_manifest_and_docs/run_results.json`), and git session user `Ayotomiwa`. State: user-confirmed (owner assignment) / observed (identity strings) — not reconciled beyond the user's explicit statement.

### Responsibility / boundary — correction

The existing staged/curated pair states responsibility as "process it using Databricks and Spark, and serve insights via LLM and dbt transformations" without flagging that the LLM-serving half is unimplemented. Corrected framing:

- **Observed, implemented responsibility**: extract YouTube video metadata (and separately, transcripts) via two different, non-unified mechanisms; stage/transform via Databricks Spark; model via dbt into intermediate/mart layers.
- **Explicitly NOT implemented** (README describes as "under progress" / future work, and no supporting code exists): LLM fine-tuning, longchain-based inference, or the Django app serving any prediction. `application/apps/alunos/views.py` only renders static templates; `application/apps/alunos/models.py` is empty; no LLM/longchain import or call exists anywhere in `application/`. State: observed (absence of implementation) — this corrects an "observed" claim in the prior staging file that should be `possible`/aspirational at most.

## Evidence

- Repository/path: `data_engineer_end2end` (local clone at `C:\Users\aomop\Desktop\dev-projects\data_engineer_end2end`)
- README/docs: `README.md`; `app_dbt/README.md`; `aws/README.md`; `databricks/README.md`; `handlers-airflow/README.md`
- Build/dependency metadata: `app_dbt/dbt_project.yml`, `app_dbt/packages.yml`, `application/requirements.txt`, `application/Dockerfile`
- Code/config path: `handlers-airflow/airflow-project/dags/youtube_aws_dag.py`; `handlers-airflow/airflow-project/hooks/*`; `handlers-airflow/airflow-project/operators/*`; `handlers-airflow/airflow-project/factories/*`; `aws/lambda.py`; `aws/lambda_kinesis.py`; `application/apps/alunos/views.py`; `application/apps/alunos/models.py`
- Schema/API/event/data-contract path: `app_dbt/models/intermediate/sources.yml` (see linked schema-info evidence `STG-20260808-dbt-hive-source-contract`)
- Infra/template path: `application/infra/*.tf`, `application/env/prod/backend.tf`, `handlers-airflow/infra/*.tf` (see linked infra evidence `STG-20260808-django-ecs-infra` and `STG-20260808-airflow-ec2-infra`)
- Scheduler/workflow definition: `handlers-airflow/airflow-project/dags/youtube_aws_dag.py` (`schedule_interval='0 0 * * 6'`)
- Other: `samples/dbt_lineage_manifest_and_docs/run_results.json` (dbt Cloud execution record: project ID 263221, job ID 370258, run ID 170594209, dbt 1.5.2, run 2023-07-12)

## What is known

### Internal units

| Unit | Type | Purpose/role | Path | Source | State |
|---|---|---|---|---|---|
| `youtube_video_details_dag` | Airflow DAG (scheduled) | Weekly extraction of YouTube video metadata for 4 hardcoded playlists; single task `fetch_and_upload` | `handlers-airflow/airflow-project/dags/youtube_aws_dag.py` | code | observed |
| Hook/Operator/Processor factories | internal design pattern | Pluggable YouTube/AWS hooks, S3 upload operator, pandas/spark output processors | `handlers-airflow/airflow-project/{hooks,operators,factories,processors,abstract_classes}/` | code | observed |
| `lambda.py` | Lambda function | Writes API-Gateway-received JSON payload to S3 under `videos_info/` prefix | `aws/lambda.py` | code | observed |
| `lambda_kinesis.py` | Lambda function | Writes JSON to S3 under `transcripts/` prefix and puts a record to Kinesis stream `JsonChunksStream`; instantiates but never calls a Glue client despite a success message claiming a Glue job started | `aws/lambda_kinesis.py` | code | observed |
| Databricks Spark staging notebook | notebook (exported HTML, not fully parsed — 13.7MB) | Flattens nested/array columns, casts types, renames to camelCase, null/duplicate/NA quality checks | `databricks/*.html`; described in `databricks/README.md` | docs + file existence | observed (description); notebook body not directly parsed |
| dbt intermediate models | dbt models | `dim_channel`, `dim_time_videos`, `dim_transcripts`, `dim_video`, `fact_video_count`, `inter_videos`, `inter_transcripts` | `app_dbt/models/intermediate/*.sql` | code | observed |
| dbt mart models | dbt models | `dim_channels`, `dim_datetime_videos`, `dim_videos`, `fact_comments_per_channel`, `fact_likes_per_channel`, `fact_video_time`, `fact_videos`, `fact_videos_time`, `fact_views_per_channel` | `app_dbt/models/marts/*.sql` | code | observed |
| Django app `alunos` | Django app | Renders static template pages only (index/dashboard/mentor/cursos/perfil/etc.); no DB models, no LLM logic | `application/apps/alunos/{views.py,models.py,urls.py}` | code | observed |
| Standalone extraction notebook | Jupyter notebook | Duplicates Airflow extraction logic outside any orchestrator; writes Delta table to S3 via `getpass()`-prompted AWS credentials | `samples/python_script_without_airflow/video-extraction.ipynb` | code | observed |

### Consumes

| Kind | Name/target | From/source | Evidence | State |
|---|---|---|---|---|
| api | YouTube Data API v3 (`videos().list`, part=snippet,contentDetails,statistics) | Google/YouTube | `handlers-airflow/airflow-project/src/youtube/youtube_video_details.py` | observed |
| api | YouTube Data API v3 (implied — playlist resolution via `pytube.Playlist`) | YouTube | `dags/youtube_aws_dag.py` | observed |
| table (Hive metastore) | `hive_metastore.default.table_flat`, `hive_metastore.default.all_transcripts` | Databricks | `app_dbt/models/intermediate/sources.yml` | observed |
| config | `config/config.json` | local repo | `handlers-airflow/airflow-project/dags/youtube_aws_dag.py` | observed |

### Produces

| Kind | Name/target | Known consumer/use | Evidence | State |
|---|---|---|---|---|
| file (parquet, S3) | `s3://youtube-video-details/video_data/raw/parquet/video_airflow.parquet` | Databricks staging transform (possible — no direct trigger file found) | `handlers-airflow/airflow-project/operators/aws_operator.py` | observed (write); consumer link is possible |
| file (JSON, S3) | `s3://application-kinesis-bucket/videos_info/output-<ts>.json` | Not evidenced — distinct bucket from the Airflow-written data | `aws/lambda.py` | observed (write); no evidenced consumer |
| file (JSON, S3) + Kinesis record | `s3://application-kinesis-bucket/transcripts/output-<ts>.json`; Kinesis stream `JsonChunksStream` | Not evidenced | `aws/lambda_kinesis.py` | observed (write); no evidenced consumer |
| table/parquet | `data/mart/*.parquet` (dbt mart materializations) | data analysts (per README framing only; no consuming code found) | dbt `+materialized: table` config; dir listing `data/mart/` | observed (existence) / possible (consumer) |

### Related flows

| Flow/candidate flow | Role in flow | Evidence | State |
|---|---|---|---|
| Airflow batch extraction → Databricks staging → dbt marts (user-confirmed scope; see `STG-20260808-airflow-batch-flow`) | core scheduled ELT path | DAG + sources.yml + run_results.json | user-confirmed (boundary) / observed (individual steps) |
| Lambda/API-Gateway event ingestion (separate candidate flow, NOT staged as a flow per user decision) | possible parallel ingestion path | `aws/lambda.py`, `aws/lambda_kinesis.py` | possible — explicitly not confirmed to connect to the dbt/Databricks path; different S3 bucket, no linking evidence |

### Related infrastructure

| Package/resource | Relationship to component | Evidence | State |
|---|---|---|---|
| AWS ECS Fargate service `Django-API` + ALB `ECS-Django` + ECR repo `prod` (see `STG-20260808-django-ecs-infra`) | hosts/deploys the Django app | `application/infra/*.tf` | observed |
| AWS EC2 instance + VPC (see `STG-20260808-airflow-ec2-infra`) | hosts the Airflow docker-compose stack | `handlers-airflow/infra/*.tf` | observed |
| S3 buckets `youtube-video-details` and `application-kinesis-bucket` | two distinct, non-unified storage targets | `aws_operator.py`, `lambda.py`, `lambda_kinesis.py` | observed |
| Kinesis stream `JsonChunksStream` | streaming target for transcript path | `lambda_kinesis.py` | observed |
| Databricks S3-ingest CloudFormation custom resource (Databricks-provided quickstart, not custom app code) | possible bridge between S3 and Databricks | `aws/databricks_logs/{connection.txt,trigger.txt}` | possible — no explicit S3 event-notification config found in-repo |

### Local repository references

- Local README/build guidance: `README.md` (root) plus per-directory READMEs listed above
- Test guidance: `handlers-airflow/README.md` documents `python -m unittest discover -s tests`; tests exist at `handlers-airflow/airflow-project/tests/{test_aws_hook.py,test_video_info.py}` but no CI wiring was found to run them (see CI correction below)
- Runtime/deployment guidance: `handlers-airflow/docker-compose.yaml`, `handlers-airflow/playbook.yml` (Ansible), `application/Dockerfile`
- Other stable reference: `app_dbt/dbt_project.yml` (dbt Cloud project config)

### Operational notes

- Root README claims "GitHub Actions ensured compatibility testing of the Django application across multiple operating systems." No `.github/workflows` directory exists anywhere in this repository clone. User was asked and responded "not sure" whether CI exists elsewhere — left as an open, unresolved question rather than staged as fact.
- `handlers-airflow/infra` security group opens ports 8080/22/6379/5555/8974 to `0.0.0.0/0` — broad ingress, noted as an operational/security observation only, not remediated here.
- Sensitive findings (hardcoded API key literal in a committed notebook; an unopened `terraform.tfstate.backup` file that may contain resolved secrets) were surfaced during the scan. Per explicit user instruction, these are reported to the user directly (outside Atlas) rather than recorded here, and no secret values are staged anywhere in this evidence.

### Runbooks, standards and incident learnings

- Runbook evidence/reference: *Not covered* — no operational runbook found.
- Standard/convention evidence/reference: factory + abstract-base-class design pattern is consistently used in `handlers-airflow/airflow-project/` (`factories/`, `abstract_classes/`) — candidate for `atlas-onboard-standards`, not curated here.
- Incident/near-miss learning reference: *Not covered*.

### Other known findings

| Finding | Source | State (`observed` / `user-confirmed`) |
|---|---|---|
| Two ingestion mechanisms write to two different S3 buckets with no evidenced link between them | `aws_operator.py` vs `lambda.py`/`lambda_kinesis.py` | observed |
| README's GitHub Actions CI claim is unconfirmed/possibly stale | `README.md` vs. repo-wide search | observed (claim) / not-covered (actual CI existence) |
| Owner explicitly confirmed by user as session identity (Ayotomiwa) for Atlas purposes | this conversation | user-confirmed |

## What is possible / unconfirmed

| Possible finding/relationship | Why plausible | Evidence needed |
|---|---|---|
| S3 bucket `youtube-video-details` triggers the Databricks staging transform | README claims "S3 triggers were set up to activate the staging layer in Databricks"; Databricks S3-ingest CloudFormation logs exist in this AWS account | An explicit S3 event-notification config or Databricks job/trigger definition referencing this specific bucket |
| `application-kinesis-bucket` / Kinesis stream `JsonChunksStream` feed into the same Databricks/dbt pipeline as the Airflow path | Both eventually claim to reach "the data lakehouse" per README narrative | A config/code artifact tying this bucket or stream to a Databricks job or dbt source |
| dbt mart outputs in `data/mart/*.parquet` are actually consumed by any downstream analyst tooling or the Django app | README framing only | Evidence of a consuming job/dashboard/API |

## Suggested curated targets

- `_curated/components/youtube-pipeline.md` (corrective update to the existing **proposed** page — correct the "serve insights via LLM" responsibility claim, add the internal units/consumes/produces detail above, link the new infra and schema-info evidence)

## Open questions

- Is the GitHub Actions CI claim stale, or does CI exist in a location not visible in this local clone? (user: not sure)
- Does `application-kinesis-bucket`/`JsonChunksStream` actually feed the same lakehouse as the Airflow-written bucket, or is it a genuinely separate, currently-dormant ingestion experiment?
- Should the Django/LLM-serving capability remain listed as a component responsibility at all, given it is unimplemented, or should it move entirely to a roadmap/open-question note?
