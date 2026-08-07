#!/usr/bin/env python3
from pathlib import Path
import argparse, json, re, sys, datetime
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import yaml
from scripts.lib.frontmatter import parse_frontmatter
from scripts.lib.taxonomy import load_taxonomy
from scripts.lib.ids import valid_curated_id, valid_staging_id
from scripts.lib.links import broken_links
from scripts.lib.maps import build_maps, stable_bytes
NOT_COVERED='*Not covered — no evidence in current staging material.*'
KINDS={'event','api','table','file','component','shared-library','schema-library','config','job-output','infra','other'}
SENSITIVE_MARKERS=['api_key','api-key','secret','token','private key']
EXEMPT_NAMES={'README.md','index.md','_template.md','CLAUDE.md','log.md','service-questionnaire.md','standards-questionnaire.md','local-CLAUDE.template.md','curation-status.md','IMPLEMENTATION_SPEC.md'}

def issue(code,level,path,msg): return {'code':code,'level':level,'path':str(path),'message':msg}
def main(argv=None):
    ap=argparse.ArgumentParser(); ap.add_argument('path',nargs='?',default='.'); ap.add_argument('--format',choices=['text','json'],default='text'); ap.add_argument('--warn-as-error',action='store_true'); a=ap.parse_args(argv)
    root=Path(a.path).resolve(); tax=load_taxonomy(root); issues=[]
    types={x['name']:x for x in tax['types']['types']}; active={k:v for k,v in types.items() if v.get('status')=='active'}; rels=set(tax['relationships']['relationships']); statuses=set(tax['statuses']['curated_status']); conf=set(tax['statuses']['relationship_confidence']); cats=set(tax['categories']['categories']); ids={}
    governed=[]
    for p in sorted(root.rglob('*.md')):
        rel=p.relative_to(root)
        text=p.read_text(encoding='utf-8')
        low=text.lower()
        if any(marker in low and any(ch.isdigit() for ch in low[low.find(marker):low.find(marker)+80]) for marker in SENSITIVE_MARKERS):
            issues.append(issue('ATLAS019','ERROR',rel,'obvious secret-like pattern detected'))
        if p.name not in EXEMPT_NAMES:
            for b in broken_links(p): issues.append(issue('ATLAS008','ERROR',rel,f'broken relative link {b}'))
        is_governed = (('_curated' in rel.parts and p.name not in EXEMPT_NAMES and 'maps' not in rel.parts and 'status' not in rel.parts) or ('_staging' in rel.parts and p.name not in EXEMPT_NAMES))
        if not is_governed: continue
        governed.append((p,rel))
        try: fm,body=parse_frontmatter(p)
        except Exception as e: issues.append(issue('ATLAS001','ERROR',rel,str(e))); continue
        typ=fm.get('type')
        if typ not in active: issues.append(issue('ATLAS002','ERROR',rel,f'inactive/unknown type {typ}')); continue
        spec=active[typ]; folder=spec.get('folder','')
        if folder!='**' and folder!='.' and not str(rel).startswith(folder+'/'): issues.append(issue('ATLAS002','ERROR',rel,f'type {typ} not allowed under {rel.parent}'))
        if fm.get('package')!='teama': issues.append(issue('ATLAS004','ERROR',rel,'package must equal teama'))
        if typ.startswith('atlas.staging.'):
            if not valid_staging_id(fm.get('id')): issues.append(issue('ATLAS003','ERROR',rel,'invalid staging id'))
            continue
        ident=fm.get('id'); pref=spec.get('id_prefix')
        if not valid_curated_id(ident,pref): issues.append(issue('ATLAS003','ERROR',rel,'invalid curated id prefix/grammar'))
        elif ident in ids: issues.append(issue('ATLAS003','ERROR',rel,f'duplicate id also in {ids[ident]}'))
        else: ids[ident]=rel
        st=fm.get('status')
        if st not in statuses: issues.append(issue('ATLAS006','ERROR',rel,f'invalid status {st}'))
        if st=='curated' and (not fm.get('reviewed_by') or not fm.get('last_reviewed') or not fm.get('evidence')): issues.append(issue('ATLAS007','ERROR',rel,'curated page requires reviewer/date/evidence'))
        if typ=='atlas.standard':
            cat=fm.get('standard_category')
            if cat not in cats or len(rel.parts)<3 or rel.parts[2]!=cat: issues.append(issue('ATLAS017','ERROR',rel,'standard category invalid or storage mismatch'))
        for r in fm.get('relationships') or []:
            rt=r.get('type')
            if rt not in rels: issues.append(issue('ATLAS009','ERROR',rel,f'unknown relationship {rt}'))
            if rt in {'atlas.consumes','atlas.produces','atlas.depends-on'} and r.get('kind') not in KINDS: issues.append(issue('ATLAS011','ERROR',rel,'relationship kind missing/invalid'))
            c=r.get('confidence')
            if c not in conf: issues.append(issue('ATLAS012','ERROR',rel,'invalid relationship confidence'))
            if c!='reviewed' and not r.get('note'): issues.append(issue('ATLAS012','ERROR',rel,'non-reviewed relationship requires note'))
        if st not in {'archived'}:
            idx=p.parent/'index.md'
            if idx.exists() and p.name not in idx.read_text(encoding='utf-8'): issues.append(issue('ATLAS013','ERROR',rel,'page missing from index'))
        elif (p.parent/'index.md').exists() and p.name in (p.parent/'index.md').read_text(encoding='utf-8'): issues.append(issue('ATLAS014','ERROR',rel,'archived page present in normal index'))
        for ev in fm.get('evidence') or []:
            if isinstance(ev,str) and '://' not in ev and (ev.startswith('_') or ev.startswith('reviews/') or ev.startswith('onboarding/')) and not (root/ev).exists(): issues.append(issue('ATLAS015','ERROR',rel,f'evidence path missing {ev}'))
        for m in re.finditer(r'^##\s+(.+?)\s*$([\s\S]*?)(?=^##\s+|\Z)', body, re.M):
            sec=m.group(2).strip()
            if not sec: issues.append(issue('ATLAS016','ERROR',rel,f'empty section {m.group(1)}'))
        if st in {'proposed','curated'} and fm.get('last_reviewed'):
            try:
                d=datetime.date.fromisoformat(str(fm['last_reviewed']))
                if (datetime.date.today()-d).days>180: issues.append(issue('ATLAS020','WARN',rel,'review older than 180 days'))
            except ValueError: pass
        if typ=='atlas.component' and fm.get('deployed_as'):
            infra='\n'.join(q.read_text(encoding='utf-8') for q in (root/'_curated/infra').rglob('*.md'))
            for x in fm.get('deployed_as') or []:
                if x not in infra: issues.append(issue('ATLAS022','WARN',rel,f'deployed_as has no infra evidence: {x}'))
    for p,rel in governed:
        if '_staging' in rel.parts: continue
        try: fm,_=parse_frontmatter(p)
        except Exception: continue
        for r in fm.get('relationships') or []:
            tgt=r.get('target','')
            if r.get('confidence')=='reviewed' and tgt.startswith('atlas-') and tgt not in ids: issues.append(issue('ATLAS010','ERROR',rel,f'reviewed local target missing {tgt}'))
    for name,obj in build_maps(root).items():
        p=root/'_curated/maps'/name
        if not p.exists() or p.read_bytes()!=stable_bytes(obj): issues.append(issue('ATLAS018','ERROR',p.relative_to(root),'generated map drift'))
    if a.format=='json': print(json.dumps(issues,indent=2))
    else:
        for i in issues: print(f"{i['level']} {i['code']} {i['path']}: {i['message']}")
        print(f"{sum(i['level']=='ERROR' for i in issues)} error(s), {sum(i['level']=='WARN' for i in issues)} warning(s)")
    return 1 if any(i['level']=='ERROR' or (a.warn_as_error and i['level']=='WARN') for i in issues) else 0
if __name__=='__main__': raise SystemExit(main())
