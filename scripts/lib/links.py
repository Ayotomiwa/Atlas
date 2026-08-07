import re
from pathlib import Path
LINK_RE=re.compile(r'\[[^\]]+\]\(([^)]+)\)')

def unresolved_links(path: Path, root: Path):
    out=[]
    text=path.read_text(encoding='utf-8')
    for target in LINK_RE.findall(text):
        if target.startswith(('http://','https://','#','mailto:')): continue
        target=target.split('#',1)[0]
        if not target: continue
        resolved=(path.parent/target).resolve()
        try: resolved.relative_to(root.resolve())
        except ValueError: out.append(target); continue
        if not resolved.exists(): out.append(target)
    return out
