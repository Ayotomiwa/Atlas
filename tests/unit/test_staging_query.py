from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json

import yaml

from scripts.atlas_query import main
from scripts.lib.staging import query_staging


def _write_staging(
    root: Path,
    relative: str,
    *,
    record_id: str,
    record_type: str,
    status: str,
    timestamp: str | datetime,
    targets: list[str] | None = None,
    change_source: dict | None = None,
    target_body: str | None = None,
    onboarding_source: dict | None = None,
) -> Path:
    frontmatter = {
        "id": record_id,
        "type": record_type,
        "package": "fixtures",
        "timestamp": timestamp,
        "title": f"Title for {record_id}",
        "description": f"Description for {record_id}",
        "status": status,
        "captured_by": "Fixture Author",
        "source_type": "merged-change" if change_source else "repository",
    }
    if change_source is not None:
        frontmatter["change_source"] = change_source
    if onboarding_source is not None:
        frontmatter["onboarding_source"] = onboarding_source
    if target_body is None:
        bullets = "\n".join(f"- `{target}`" for target in targets or []) or "None recorded."
        target_body = f"## Suggested curated targets\n\n{bullets}\n\n## Open questions\n"
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        + yaml.safe_dump(frontmatter, sort_keys=False)
        + "---\n\n# Evidence\n\n"
        + target_body,
        encoding="utf-8",
    )
    return path


def _fixture(root: Path) -> dict:
    change_source = {
        "source_key": "datalens-monorepo",
        "branch": "main",
        "commit_range": {
            "from_exclusive": "a" * 40,
            "through_inclusive": "b" * 40,
        },
        "merge_requests": [{"id": "1420", "merged_commit": "b" * 40}],
    }
    _write_staging(
        root,
        "_staging/components/payments/STG-20260810-payments.md",
        record_id="STG-20260810-payments",
        record_type="staging.component",
        status="new",
        timestamp="2026-08-10",
        targets=["comp.payments-api"],
    )
    _write_staging(
        root,
        "_staging/flows/orders/STG-20260809-order-flow.md",
        record_id="STG-20260809-order-flow",
        record_type="staging.flow",
        status="curating",
        timestamp="2026-08-09",
        targets=["_curated/flows/orders/order-flow.md"],
    )
    _write_staging(
        root,
        "_staging/changes/STG-20260811-merged-change.md",
        record_id="STG-20260811-merged-change",
        record_type="staging.change",
        status="consumed",
        timestamp="2026-08-11",
        targets=["comp.payments-api"],
        change_source=change_source,
    )
    _write_staging(
        root,
        "_staging/runbooks/STG-20260808-old-runbook.md",
        record_id="STG-20260808-old-runbook",
        record_type="staging.runbook",
        status="rejected",
        timestamp="2026-08-08",
        targets=[],
    )
    return change_source


def _write_curated(
    root: Path,
    relative: str,
    record_id: str,
    *,
    record_type: str = "component",
    extra: dict | None = None,
) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    frontmatter = {"id": record_id, "type": record_type, "status": "curated"}
    frontmatter.update(extra or {})
    path.write_text(
        "---\n"
        + yaml.safe_dump(frontmatter, sort_keys=False)
        + "---\n",
        encoding="utf-8",
    )


def test_staging_defaults_to_active_records_across_buckets(tmp_path: Path):
    _fixture(tmp_path)

    payload = query_staging(tmp_path)

    assert [record["id"] for record in payload["results"]] == [
        "STG-20260809-order-flow",
        "STG-20260810-payments",
    ]
    assert payload["results"][0]["suggested_targets"] == [
        "_curated/flows/orders/order-flow.md"
    ]
    component = payload["results"][1]
    assert component == {
        "id": "STG-20260810-payments",
        "type": "staging.component",
        "bucket": "components",
        "title": "Title for STG-20260810-payments",
        "description": "Description for STG-20260810-payments",
        "status": "new",
        "timestamp": "2026-08-10",
        "captured_by": "Fixture Author",
        "source_type": "repository",
        "candidate_domain": "payments",
        "suggested_targets": ["comp.payments-api"],
        "change_source": None,
        "onboarding_source": None,
        "page": "_staging/components/payments/STG-20260810-payments.md",
    }


