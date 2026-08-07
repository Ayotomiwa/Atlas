#!/usr/bin/env python3
import argparse,re,subprocess,sys,yaml
from datetime import date
from pathlib import Path
from lib.frontmatter import load_page
from lib.taxonomy import type_map,relationship_names,status_sets
from lib.ids import valid_id

SKIP={'README.md','_template.md'}
LINK=re.compile(r'\[[^]]+\]\(([^)]+)\)')
SECRETS=[re.compile(r'AKIA[0-9A-Z]{16}'),re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),re.compile(r'(?i)(?:token|password|secret)\s*[:=]\s*["\']?[A-Za-z0-9_\-]{20,}')]
ALLOWED_KINDS={'event','api','table','file','shared-library','schema-library','component','config','job-output','other'}

def report(findings,fmt):
    if fmt=='json':
        import json; print(json.dumps(findings,indent=2))
    else:
        for f in findings: print(f"{f['level']} {f['code']} {f['path']}:{f['line']} {f['message']}")
        print(f"Summary: {sum(f['level']=='ERROR' for f in findings)} ERROR, {sum(f['level']=='WARN' for f in findings)} WARN")

def lint(root,rules=None):
    root=Path(root); findings=[]
    def add(level,code,p,msg,line=1):
        if not rules or code in rules: findings.append({'level':level,'code':code,'path':str(Path(p).relative_to(root)) if Path(p).is_absolute() else str(p),'line':line,'message':msg})
    tm=type_map(root); rn=relationship_names(root); cs,ss,conf=status_sets(root)
    pkgfm,_=load_page(root/'package.md'); pkg=pkgfm['package']; domains=set(pkgfm.get('domains',[]))
    pages=[]; ids={}
    for p in root.rglob('*.md'):
        if '.git' in p.parts or '_fixtures' in p.parts or '.claude' in p.parts or p.name in SKIP: continue
        fm,body=load_page(p)
        if fm is None:
            if p.name=='index.md' or p.name=='package.md' or p.parts[-2:]==('status','curation-status.md'): add('ERROR','ATLAS001',p,'frontmatter missing or invalid')
            continue
        typ=fm.get('type'); t=tm.get(typ)
        if not t or t.get('status')!='active': add('ERROR','ATLAS001',p,'type must be an active taxonomy type')
        if typ and t and t.get('status')=='reserved': add('ERROR','ATLAS006',p,'reserved type cannot have pages')
        ident=fm.get('id')
        if not ident or (typ!='atlas.package' and not valid_id(ident)): add('ERROR','ATLAS002',p,'id missing or invalid')
        if ident:
            if ident in ids: add('ERROR','ATLAS002',p,f'duplicate id {ident}')
            ids[ident]=p
        if fm.get('package')!=pkg: add('ERROR','ATLAS003',p,f'package must equal {pkg}')
        if typ not in {'atlas.package','atlas.index'} and t:
            rel=p.relative_to(root).as_posix(); folder=t['folder'].rstrip('/')
            if not rel.startswith(folder+'/'): add('ERROR','ATLAS005',p,f'page must live under {folder}')
            if p.stem and ident:
                if not ident.endswith('.'+p.stem): add('ERROR','ATLAS004',p,'id slug must equal filename stem')
                if t.get('grouped'):
                    group=p.parent.name
                    if f'.{group}.{p.stem}' not in ident: add('ERROR','ATLAS004',p,'group segment must equal containing folder')
        if typ and typ.startswith('atlas.staging.'):
            if fm.get('status') not in ss: add('ERROR','ATLAS001',p,'invalid staging status')
            if fm.get('promoted_to'):
                try:
                    st=subprocess.run(['git','status','--porcelain','--',str(p)],cwd=root,capture_output=True,text=True).stdout.strip()
                    if st: add('ERROR','ATLAS022',p,'staging file with promoted_to set has uncommitted modifications')
                except Exception: pass
        elif typ and typ not in {'atlas.package','atlas.index'}:
            if fm.get('status') not in cs: add('ERROR','ATLAS001',p,'invalid curated status')
            for d in ((fm.get('routing') or {}).get('domains') or []):
                if d not in domains: add('ERROR','ATLAS018',p,f'undeclared domain {d}')
            if fm.get('status')=='curated' and (not fm.get('reviewed_by') or not fm.get('last_reviewed') or (not fm.get('evidence') and not fm.get('evidence_exempt'))): add('ERROR','ATLAS013',p,'curated pages need reviewer, review date and evidence')
            if fm.get('status')=='curated' and fm.get('last_reviewed'):
                try:
                    reviewed=fm['last_reviewed']; reviewed=reviewed if isinstance(reviewed,date) else date.fromisoformat(str(reviewed))
                    if (date.today()-reviewed).days>180: add('WARN','ATLAS021',p,'last_reviewed is older than 180 days')
                except Exception: pass
            for m in re.finditer(r'^##+\s+.+$',body,re.M):
                end=re.search(r'^##+\s+.+$',body[m.end():],re.M); chunk=body[m.end():m.end()+(end.start() if end else len(body[m.end():]))].strip()
                if not chunk: add('ERROR','ATLAS017',p,'empty body section')
        for edge in fm.get('relationships') or []:
            if edge.get('type') not in rn: add('ERROR','ATLAS009',p,'unknown relationship type')
            if edge.get('type') in {'atlas.consumes','atlas.produces','atlas.depends-on'} and edge.get('kind') not in ALLOWED_KINDS: add('ERROR','ATLAS011',p,'kind required and must be allowed')
            if edge.get('confidence') not in conf or (edge.get('confidence')!='reviewed' and not edge.get('note')): add('ERROR','ATLAS012',p,'valid confidence required; non-reviewed needs note')
        for m in LINK.finditer(body):
            link=m.group(1).split('#')[0]
            if link and not re.match(r'^[a-z]+://',link) and not link.startswith('#') and not (p.parent/link).resolve().exists(): add('ERROR','ATLAS008',p,f'broken relative link {link}')
        text=p.read_text(errors='ignore')
        if any(rx.search(text) for rx in SECRETS): add('ERROR','ATLAS020',p,'possible secret pattern')
        pages.append((p,fm,body))
    for p,fm,_ in pages:
        for edge in fm.get('relationships') or []:
            target=edge.get('target','')
            if target and not target.startswith(('team:','person:')) and target not in ids: add('ERROR','ATLAS010',p,f'unresolved relationship target {target}')
        for ev in fm.get('evidence') or []:
            if isinstance(ev,str) and not (ev.startswith(('http://','https://','external:')) or (root/ev).exists()): add('ERROR','ATLAS015',p,f'evidence path does not resolve: {ev}')
        typ=fm.get('type'); status=fm.get('status')
        if typ and typ not in {'atlas.package','atlas.index'} and typ.startswith('atlas.') and not typ.startswith('atlas.staging.'):
            idx=p.parent/'index.md'
            if status!='archived' and idx.exists() and p.name not in idx.read_text(): add('ERROR','ATLAS007',p,'non-archived page missing from folder index')
            if status=='archived' and idx.exists() and p.name in idx.read_text(): add('ERROR','ATLAS016',p,'archived page must not appear in index')
    resources=set()
    for _,fm,_ in pages:
        if fm.get('type')=='atlas.infra': resources.update(fm.get('resource_names') or [])
    for p,fm,_ in pages:
        if fm.get('type')=='atlas.component':
            for name in fm.get('deployed_as') or []:
                if name not in resources: add('WARN','ATLAS014',p,f'deployed resource not found in infra pages: {name}')
    if not rules or 'ATLAS019' in rules:
        cp=subprocess.run([sys.executable,str(root/'scripts/rebuild_maps.py'),'--check',str(root)],capture_output=True,text=True)
        if cp.returncode: add('ERROR','ATLAS019',root/'_curated/maps/index.md','generated maps differ from pages')
    return findings

