from __future__ import annotations

from pathlib import Path
import json
import shutil

import yaml

from scripts.atlas_lint import lint_repository

ROOT = Path(__file__).resolve().parents[2]


def _root(tmp_path: Path) -> Path:
    shutil.copytree(ROOT / "taxonomy", tmp_path / "taxonomy")
    shutil.copytree(ROOT / "contracts", tmp_path / "contracts")
    manifest = {
        "schema_version": "atlas-package/1.0",
        "id": "package.fixtures",
        "type": "package",
        "package": "fixtures",
        "title": "Fixture Atlas",
        "description": "Synthetic validation fixture.",
        "status": "active",
        "owners": {},
        "aliases": ["fixtures"],
        "domains": [
            {
                "id": "test",
                "title": "Test",
                "aliases": [],
                "routing_description": "Synthetic test records.",
            }
        ],
        "entrypoints": {"root": "index.md"},
        "maps": {
            "flow_component": "_curated/maps/flow-component/flow-component-map.json",
            "repository_component": "_curated/maps/repository-component/repository-component-map.json",
            "infra_dependency": "_curated/maps/infra-dependency/infra-dependency-map.json",
        },
        "taxonomy": {
            "types": "taxonomy/types.yaml",
            "statuses": "taxonomy/statuses.yaml",
            "standard_categories": "taxonomy/standard-categories.yaml",
            "concept_fields": "taxonomy/concept-fields.yaml",
        },
        "contracts": {"map_fields": "contracts/map-fields.yaml"},
    }
    (tmp_path / "atlas-package.json").write_text(json.dumps(manifest), encoding="utf-8")
    return tmp_path


def _common(identifier: str, typ: str) -> dict:
    return {
        "id": identifier,
        "type": typ,
        "package": "fixtures",
        "schema_version": "atlas/1.0",
        "title": identifier,
        "description": "Synthetic record.",
        "status": "curated",
        "last_reviewed": "2026-08-11",
        "reviewed_by": ["Fixture Curator"],
        "owners": [],
        "routing": {"aliases": []},
        "evidence": ["fixture://record"],
        "coverage": {"level": "partial", "notes": []},
    }


def _repository(identifier: str, parent: str | None = None) -> dict:
    return {
        **_common(identifier, "repository"),
        "primary_domain": "test",
        "related_domains": [],
        "repository_locator": "https://example.invalid/repository",
        "repository_root": ".",
        "repository_type": "standalone",
        "default_branch": "main",
        "parent_repository": parent,
        "source_roots": [],
        "depends_on_repositories": [],
        "runbooks": [],
        "standards": [],
        "incident_learnings": [],
    }


def _write(root: Path, relative: str, frontmatter: dict, body: str = "") -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = "---\n" + yaml.safe_dump(frontmatter, sort_keys=False) + "---\n\n" + body
    path.write_text(rendered, encoding="utf-8")
    return path


def _codes(issues: list[dict[str, str]]) -> set[str]:
    return {item["code"] for item in issues}


def test_lint_accepts_current_frontmatter_and_relative_links(tmp_path: Path):
    root = _root(tmp_path)
    _write(root, "_curated/repositories/test/repo.md", _repository("repo.fixture"))
    (root / "notes.md").write_text(
        "[Repository](_curated/repositories/test/repo.md)\n", encoding="utf-8"
    )

    assert lint_repository(root) == []


def test_lint_reports_frontmatter_trust_and_broken_links(tmp_path: Path):
    root = _root(tmp_path)
    record = _repository("repo.fixture")
    record.update({"package": "wrong", "status": "curated", "reviewed_by": [], "evidence": []})
    _write(root, "_curated/repositories/test/repo.md", record)
    (root / "notes.md").write_text("[Missing](missing.md)\n", encoding="utf-8")

    assert {"ATLAS004", "ATLAS007", "ATLAS008"} <= _codes(lint_repository(root))


def test_lint_validates_restored_schema_and_incident_scalars(tmp_path: Path):
    root = _root(tmp_path)
    schema = {
        **_common("schema.fixture", "schema-info"),
        "primary_domain": "test",
        "related_domains": [],
        "links": [],
        "asset_type": "schema",
        "physical_name": "fixture.records",
        "platform": "fixture-platform",
        "temporal_model": "append-only",
        "classification": "internal",
    }
    incident = {
        **_common("incident.fixture", "incident-learning"),
        "links": [],
        "incident_date": "2026-08-10",
        "source_severity": "SEV-3",
    }
    _write(root, "_curated/schema-info/test/schema.md", schema)
    _write(root, "_curated/incidents/incident.md", incident)
    assert "ATLAS025" not in _codes(lint_repository(root))

    incident["incident_date"] = "10 August"
    _write(root, "_curated/incidents/incident.md", incident)
    assert "ATLAS025" in _codes(lint_repository(root))


