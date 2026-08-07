from pathlib import Path
import json
from scripts.lib.frontmatter import parse_frontmatter
META={"schema_version":"atlas-map/1.0","generated":True,"generator":"scripts/rebuild_maps.py","package":"teama","source_of_truth":["_curated/**/*.md"]}

def governed_pages(root):
    root=Path(root); out=[]
    for p in sorted((root/'_curated').rglob('*.md')):
        if p.name in {'README.md','index.md','_template.md'} or 'maps' in p.parts or 'status' in p.parts: continue
        try: fm,_=parse_frontmatter(p)
        except Exception: continue
        if fm.get('status')!='archived': out.append((p,fm))
    return out

def build_maps(root):
    maps={k:{**META,"nodes":[],"edges":[]} for k in ['flow-component-map.json','repo-dependency-map.json','infra-dependency-map.json']}
    nodes={k:{} for k in maps}
    for p,fm in governed_pages(root):
        ident=fm.get('id'); typ=fm.get('type')
        if not ident: continue
        for rel in fm.get('relationships') or []:
            rt=rel.get('type'); tgt=rel.get('target'); edge={k:v for k,v in rel.items() if k in {'type','target','kind','confidence','note','evidence'}}; edge['source']=ident
            dest=[]
            if rt=='atlas.participates-in' or (typ=='atlas.flow' and rt=='atlas.depends-on'): dest.append('flow-component-map.json')
            if typ=='atlas.component' and rt in {'atlas.consumes','atlas.produces','atlas.depends-on'}: dest.append('repo-dependency-map.json')
            if typ=='atlas.infra' and rt in {'atlas.depends-on','atlas.deployed-by','atlas.consumes','atlas.produces'}: dest.append('infra-dependency-map.json')
            if typ=='atlas.component' and rt=='atlas.deployed-by': dest.append('infra-dependency-map.json')
            for m in dest:
                nodes[m][ident]={"id":ident,"type":typ}
                if tgt: nodes[m].setdefault(tgt,{"id":tgt})
                maps[m]['edges'].append(edge)
    for m in maps:
        maps[m]['nodes']=sorted(nodes[m].values(), key=lambda x:x['id'])
        maps[m]['edges']=sorted(maps[m]['edges'], key=lambda x:(x.get('source',''),x.get('type',''),x.get('target','')))
    return maps

def stable_bytes(obj): return (json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False)+'\n').encode()