def self_test(root):
    root=Path(root)
    required=['taxonomy/types.yaml','taxonomy/relationships.yaml','taxonomy/statuses.yaml']
    missing=[x for x in required if not (root/x).exists()]
    invalid=sorted((root/'_fixtures/invalid').glob('ATLAS*-*.md')) if (root/'_fixtures/invalid').exists() else []
    expected={f'ATLAS{i:03d}' for i in range(1,23)}
    present={p.name.split('-',1)[0] for p in invalid}
    if missing or present!=expected:
        print('self-test failed:',{'missing':missing,'missing_fixture_codes':sorted(expected-present)}); return 1
    print('self-test: PASS'); return 0

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('path',nargs='?',default='.'); ap.add_argument('--rules'); ap.add_argument('--format',choices=['text','json'],default='text'); ap.add_argument('--warn-as-error',action='store_true'); ap.add_argument('--self-test',action='store_true')
    a=ap.parse_args(); root=Path(a.path).resolve()
    if a.self_test: return self_test(root)
    rules=set(a.rules.split(',')) if a.rules else None; f=lint(root,rules); report(f,a.format)
    return 1 if any(x['level']=='ERROR' or (a.warn_as_error and x['level']=='WARN') for x in f) else 0
if __name__=='__main__': raise SystemExit(main())
