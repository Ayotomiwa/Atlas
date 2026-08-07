from pathlib import Path
import re
LINK_RE=re.compile(r'(?<!!)\[[^\]]+\]\(([^)]+)\)')
def broken_links(path):
    path=Path(path); out=[]
    for target in LINK_RE.findall(path.read_text(encoding='utf-8')):
        if '://' in target or target.startswith('#'): continue
        clean=target.split('#',1)[0]
        if clean and not (path.parent/clean).resolve().exists(): out.append(target)
    return out