def test_staging_status_terminal_and_change_provenance(tmp_path: Path):
    expected_change_source = _fixture(tmp_path)

    terminal = query_staging(tmp_path, statuses=["consumed"])
    assert [record["id"] for record in terminal["results"]] == [
        "STG-20260811-merged-change"
    ]
    assert terminal["results"][0]["candidate_domain"] == ""
    assert terminal["results"][0]["change_source"] == expected_change_source

    all_records = query_staging(tmp_path, include_terminal=True)
    assert len(all_records["results"]) == 4

    # Explicit statuses replace the default even when --include-terminal is present.
    explicit = query_staging(
        tmp_path, statuses=["rejected"], include_terminal=True
    )
    assert [record["status"] for record in explicit["results"]] == ["rejected"]


def test_staging_exposes_onboarding_provenance_and_infra_candidate_domain(tmp_path: Path, capsys):
    _write_staging(
        tmp_path,
        "_staging/infra/platform/STG-20260820-infra.md",
        record_id="STG-20260820-infra",
        record_type="staging.infra",
        status="new",
        timestamp="2026-08-20",
        onboarding_source={"campaign_id": "fixture-portfolio", "item_id": "platform"},
    )

    payload = query_staging(tmp_path)

    assert payload["results"][0]["candidate_domain"] == "platform"
    assert payload["results"][0]["onboarding_source"] == {
        "campaign_id": "fixture-portfolio", "item_id": "platform"
    }
    assert main(["--root", str(tmp_path), "staging"]) == 0
    assert "onboarding=fixture-portfolio/platform" in capsys.readouterr().out


def test_staging_filters_are_and_across_kinds_and_or_within_kind(tmp_path: Path):
    _fixture(tmp_path)

    selected = query_staging(
        tmp_path,
        statuses=["new", "curating"],
        buckets=["components", "flows"],
        domain="payments",
        timestamp="2026-08-10",
        targets=["comp.missing", "comp.payments-api"],
    )

    assert [record["id"] for record in selected["results"]] == [
        "STG-20260810-payments"
    ]
    assert selected["filters"]["targets"] == [
        "comp.missing",
        "comp.payments-api",
    ]


def test_staging_filters_exact_change_provenance_and_composes_with_existing_filters(
    tmp_path: Path,
):
    change_source = _fixture(tmp_path)
    _write_staging(
        tmp_path,
        "_staging/changes/STG-20260812-same-range.md",
        record_id="STG-20260812-same-range",
        record_type="staging.change",
        status="new",
        timestamp="2026-08-12",
        targets=["comp.payments-api"],
        change_source=change_source,
    )
    differing_sources = {
        "different-source": {**change_source, "source_key": "other-source"},
        "different-branch": {**change_source, "branch": "release"},
        "different-from": {
            **change_source,
            "commit_range": {
                **change_source["commit_range"],
                "from_exclusive": "c" * 40,
            },
        },
        "different-through": {
            **change_source,
            "commit_range": {
                **change_source["commit_range"],
                "through_inclusive": "d" * 40,
            },
        },
    }
    for suffix, record_source in differing_sources.items():
        _write_staging(
            tmp_path,
            f"_staging/changes/STG-20260812-{suffix}.md",
            record_id=f"STG-20260812-{suffix}",
            record_type="staging.change",
            status="new",
            timestamp="2026-08-12",
            targets=["comp.payments-api"],
            change_source=record_source,
        )

    selected = query_staging(
        tmp_path,
        source_key=" datalens-monorepo ",
        branch=" main ",
        from_exclusive="a" * 40,
        through_inclusive="b" * 40,
        buckets=["changes"],
        targets=["comp.payments-api"],
        include_terminal=True,
    )

    assert [record["id"] for record in selected["results"]] == [
        "STG-20260811-merged-change",
        "STG-20260812-same-range",
    ]
    assert selected["filters"] == {
        "statuses": sorted({"new", "curating", "consumed", "no-change", "deferred", "rejected"}),
        "buckets": ["changes"],
        "domain": None,
        "date": None,
        "targets": ["comp.payments-api"],
        "include_terminal": True,
        "source_key": "datalens-monorepo",
        "branch": "main",
        "from_exclusive": "a" * 40,
        "through_inclusive": "b" * 40,
    }

    selectors = {
        "source_key": "datalens-monorepo",
        "branch": "main",
        "from_exclusive": "a" * 40,
        "through_inclusive": "b" * 40,
        "include_terminal": True,
    }
    independently_selected = {
        key: [
            record["id"]
            for record in query_staging(
                tmp_path,
                **{name: value for name, value in selectors.items() if name != key},
            )["results"]
        ]
        for key in ("source_key", "branch", "from_exclusive", "through_inclusive")
    }
    assert independently_selected == {
        "source_key": [
            "STG-20260811-merged-change",
            "STG-20260812-different-source",
            "STG-20260812-same-range",
        ],
        "branch": [
            "STG-20260811-merged-change",
            "STG-20260812-different-branch",
            "STG-20260812-same-range",
        ],
        "from_exclusive": [
            "STG-20260811-merged-change",
            "STG-20260812-different-from",
            "STG-20260812-same-range",
        ],
        "through_inclusive": [
            "STG-20260811-merged-change",
            "STG-20260812-different-through",
            "STG-20260812-same-range",
        ],
    }

    source_only = query_staging(
        tmp_path, source_key="datalens-monorepo", include_terminal=True
    )
    assert [record["id"] for record in source_only["results"]] == [
        "STG-20260811-merged-change",
        "STG-20260812-different-branch",
        "STG-20260812-different-from",
        "STG-20260812-different-through",
        "STG-20260812-same-range",
    ]


