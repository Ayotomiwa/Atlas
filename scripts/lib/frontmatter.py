from pathlib import Path
import yaml


def parse_frontmatter(path_or_text):
    if isinstance(path_or_text, Path):
        text = path_or_text.read_text(encoding="utf-8")
    elif isinstance(path_or_text, str) and path_or_text.startswith("---\n"):
        text = path_or_text
    elif isinstance(path_or_text, str):
        candidate = Path(path_or_text)
        text = candidate.read_text(encoding="utf-8") if candidate.exists() else path_or_text
    else:
        text = str(path_or_text)
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("unterminated YAML frontmatter")
    return yaml.safe_load(text[4:end]) or {}, text[end + 5 :]
