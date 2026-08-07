from __future__ import annotations

import re

# Curated IDs are prefix + one or more dot-separated kebab-case segments.
ID_RE = re.compile(r"^[a-z0-9-]+(?:\.[a-z0-9-]+)+$")
STG_RE = re.compile(r"^STG-\d{8}-[a-z0-9-]+(?:-\d+)?$")


def valid_curated_id(value: object, prefix: str | None) -> bool:
    return bool(
        isinstance(value, str)
        and prefix
        and value.startswith(prefix + ".")
        and ID_RE.fullmatch(value)
    )


def valid_staging_id(value: object) -> bool:
    return bool(isinstance(value, str) and STG_RE.fullmatch(value))