def test_staging_change_provenance_start_matches_only_null_from_exclusive(tmp_path: Path):
    _fixture(tmp_path)
    _write_staging(
        tmp_path,
        "_staging/changes/STG-20260812-from-start.md",
        record_id="STG-20260812-from-start",
        record_type="staging.change",
        status="new",
        timestamp="2026-08-12",
        change_source={
            "source_key": "datalens-monorepo",
            "branch": "main",
            "commit_range": {
                "from_exclusive": None,
                "through_inclusive": "c" * 40,
            },
            "merge_requests": [],
        },
    )
    _write_staging(
        tmp_path,
        "_staging/changes/STG-20260812-missing-from.md",
        record_id="STG-20260812-missing-from",
        record_type="staging.change",
        status="new",
        timestamp="2026-08-12",
        change_source={
            "source_key": "datalens-monorepo",
            "branch": "main",
            "commit_range": {"through_inclusive": "c" * 40},
            "merge_requests": [],
        },
    )

    selected = query_staging(
        tmp_path,
        source_key="datalens-monorepo",
        from_exclusive="start",
        through_inclusive="c" * 40,
    )

    assert [record["id"] for record in selected["results"]] == [
        "STG-20260812-from-start"
    ]
    assert selected["filters"]["from_exclusive"] == "start"


def test_staging_change_provenance_accepts_exact_64_character_hashes(tmp_path: Path):
    from_sha = "c" * 64
    through_sha = "d" * 64
    _write_staging(
        tmp_path,
        "_staging/changes/STG-20260812-sha256-range.md",
        record_id="STG-20260812-sha256-range",
        record_type="staging.change",
        status="new",
        timestamp="2026-08-12",
        change_source={
            "source_key": "datalens-monorepo",
            "branch": "main",
            "commit_range": {
                "from_exclusive": from_sha,
                "through_inclusive": through_sha,
            },
            "merge_requests": [],
        },
    )

    selected = query_staging(
        tmp_path,
        source_key="datalens-monorepo",
        branch="main",
        from_exclusive=from_sha,
        through_inclusive=through_sha,
    )

    assert [record["id"] for record in selected["results"]] == [
        "STG-20260812-sha256-range"
    ]


