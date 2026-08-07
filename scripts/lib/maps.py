from pathlib import Path
from .frontmatter import parse_frontmatter
MAP_META={"schema_version":"atlas-map/1.0","generated":True,"generator":"scripts/rebuild_maps.py","package":"teama","source_of_truth":["_curated/**/*.md"]}

def governed_pages(root: Path):
    skip={'README.md','index.md','_template.md','curation-status.md'}
    for p in sorted((root/'_curated').rglob('*.md')):
        if p.name in skip or '/maps/' in p.as_posix() or '/status/' in p.as_posix(): continue
        try: fm,_=parse_frontmatter(p)
        except Exception: continue
        if fm and fm.get('type','').startswith('atlas.') and fm.get('status')!='archived': yield p,fm

def generate_maps(root: Path):
    out={k:{**MAP_META,"nodes":[],"edges":[],"reverse":[]} for k in ('flow-component','repo-dependency','infra-dependency')}
    ids={}
    pages=list(governed_pages(root))
    for p,fm in pages:
        ids[fm.get('id')]=(p,fm)
        node={"id":fm.get('id'),"type":fm.get('type'),"title":fm.get('title',''),"path":p.relative_to(root).as_posix()}
        if fm.get('type') in {'atlas.flow','atlas.component'}: out['flow-component']['nodes'].append(node)
        if fm.get('type') in {'atlas.component','atlas.schema-info'}: out['repo-dependency']['nodes'].append(node)
        if fm.get('type') in {'atlas.infra','atlas.component'}: out['infra-dependency']['nodes'].append(node)
    for p,fm in pages:
        src=fm.get('id'); st=fm.get('type')
        for r in fm.get('relationships') or []:
            if not isinstance(r,dict): continue
            typ=r.get('type'); tgt=r.get('target')
            edge={k:r[k] for k in ('type','target','kind','confidence','note','evidence') if k in r}; edge['source']=src
            buckets=[]
            if typ=='atlas.participates-in' or (st=='atlas.flow' and typ=='atlas.depends-on'): buckets.append('flow-component')
            if st=='atlas.component' and typ in {'atlas.consumes','atlas.produces','atlas.depends-on'}: buckets.append('repo-dependency')
            if st=='atlas.infra' and typ in {'atlas.depends-on','atlas.deployed-by','atlas.consumes','atlas.produces'}: buckets.append('infra-dependency')
            if st=='atlas.component' and typ=='atlas.deployed-by': buckets.append('infra-dependency')
            for b in buckets:
                out[b]['edges'].append(edge)
                rev=dict(edge); rev['source'],rev['target']=tgt,src; out[b]['reverse'].append(rev)
    for m in out.values():
        for key in ('nodes','edges','reverse'):
            m[key]=sorted(m[key], key=lambda x: json_key(x))
    return out

def json_key(x):
    return tuple(str(x.get(k,'')) for k in ('source','target','type','id','path'))
