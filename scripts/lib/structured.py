from __future__ import annotations

from pathlib import Path
import re

from scripts.lib.ids import valid_curated_id


LOCAL_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class StructuredFrontmatterError(ValueError):
    pass


def _strings(value: object, *, owner: str, field: str) -> list[str]:
    if not isinstance(value, list) or not value or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise StructuredFrontmatterError(f"{owner} {field} must contain non-empty strings")
    return [item.strip() for item in value]


def parse_data_assets(path: str | Path, frontmatter: dict, taxonomy: dict) -> list[dict]:
    """Validate and normalise schema-owned embedded data assets."""
    raw = frontmatter.get("assets", [])
    if not isinstance(raw, list):
        raise StructuredFrontmatterError("assets must be a list")
    if raw and frontmatter.get("type") != "schema-info":
        raise StructuredFrontmatterError("assets may be authored only on schema-info pages")

    allowed_asset_types = set(taxonomy["concept_fields"]["schema"]["data_asset_type"])
    allowed_confidence = set(taxonomy["statuses"]["connection_confidence"])
    seen: set[str] = set()
    assets: list[dict] = []
    for raw_asset in raw:
        if not isinstance(raw_asset, dict):
            raise StructuredFrontmatterError("asset entry must be an object")
        identifier = raw_asset.get("id")
        if not valid_curated_id(identifier, "asset") or identifier in seen:
            raise StructuredFrontmatterError(f"invalid or duplicate data asset id {identifier!r}")
        name = raw_asset.get("name")
        if not isinstance(name, str) or not name.strip():
            raise StructuredFrontmatterError(f"data asset {identifier} requires a name")
        asset_type = raw_asset.get("asset_type")
        if asset_type not in allowed_asset_types:
            raise StructuredFrontmatterError(f"data asset {identifier} has invalid asset_type {asset_type!r}")
        for scalar in ("physical_name", "description"):
            if scalar in raw_asset and not isinstance(raw_asset.get(scalar), str):
                raise StructuredFrontmatterError(f"data asset {identifier} {scalar} must be a string")
        confidence = raw_asset.get("confidence")
        if confidence not in allowed_confidence:
            raise StructuredFrontmatterError(f"data asset {identifier} has invalid confidence {confidence!r}")
        evidence = _strings(raw_asset.get("evidence"), owner=f"data asset {identifier}", field="evidence")
        if confidence != "reviewed" and not str(raw_asset.get("note", "")).strip():
            raise StructuredFrontmatterError(f"non-reviewed data asset {identifier} requires note")

        inputs = raw_asset.get("inputs", [])
        if not isinstance(inputs, list):
            raise StructuredFrontmatterError(f"data asset {identifier} inputs must be a list")
        normalised_inputs: list[dict] = []
        for raw_input in inputs:
            if not isinstance(raw_input, dict):
                raise StructuredFrontmatterError(f"data asset {identifier} input must be an object")
            input_id = raw_input.get("id")
            input_name = raw_input.get("name")
            if bool(input_id) == bool(input_name):
                raise StructuredFrontmatterError(
                    f"data asset {identifier} input requires exactly one of id or name"
                )
            if input_id is not None and not valid_curated_id(input_id, "asset"):
                raise StructuredFrontmatterError(
                    f"data asset {identifier} input id must use the asset.* prefix"
                )
            if input_name is not None and (not isinstance(input_name, str) or not input_name.strip()):
                raise StructuredFrontmatterError(f"data asset {identifier} input name must be non-empty")
            input_confidence = raw_input.get("confidence")
            if input_confidence not in allowed_confidence:
                raise StructuredFrontmatterError(
                    f"data asset {identifier} input has invalid confidence {input_confidence!r}"
                )
            input_evidence = _strings(
                raw_input.get("evidence"), owner=f"data asset {identifier} input", field="evidence"
            )
            if input_confidence != "reviewed" and not str(raw_input.get("note", "")).strip():
                raise StructuredFrontmatterError(
                    f"non-reviewed data asset {identifier} input requires note"
                )
            item = {
                "confidence": input_confidence,
                "evidence": input_evidence,
            }
            if input_id is not None:
                item["id"] = input_id
            else:
                item.update({"name": input_name.strip(), "external": True})
            if str(raw_input.get("note", "")).strip():
                item["note"] = raw_input["note"].strip()
            normalised_inputs.append(item)

        asset = {
            "id": identifier,
            "name": name.strip(),
            "asset_type": asset_type,
            "confidence": confidence,
            "evidence": evidence,
            "inputs": normalised_inputs,
        }
        for field in ("physical_name", "description", "note"):
            if field in raw_asset and raw_asset[field] not in (None, ""):
                asset[field] = raw_asset[field]
        assets.append(asset)
        seen.add(identifier)
    return assets


def parse_conflicts(path: str | Path, frontmatter: dict) -> list[dict]:
    """Validate common curated conflicts and return their qualified identities."""
    raw = frontmatter.get("conflicts", [])
    if not isinstance(raw, list):
        raise StructuredFrontmatterError("conflicts must be a list")
    owner = frontmatter.get("id")
    if raw and not isinstance(owner, str):
        raise StructuredFrontmatterError("conflicts require an owning stable ID")
    seen: set[str] = set()
    conflicts: list[dict] = []
    for raw_conflict in raw:
        if not isinstance(raw_conflict, dict):
            raise StructuredFrontmatterError("conflict entry must be an object")
        local_id = raw_conflict.get("conflict_id")
        if not isinstance(local_id, str) or not LOCAL_ID_RE.fullmatch(local_id) or local_id in seen:
            raise StructuredFrontmatterError(f"invalid or duplicate conflict_id {local_id!r}")
        topic = raw_conflict.get("topic")
        interpretation = raw_conflict.get("interpretation")
        if not isinstance(topic, str) or not topic.strip():
            raise StructuredFrontmatterError(f"conflict {local_id} requires a topic")
        if not isinstance(interpretation, str) or not interpretation.strip():
            raise StructuredFrontmatterError(f"conflict {local_id} requires an interpretation")
        claims = raw_conflict.get("claims")
        if not isinstance(claims, list) or len(claims) < 2:
            raise StructuredFrontmatterError(f"conflict {local_id} requires at least two claims")
        normalised_claims: list[dict] = []
        for claim in claims:
            if not isinstance(claim, dict) or not isinstance(claim.get("statement"), str) or not claim["statement"].strip():
                raise StructuredFrontmatterError(f"conflict {local_id} claim requires a statement")
            evidence = _strings(claim.get("evidence"), owner=f"conflict {local_id} claim", field="evidence")
            normalised_claims.append({"statement": claim["statement"].strip(), "evidence": evidence})
        conflicts.append(
            {
                "id": f"{owner}#{local_id}",
                "conflict_id": local_id,
                "topic": topic.strip(),
                "claims": normalised_claims,
                "interpretation": interpretation.strip(),
            }
        )
        seen.add(local_id)
    return conflicts