def test_staging_change_provenance_filter_validation(tmp_path: Path):
    _fixture(tmp_path)

    for kwargs, message in [
        ({"source_key": "Bad_Source"}, "source-key"),
        ({"branch": "   "}, "branch"),
        ({"from_exclusive": "a" * 39}, "from-exclusive"),
        ({"from_exclusive": "A" * 40}, "from-exclusive"),
        ({"from_exclusive": "g" * 64}, "from-exclusive"),
        ({"through_inclusive": "start"}, "through-inclusive"),
        ({"through_inclusive": "not-a-sha"}, "through-inclusive"),
        ({"through_inclusive": "g" * 64}, "through-inclusive"),
    ]:
        try:
            query_staging(tmp_path, **kwargs)
        except ValueError as exc:
            assert message in str(exc)
        else:
            raise AssertionError(f"expected ValueError for {kwargs}")


def test_target_filter_resolves_curated_id_and_page_both_ways(tmp_path: Path):
    curated_page = "_curated/components/payments/payments-api.md"
    _write_curated(tmp_path, curated_page, "comp.payments-api")
    _write_staging(
        tmp_path,
        "_staging/changes/STG-20260811-by-page.md",
        record_id="STG-20260811-by-page",
        record_type="staging.change",
        status="new",
        timestamp="2026-08-11",
        targets=[curated_page],
    )
    _write_staging(
        tmp_path,
        "_staging/changes/STG-20260811-by-id.md",
        record_id="STG-20260811-by-id",
        record_type="staging.change",
        status="new",
        timestamp="2026-08-11",
        targets=["comp.payments-api"],
    )
    unresolved = "_curated/components/payments/not-created-yet.md"
    _write_staging(
        tmp_path,
        "_staging/changes/STG-20260811-unresolved.md",
        record_id="STG-20260811-unresolved",
        record_type="staging.change",
        status="new",
        timestamp="2026-08-11",
        targets=[unresolved],
    )

    expected = ["STG-20260811-by-id", "STG-20260811-by-page"]
    assert [item["id"] for item in query_staging(
        tmp_path, targets=["comp.payments-api"]
    )["results"]] == expected
    assert [item["id"] for item in query_staging(
        tmp_path, targets=[curated_page]
    )["results"]] == expected
    assert [item["id"] for item in query_staging(
        tmp_path, targets=[unresolved]
    )["results"]] == ["STG-20260811-unresolved"]


def test_target_filter_aliases_embedded_ids_to_owning_page_without_merging_siblings(
    tmp_path: Path,
):
    infra_page = "_curated/infra/payments/platform.md"
    _write_curated(
        tmp_path,
        infra_page,
        "infra.payments-platform",
        record_type="infra",
        extra={
            "promoted_resources": [
                {"id": "resource.payments-bucket"},
                {"id": "resource.payments-queue"},
            ]
        },
    )
    schema_page = "_curated/schema-info/payments/events.md"
    _write_curated(
        tmp_path,
        schema_page,
        "schema.payment-events",
        record_type="schema-info",
        extra={"assets": [{"id": "asset.payment-created"}]},
    )
    records = [
        ("resource-id", "resource.payments-bucket"),
        ("resource-page", infra_page),
        ("resource-sibling", "resource.payments-queue"),
        ("asset-id", "asset.payment-created"),
        ("asset-page", schema_page),
    ]
    for suffix, target in records:
        _write_staging(
            tmp_path,
            f"_staging/changes/STG-20260811-{suffix}.md",
            record_id=f"STG-20260811-{suffix}",
            record_type="staging.change",
            status="new",
            timestamp="2026-08-11",
            targets=[target],
        )

    assert [item["id"] for item in query_staging(
        tmp_path, targets=["resource.payments-bucket"]
    )["results"]] == [
        "STG-20260811-resource-id",
        "STG-20260811-resource-page",
    ]
    assert [item["id"] for item in query_staging(
        tmp_path, targets=[schema_page]
    )["results"]] == [
        "STG-20260811-asset-id",
        "STG-20260811-asset-page",
    ]


