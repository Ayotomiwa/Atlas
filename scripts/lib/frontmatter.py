from pathlib import Path
import yaml

def parse_frontmatter(path_or_text):
    text = Path(path_or_text).read_text(encoding='utf-8') if isinstance(path_or_text, (str, Path)) and Path(path_or_text).exists() else str(path_or_text)
    if not text.startswith('---\n'):
        raise ValueError('missing YAML frontmatter')
    end = text.find('\n---\n', 4)
    if end < 0:
        raise ValueError('unterminated YAML frontmatter')
    return yaml.safe_load(text[4:end]) or {}, text[end+5:]
