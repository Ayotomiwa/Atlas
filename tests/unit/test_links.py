from pathlib import Path

from scripts.lib.links import broken_links, links_to, markdown_links


def test_relative_links_resolve_and_remote_or_anchor_links_are_ignored(tmp_path: Path):
    target = tmp_path / "target.md"
    target.write_text("ok\n", encoding="utf-8")
    source = tmp_path / "source.md"
    source.write_text(
        "[local](target.md#section) [remote](https://example.com) [anchor](#here)\n",
        encoding="utf-8",
    )
    assert broken_links(source) == []
    assert links_to(source, target)


def test_broken_relative_link_is_reported(tmp_path: Path):
    source = tmp_path / "source.md"
    source.write_text("[missing](nested/missing.md)\n", encoding="utf-8")
    assert broken_links(source) == ["nested/missing.md"]


def test_markdown_link_extractor_excludes_images():
    text = "[page](a.md) ![image](a.png) [other](b.md)"
    assert markdown_links(text) == ["a.md", "b.md"]