def test_date_filter_uses_calendar_date_and_preserves_datetime_timestamp(
    tmp_path: Path,
):
    observed = datetime(2026, 8, 11, 23, 45, tzinfo=timezone.utc)
    _write_staging(
        tmp_path,
        "_staging/changes/STG-20260811-timestamp.md",
        record_id="STG-20260811-timestamp",
        record_type="staging.change",
        status="new",
        timestamp=observed,
        targets=[],
    )

    payload = query_staging(tmp_path, timestamp="2026-08-11")

    assert [item["id"] for item in payload["results"]] == [
        "STG-20260811-timestamp"
    ]
    assert payload["results"][0]["timestamp"] == "2026-08-11T23:45:00+00:00"
    assert query_staging(tmp_path, timestamp="2026-08-10")["results"] == []


def test_staging_reports_target_shape_and_duplicate_id_diagnostics(tmp_path: Path):
    malformed = (
        "## Suggested curated targets\n\n"
        "- maybe update the relevant component\n\n"
        "## Open questions\n"
    )
    for bucket in ("changes", "infra"):
        _write_staging(
            tmp_path,
            f"_staging/{bucket}/STG-20260811-duplicate.md",
            record_id="STG-20260811-duplicate",
            record_type=f"staging.{bucket.removesuffix('s')}",
            status="new",
            timestamp="2026-08-11",
            target_body=malformed,
        )

    payload = query_staging(tmp_path)

    assert len(payload["results"]) == 2
    assert sum(item["kind"] == "duplicate-id" for item in payload["diagnostics"]) == 1
    assert sum(item["kind"] == "suggested-targets" for item in payload["diagnostics"]) == 2
    assert all(item["page"].startswith("_staging/") for item in payload["diagnostics"])


def test_non_mapping_frontmatter_and_unknown_bucket_are_diagnosed_and_excluded(
    tmp_path: Path,
):
    non_mapping = tmp_path / "_staging/changes/STG-20260811-list.md"
    non_mapping.parent.mkdir(parents=True)
    non_mapping.write_text(
        "---\n- this\n- is-not-a-mapping\n---\n\n## Suggested curated targets\n",
        encoding="utf-8",
    )
    _write_staging(
        tmp_path,
        "_staging/misc/STG-20260811-unknown.md",
        record_id="STG-20260811-unknown",
        record_type="staging.change",
        status="new",
        timestamp="2026-08-11",
        targets=["comp.example"],
    )

    payload = query_staging(tmp_path)

    assert payload["results"] == []
    assert {(item["kind"], item["page"]) for item in payload["diagnostics"]} == {
        ("frontmatter", "_staging/changes/STG-20260811-list.md"),
        ("unknown-bucket", "_staging/misc/STG-20260811-unknown.md"),
    }


def test_suggested_target_parser_ignores_fences_and_multiline_comments(tmp_path: Path):
    target_body = """<!--
## Suggested curated targets

- `comp.from-comment`
-->

```markdown
## Suggested curated targets

- `comp.from-fence`
```

## Suggested curated targets

- `comp.real`

## Open questions
"""
    _write_staging(
        tmp_path,
        "_staging/changes/STG-20260811-markdown-examples.md",
        record_id="STG-20260811-markdown-examples",
        record_type="staging.change",
        status="new",
        timestamp="2026-08-11",
        target_body=target_body,
    )

    payload = query_staging(tmp_path)

    assert payload["results"][0]["suggested_targets"] == ["comp.real"]
    assert payload["diagnostics"] == []


def test_staging_cli_json_and_empty_human_result(tmp_path: Path, capsys):
    _fixture(tmp_path)

    exit_code = main(
        [
            "--root",
            str(tmp_path),
            "staging",
            "--status",
            "consumed",
            "--format",
            "json",
        ]
    )
    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["command"] == "staging"
    assert output["results"][0]["id"] == "STG-20260811-merged-change"

    exit_code = main(
        ["--root", str(tmp_path), "staging", "--status", "consumed"]
    )
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "type=staging.change" in output
    assert "captured_by=Fixture Author" in output
    assert "Change source: source=datalens-monorepo; branch=main" in output
    assert "range=aaaaaaaaaaaa..bbbbbbbbbbbb; MRs=1420" in output

    exit_code = main(
        ["--root", str(tmp_path), "staging", "--domain", "not-present"]
    )
    output = capsys.readouterr().out.strip()
    assert exit_code == 0
    assert output == "No matching staging records were found."


