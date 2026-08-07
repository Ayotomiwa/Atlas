import pytest

from scripts.lib.ids import valid_curated_id, valid_staging_id


@pytest.mark.parametrize(
    "value,prefix",
    [
        ("atlas-comp.sds.service", "atlas-comp"),
        ("atlas-flow.reference-data", "atlas-flow"),
        ("atlas-standard.java.spring-boot", "atlas-standard"),
    ],
)
def test_valid_curated_ids(value: str, prefix: str):
    assert valid_curated_id(value, prefix)


@pytest.mark.parametrize(
    "value,prefix",
    [
        ("atlas-flow.sds.service", "atlas-comp"),
        ("atlas-comp", "atlas-comp"),
        ("atlas-comp.Bad.Name", "atlas-comp"),
        ("atlas-comp.bad_name", "atlas-comp"),
        (None, "atlas-comp"),
    ],
)
def test_invalid_curated_ids(value, prefix: str):
    assert not valid_curated_id(value, prefix)


@pytest.mark.parametrize(
    "value",
    [
        "STG-20260807-service-onboarding",
        "STG-20260807-service-onboarding-2",
    ],
)
def test_valid_staging_ids(value: str):
    assert valid_staging_id(value)


@pytest.mark.parametrize(
    "value",
    [
        "stg-20260807-service",
        "STG-2026-08-07-service",
        "STG-20260807-Service",
        "STG-20260807-service_2",
    ],
)
def test_invalid_staging_ids(value: str):
    assert not valid_staging_id(value)
