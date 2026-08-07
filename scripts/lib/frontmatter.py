from pathlib import Path
import yaml

def parse_frontmatter_text(text: str):
    if not text.startswith('---\n'):
        return None, text
    parts=text.split('---\n',2)
    if len(parts)<3:
        raise ValueError('unterminated YAML frontmatter')
    data=yaml.safe_load(parts[1]) or {}
    if not isinstance(data, dict):
        raise ValueError('frontmatter must be a mapping')
    return data, parts[2]

def parse_frontmatter(path: Path):
    return parse_frontmatter_text(path.read_text(encoding='utf-8'))
