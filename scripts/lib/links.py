from __future__ import annotations

from pathlib import Path
import re
from urllib.parse import unquote

# Markdown links only. Images are intentionally excluded because the V1 repository
# has no required image assets and image URLs are not part of Atlas navigation.
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
REMOTE_SCHEMES = ("http://", "https://", "mailto:", "tel:")


def markdown_links(text: str) -> list[str]:
    """Return raw Markdown link targets in source order."""
    return LINK_RE.findall(text)


def _clean_target(target: str) -> str:
    target = target.strip()
    # Support the common Markdown form: (path "optional title").
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    elif " \"" in target:
        target = target.split(" \"", 1)[0]
    return unquote(target.split("#", 1)[0].strip())


def broken_links(path: str | Path) -> list[str]:
    """Return relative Markdown targets that do not resolve from *path*."""
    path = Path(path)
    out: list[str] = []
    for raw in markdown_links(path.read_text(encoding="utf-8")):
        target = raw.strip()
        if not target or target.startswith("#") or target.startswith(REMOTE_SCHEMES):
            continue
        clean = _clean_target(target)
        if not clean:
            continue
        # Windows normalises a path made only of dots to the containing
        # directory. Markdown's common `...` placeholder is not a real route.
        if clean == "...":
            out.append(raw)
            continue
        if not (path.parent / clean).resolve().exists():
            out.append(raw)
    return out


def links_to(path: str | Path, target: str | Path) -> bool:
    """Whether a Markdown file contains a relative link resolving to target."""
    path = Path(path)
    target = Path(target).resolve()
    for raw in markdown_links(path.read_text(encoding="utf-8")):
        clean = _clean_target(raw)
        if not clean or clean == "..." or raw.startswith(REMOTE_SCHEMES):
            continue
        if (path.parent / clean).resolve() == target:
            return True
    return False
