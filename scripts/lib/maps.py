from pathlib import Path
from .frontmatter import load_page

def curated_pages(root):
    for p in (Path(root)/'_curated').rglob('*.md'):
        if p.name in {'README.md','_template.md','index.md','curation-status.md'} or 'maps' in p.parts or 'domains' in p.parts or 'status' in p.parts:
            continue
        fm,_=load_page(p)
        if fm and fm.get('type','').startswith('atlas.'):
            yield p,fm