def test_structured_errors_are_attributed_to_owning_pages(tmp_path: Path):
    root = _root(tmp_path)
    infra = {
        **_common("infra.fixture", "infra"),
        "primary_domain": "test",
        "related_domains": [],
        "infra_package": "fixture",
        "repository": None,
        "package_path": "",
        "template_path": "infra/main.tf",
        "environments": [],
        "depends_on": [],
        "uses_resources": [],
        "reads_from": [],
        "writes_to": [],
        "triggers": [],
        "scheduled_by": [],
        "imports_values": [],
        "exports_values": [],
        "permissions": [],
        "monitored_by": [],
        "deployed_by": [],
        "promoted_resources": "not-a-list",
        "runbooks": [],
        "standards": [],
        "incident_learnings": [],
    }
    _write(root, "_curated/infra/test/infra.md", infra)
    _write(root, "_curated/repositories/test/a.md", _repository("repo.a", "repo.b"))
    _write(root, "_curated/repositories/test/b.md", _repository("repo.b", "repo.a"))

    issues = [item for item in lint_repository(root) if item["code"] == "ATLAS009"]
    assert any(item["path"].endswith("infra.md") and "promoted_resources" in item["message"] for item in issues)
    cycle_issues = [item for item in issues if "hierarchy contains cycle" in item["message"]]
    assert len(cycle_issues) == 1
    assert "repo.a -> repo.b -> repo.a" in cycle_issues[0]["message"]


def test_duplicate_issue_exposes_record_and_related_path_metadata(tmp_path: Path):
    root = _root(tmp_path)
    _write(root, "_curated/repositories/test/first.md", _repository("repo.fixture"))
    _write(root, "_curated/repositories/test/second.md", _repository("repo.fixture"))

    duplicate = next(
        item
        for item in lint_repository(root)
        if item["code"] == "ATLAS003" and "duplicate" in item["message"]
    )

    assert duplicate["record_id"] == "repo.fixture"
    assert duplicate["related_ids"] == ["repo.fixture"]
    assert duplicate["related_paths"] == ["_curated/repositories/test/first.md"]


def test_body_shape_secrets_and_review_age_are_not_lint_rules(tmp_path: Path):
    root = _root(tmp_path)
    record = _repository("repo.fixture")
    record["last_reviewed"] = "2020-01-01"
    body = "No prescribed headings.\n\n| Wrong | Question | Table |\n\npassword=abcdefghijklmnopqrstuvwxyz\n"
    _write(root, "_curated/repositories/test/repo.md", record, body)

    assert lint_repository(root) == []


def test_lifecycle_and_candidate_staging_domain_rules(tmp_path: Path):
    root = _root(tmp_path)
    record = _repository("repo.fixture")
    record["status"] = "proposed"
    _write(root, "_curated/repositories/test/repo.md", record)
    staging = {
        "id": "STG-20260811-candidate",
        "type": "staging.component",
        "package": "fixtures",
        "timestamp": "2026-08-11",
        "title": "Candidate",
        "description": "Evidence.",
        "status": "consumed",
        "captured_by": "Fixture Curator",
        "source_type": "repository",
    }
    _write(root, "_staging/components/not-yet-registered/STG-20260811-candidate.md", staging)
    issues = lint_repository(root)
    assert any(item["code"] == "ATLAS006" and "proposed" in item["message"] for item in issues)
    assert not any(item["code"] == "ATLAS027" and "not-yet-registered" in item["path"] for item in issues)


def test_domain_grouped_staging_error_names_the_actual_type(tmp_path: Path):
    root = _root(tmp_path)
    staging = {
        "id": "STG-20260817-infra",
        "type": "staging.infra",
        "package": "fixtures",
        "timestamp": "2026-08-17",
        "title": "Infrastructure evidence",
        "description": "Evidence.",
        "status": "new",
        "captured_by": "Fixture Curator",
        "source_type": "repository",
    }
    _write(root, "_staging/infra/Bad Group/STG-20260817-infra.md", staging)

    issues = [item for item in lint_repository(root) if item["code"] == "ATLAS027"]

    assert any("staging.infra must be under" in item["message"] for item in issues), issues
    assert all("component/flow" not in item["message"] for item in issues)


