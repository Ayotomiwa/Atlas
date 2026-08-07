from pathlib import Path

import pytest

from scripts.lib.frontmatter import parse_frontmatter


def test_parse_frontmatter_from_text():
    fm, body = parse_frontmatter("---\nid: fixture\nitems: [a, b]\n---\n# Heading\n")
    assert fm["id"] == "fixture"
    assert fm["items"] == ["a", "b"]
    assert "Heading" in body


def test_parse_frontmatter_from_path(tmp_path: Path):
    path = tmp_path / "page.md"
    path.write_text("---\ntype: atlas.component\n---\nbody\n", encoding="utf-8")
    fm, body = parse_frontmatter(path)
    assert fm["type"] == "atlas.component"
    assert body.strip() == "body"


@pytest.mark.parametrize(
    "text, message",
    [
        ("# no frontmatter\n", "missing YAML frontmatter"),
        ("---\nid: x\n", "unterminated YAML frontmatter"),
    ],
)
def test_invalid_frontmatter_is_rejected(text: str, message: str):
    with pytest.raises(ValueError, match=message):
        parse_frontmatter(text)
