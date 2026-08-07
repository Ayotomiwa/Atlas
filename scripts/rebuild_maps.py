#!/usr/bin/env python3
import argparse,json,sys,yaml
from pathlib import Path
from lib.maps import curated_pages

MAPS=['repo-dependency-map.json','infra-dependency-map.json','flow-component-map.json']

def desired(root):
    root=Path(root); rel=yaml.safe_load((root/'taxonomy/relationships.yaml').read_text())
    mapping={(x['relationship'],x['target_kind']):x['verb'] for x in rel.get('map_verb_mapping',[])}
    pages=list(curated_pages(root)); ids={fm['id']:(p,fm) for p,fm in pages}
    buckets={m:{'metadata':{'schema_version':'atlas-map/1.0','generated':True,'generator':'scripts/rebuild_maps.py','source_of_truth':'_curated markdown pages'},'components':[]} for m in MAPS}
    for p,fm in pages:
        if fm.get('type')!='atlas.component': continue
        base={'id':fm['id'],'path':str(p.relative_to(root)),'domain_group':fm.get('domain_group',''),'component_type':fm.get('component_type','unknown'),'component_scope':fm.get('component_scope','unknown'),'monorepo_path':fm.get('monorepo_path',''),'relationships':[]}
        for edge in fm.get('relationships') or []:
            verb=mapping.get((edge.get('type'),edge.get('kind')))
            if verb:
                base['relationships'].append({'kind':edge.get('kind'),'name':edge.get('target'),'relationship':verb,'from':fm['id'],'to':edge.get('target'),'evidence':edge.get('evidence',fm.get('evidence',[])),'confidence':edge.get('confidence')})
        buckets['repo-dependency-map.json']['components'].append(base)
    for p,fm in pages:
        if fm.get('type')=='atlas.infra':
            buckets['infra-dependency-map.json']['components'].append({'id':fm['id'],'path':str(p.relative_to(root)),'relationships':fm.get('relationships') or []})
        if fm.get('type')=='atlas.component':
            pe=[e for e in fm.get('relationships') or [] if e.get('type')=='atlas.participates-in']
            if pe: buckets['flow-component-map.json']['components'].append({'id':fm['id'],'path':str(p.relative_to(root)),'relationships':pe})
    return buckets

def domain_indexes(root):
    root=Path(root); package=yaml.safe_load((root/'package.md').read_text().split('---',2)[1]); domains=package.get('domains',[])
    pages=list(curated_pages(root)); out={}
    for d in domains:
        lines=['---',f'id: atlas.datalens.index.domains.{d}','type: atlas.index','package: datalens','schema_version: atlas/1.0','---','',f'# {d.upper()} domain','']; grouped={}
        for p,fm in pages:
            if d in ((fm.get('routing') or {}).get('domains') or []): grouped.setdefault(fm['type'],[]).append((p,fm))
        labels=[('atlas.component','Components'),('atlas.flow','Flows'),('atlas.infra','Infra'),('atlas.schema-info','Schema info'),('atlas.business-concept','Business concepts'),('atlas.standard','Standards'),('atlas.runbook','Runbooks'),('atlas.incident-learning','Incident learnings')]
        for typ,label in labels:
            lines += [f'## {label}','']; vals=grouped.get(typ,[])
            if vals:
                for p,fm in vals: lines.append(f"- [{fm.get('title',fm['id'])}](../../{p.relative_to(root/'_curated')})")
            else: lines.append('*Not covered — no evidence in current staging material.*')
            lines.append('')
        out[root/'_curated/domains'/d/'index.md']='\n'.join(lines)+'\n'
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); ap.add_argument('--domains',action='store_true'); ap.add_argument('path',nargs='?',default='.')
    a=ap.parse_args(); root=Path(a.path); changes=[]
    for name,data in desired(root).items():
        p=root/'_curated/maps'/name; txt=json.dumps(data,indent=2,sort_keys=False)+'\n'
        if p.exists() and p.read_text()==txt: pass
        elif a.check: changes.append(str(p))
        else: p.parent.mkdir(parents=True,exist_ok=True); p.write_text(txt)
    if a.domains:
        for p,txt in domain_indexes(root).items():
            if p.exists() and p.read_text()==txt: pass
            elif a.check: changes.append(str(p))
            else: p.parent.mkdir(parents=True,exist_ok=True); p.write_text(txt)
    if changes:
        print('Generated files differ:'); print('\n'.join(changes)); return 1
    return 0
if __name__=='__main__': raise SystemExit(main())