def test_domain_grouped_staging_rejects_flat_and_excessively_nested_paths(tmp_path: Path):
    root = _root(tmp_path)
    common = {
        "package": "fixtures",
        "timestamp": "2026-08-17",
        "title": "Evidence",
        "description": "Evidence.",
        "status": "new",
        "captured_by": "Fixture Curator",
        "source_type": "repository",
    }
    _write(
        root,
        "_staging/components/test/nested/STG-20260817-component.md",
        {**common, "id": "STG-20260817-component", "type": "staging.component"},
    )
    _write(
        root,
        "_staging/infra/test/nested/STG-20260817-infra-nested.md",
        {**common, "id": "STG-20260817-infra-nested", "type": "staging.infra"},
    )
    _write(
        root,
        "_staging/infra/STG-20260817-infra-flat.md",
        {**common, "id": "STG-20260817-infra-flat", "type": "staging.infra"},
    )

    issues = [item for item in lint_repository(root) if item["code"] == "ATLAS027"]

    assert {item["path"] for item in issues} == {
        "_staging/components/test/nested/STG-20260817-component.md",
        "_staging/infra/STG-20260817-infra-flat.md",
        "_staging/infra/test/nested/STG-20260817-infra-nested.md",
    }
    assert all("exactly <candidate-domain>/<staging-id>.md" in item["message"] for item in issues)


def test_unquoted_transition_key_has_actionable_error(tmp_path: Path):
    root = _root(tmp_path)
    flow = {
        **_common("flow.fixture", "flow"),
        "primary_domain": "test",
        "related_domains": [],
        "flow_scope": "test",
        "diagram": False,
        "entry_points": [],
        "inputs": [],
        "outputs": [],
        "upstream_flows": [],
        "steps": [{
            "step_id": "start",
            "order": 10,
            "name": "Start",
            "participant": {"type": "manual", "name": "Operator"},
            "role": "trigger",
            "confidence": "reviewed",
            "evidence": ["fixture://flow"],
            "transitions": [{"to": "end", True: "success"}],
        }, {
            "step_id": "end",
            "order": 20,
            "name": "End",
            "participant": {"type": "manual", "name": "Operator"},
            "role": "finish",
            "confidence": "reviewed",
            "evidence": ["fixture://flow"],
        }],
        "runbooks": [],
        "standards": [],
        "incident_learnings": [],
    }
    _write(root, "_curated/flows/test/flow.md", flow)
    issues = lint_repository(root)
    assert any('quote the reserved YAML key "on"' in item["message"] for item in issues)


def _merged_change(identifier: str = "STG-20260811-merged-change") -> dict:
    return {
        "id": identifier,
        "type": "staging.change",
        "package": "fixtures",
        "timestamp": "2026-08-11",
        "title": "Merged change",
        "description": "Evidence captured from a merged change.",
        "status": "new",
        "captured_by": "Fixture Curator",
        "source_type": "merged-change",
        "change_source": {
            "source_key": "fixture-monorepo",
            "branch": "main",
            "commit_range": {
                "from_exclusive": "1" * 40,
                "through_inclusive": "a" * 40,
            },
            "merge_requests": [{"id": "1420", "merged_commit": "a" * 40}],
        },
    }


def _intake_checkpoint(staging_id: str = "STG-20260811-merged-change") -> dict:
    return {
        "schema_version": "atlas-intake/1.0",
        "source": {
            "key": "fixture-monorepo",
            "locator": "https://example.invalid/fixture.git",
            "default_branch": "main",
        },
        "observed_through": {"commit": "a" * 40, "merge_request": "1420"},
        "considered_through": {"commit": "a" * 40, "merge_request": "1420"},
        "last_run": {
            "from_exclusive": "1" * 40,
            "through_inclusive": "a" * 40,
            "dispositions": [{
                "change_key": "mr:1420",
                "commit": "a" * 40,
                "merge_request": "1420",
                "outcome": "staged",
                "staging_ids": [staging_id],
            }],
        },
        "unresolved": [],
        "updated_at": "2026-08-11T12:30:00+00:00",
        "updated_by": "Fixture Curator",
    }


def test_lint_accepts_merged_change_provenance_and_checkpoint_join(tmp_path: Path):
    root = _root(tmp_path)
    change = _merged_change()
    _write(root, f"_staging/changes/{change['id']}.md", change)
    checkpoint = root / "_intake/checkpoints/fixture-monorepo.json"
    checkpoint.parent.mkdir(parents=True)
    checkpoint.write_text(json.dumps(_intake_checkpoint()), encoding="utf-8")

    assert lint_repository(root) == []


