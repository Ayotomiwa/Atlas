from pathlib import Path
import yaml

def load_page(path: Path):
    text=path.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        return None,text
    try:
        _, fm, body=text.split('---',2)
        return yaml.safe_load(fm) or {}, body.lstrip('\n')
    except Exception:
        return None,text