def test_staging_cli_filters_exact_change_provenance(tmp_path: Path, capsys):
    _fixture(tmp_path)

    exit_code = main(
        [
            "--root",
            str(tmp_path),
            "staging",
            "--source-key",
            "  datalens-monorepo  ",
            "--branch",
            "  main  ",
            "--from-exclusive",
            f"  {'a' * 40}  ",
            "--through-inclusive",
            f"  {'b' * 40}  ",
            "--include-terminal",
            "--format",
            "json",
        ]
    )
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert [record["id"] for record in output["results"]] == [
        "STG-20260811-merged-change"
    ]
    assert output["filters"]["source_key"] == "datalens-monorepo"
    assert output["filters"]["branch"] == "main"
    assert output["filters"]["from_exclusive"] == "a" * 40
    assert output["filters"]["through_inclusive"] == "b" * 40


def test_staging_cli_accepts_padded_64_character_hashes(tmp_path: Path, capsys):
    from_sha = "c" * 64
    through_sha = "d" * 64
    _write_staging(
        tmp_path,
        "_staging/changes/STG-20260812-cli-sha256.md",
        record_id="STG-20260812-cli-sha256",
        record_type="staging.change",
        status="new",
        timestamp="2026-08-12",
        change_source={
            "source_key": "datalens-monorepo",
            "branch": "main",
            "commit_range": {
                "from_exclusive": from_sha,
                "through_inclusive": through_sha,
            },
            "merge_requests": [],
        },
    )

    exit_code = main(
        [
            "--root",
            str(tmp_path),
            "staging",
            "--source-key",
            " datalens-monorepo ",
            "--branch",
            " main ",
            "--from-exclusive",
            f" {from_sha} ",
            "--through-inclusive",
            f" {through_sha} ",
            "--format",
            "json",
        ]
    )
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert [record["id"] for record in output["results"]] == [
        "STG-20260812-cli-sha256"
    ]
    assert output["filters"]["source_key"] == "datalens-monorepo"
    assert output["filters"]["branch"] == "main"
    assert output["filters"]["from_exclusive"] == from_sha
    assert output["filters"]["through_inclusive"] == through_sha


def test_staging_rejects_unknown_filters_and_invalid_date(tmp_path: Path, capsys):
    _fixture(tmp_path)

    assert main(
        ["--root", str(tmp_path), "staging", "--status", "curated"]
    ) == 1
    assert "unknown staging status: curated" in capsys.readouterr().out

    assert main(
        ["--root", str(tmp_path), "staging", "--date", "2026-02-30"]
    ) == 1
    assert "valid ISO YYYY-MM-DD date" in capsys.readouterr().out

    for flag, value, message in [
        ("--source-key", "Bad_Source", "source-key"),
        ("--branch", "   ", "branch"),
        ("--from-exclusive", "a" * 39, "from-exclusive"),
        ("--from-exclusive", "A" * 40, "from-exclusive"),
        ("--from-exclusive", "g" * 64, "from-exclusive"),
        ("--through-inclusive", "start", "through-inclusive"),
        ("--through-inclusive", "b" * 39, "through-inclusive"),
        ("--through-inclusive", "g" * 64, "through-inclusive"),
    ]:
        assert main(["--root", str(tmp_path), "staging", flag, value]) == 1
        assert message in capsys.readouterr().out


def test_staging_query_retrieves_component_and_flow_records_by_domain(tmp_path: Path):
    """The staging command is the queue interface for both former catalogue buckets."""
    _fixture(tmp_path)

    components = query_staging(tmp_path, buckets=["components"], domain="payments")
    flows = query_staging(tmp_path, buckets=["flows"], domain="orders")

    assert [record["id"] for record in components["results"]] == ["STG-20260810-payments"]
    assert [record["id"] for record in flows["results"]] == ["STG-20260809-order-flow"]