def test_lint_requires_and_validates_merged_change_provenance(tmp_path: Path):
    root = _root(tmp_path)
    change = _merged_change()
    del change["change_source"]
    _write(root, f"_staging/changes/{change['id']}.md", change)

    issues = lint_repository(root)
    assert any(
        item["code"] == "ATLAS025" and "change_source is required" in item["message"]
        for item in issues
    )

    change["change_source"] = {
        "source_key": "fixture-monorepo",
        "branch": "main",
        "commit_range": {"from_exclusive": None, "through_inclusive": "ABC"},
        "merge_requests": [
            {"id": "1420", "merged_commit": "a" * 40},
            {"id": "1420", "merged_commit": "b" * 40},
        ],
    }
    _write(root, f"_staging/changes/{change['id']}.md", change)
    messages = [item["message"] for item in lint_repository(root) if item["code"] == "ATLAS025"]
    assert any("through_inclusive" in item and "lowercase hexadecimal" in item for item in messages)
    assert any("duplicate id 1420" in item for item in messages)


def test_lint_attributes_checkpoint_schema_and_join_errors(tmp_path: Path):
    root = _root(tmp_path)
    checkpoint = root / "_intake/checkpoints/wrong-name.json"
    checkpoint.parent.mkdir(parents=True)
    checkpoint.write_text(json.dumps(_intake_checkpoint("STG-20260811-missing")), encoding="utf-8")

    issues = [item for item in lint_repository(root) if item["code"] == "ATLAS028"]
    assert issues
    assert all(item["path"] == "_intake/checkpoints/wrong-name.json" for item in issues)
    assert any("filename" in item["message"] for item in issues)
    assert any("missing staging ID" in item["message"] for item in issues)


def test_lint_checkpoint_join_matches_exact_commit_and_merge_request(tmp_path: Path):
    root = _root(tmp_path)
    change = _merged_change()
    change["change_source"]["merge_requests"].append(
        {"id": "1421", "merged_commit": "b" * 40}
    )
    _write(root, f"_staging/changes/{change['id']}.md", change)
    checkpoint_value = _intake_checkpoint()
    checkpoint_value["observed_through"]["merge_request"] = "1421"
    checkpoint_value["considered_through"]["merge_request"] = "1421"
    checkpoint_value["last_run"]["dispositions"][0]["merge_request"] = "1421"
    checkpoint = root / "_intake/checkpoints/fixture-monorepo.json"
    checkpoint.parent.mkdir(parents=True)
    checkpoint.write_text(json.dumps(checkpoint_value), encoding="utf-8")

    issues = [item for item in lint_repository(root) if item["code"] == "ATLAS028"]
    assert any("merge request does not match" in item["message"] for item in issues)

    checkpoint_value["last_run"]["dispositions"][0].update(
        {"commit": "b" * 40, "merge_request": "1421"}
    )
    checkpoint_value["last_run"]["through_inclusive"] = "b" * 40
    checkpoint_value["observed_through"]["commit"] = "b" * 40
    checkpoint_value["considered_through"]["commit"] = "b" * 40
    checkpoint.write_text(json.dumps(checkpoint_value), encoding="utf-8")
    issues = [item for item in lint_repository(root) if item["code"] == "ATLAS028"]
    assert any("commit does not match" in item["message"] for item in issues)


def test_lint_checkpoint_join_rejects_ambiguous_staging_id(tmp_path: Path):
    root = _root(tmp_path)
    change = _merged_change()
    _write(root, f"_staging/changes/{change['id']}.md", change)
    _write(root, f"_staging/changes/duplicate/{change['id']}.md", change)
    checkpoint = root / "_intake/checkpoints/fixture-monorepo.json"
    checkpoint.parent.mkdir(parents=True)
    checkpoint.write_text(json.dumps(_intake_checkpoint()), encoding="utf-8")

    issues = [item for item in lint_repository(root) if item["code"] == "ATLAS028"]
    assert any("references ambiguous staging ID" in item["message"] for item in issues)


def test_lint_reports_duplicate_staging_ids_with_related_paths(tmp_path: Path):
    root = _root(tmp_path)
    change = _merged_change()
    _write(root, f"_staging/changes/{change['id']}.md", change)
    duplicate = {**change, "type": "staging.runbook", "source_type": "repository"}
    duplicate.pop("change_source")
    _write(root, f"_staging/runbooks/{change['id']}.md", duplicate)

    issue = next(
        item
        for item in lint_repository(root)
        if item["code"] == "ATLAS003" and "duplicate staging id" in item["message"]
    )

    assert issue["record_id"] == change["id"]
    assert issue["related_ids"] == [change["id"]]
    assert issue["related_paths"] == [
        f"_staging/changes/{change['id']}.md",
        f"_staging/runbooks/{change['id']}.md",
    ]
