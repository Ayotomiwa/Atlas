#!/usr/bin/env python3
import argparse,json,re,sys
from datetime import date,datetime
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from scripts.lib.frontmatter import parse_frontmatter
from scripts.lib.ids import valid_curated_id,valid_staging_id
from scripts.lib.taxonomy import load_types,load_relationships,load_statuses,load_standard_categories
from scripts.lib.links import unresolved_links
SECRET_RE=re.compile(r'(?i)(-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|aws_secret_access_key\s*[:=]|api[_-]?key\s*[:=]\s*["\']?[A-Za-z0-9/+]{20,}|token\s*[:=]\s*["\']?[A-Za-z0-9_-]{24,})')
REQ_KIND={'atlas.consumes','atlas.produces','atlas.depends-on'}
KINDS={'event','api','table','file','component','shared-library','schema-library','config','job-output','infra','other'}
NOT_COVERED='*Not covered — no evidence in current staging material.*'
EXEMPT={'README.md','index.md','_template.md','CLAUDE.md','log.md','curation-status.md','service-questionnaire.md','standards-questionnaire.md','local-CLAUDE.template.md','SKILL.md'}
REQ_SECTIONS={
'atlas.component':['Summary','Responsibility','Location','Internal units','Consumes','Produces','Flows','Infrastructure','Local repository references','Operational notes','Runbooks','Standards','Incident learnings','Evidence','Possible relationships','Open questions / coverage limits'],
'atlas.flow':['Summary','Purpose and boundary','Entry point','End-to-end steps','Participating components','Inputs and outputs','Upstream dependencies','Downstream consumers','Jobs and schedules','Infrastructure','Failure modes','Runbooks','Incident learnings','Standards','Evidence','Possible relationships','Open questions / coverage limits'],
'atlas.infra':['Summary','Package location and structure','Environment notes','Internal resources','Promoted resources and promotion reason','Resource relationships','Components using resources','Flows using resources','Parameters/imports/exports','Schedules/triggers/events','Permissions and roles','Monitoring','Impact if changed or deleted','Evidence','Possible relationships','Open questions / coverage limits'],
'atlas.schema-info':['Summary','Business meaning','Physical identity','Grain','Keys','Temporal model','Important fields','Producers','Consumers','Approved/known joins','Quality issues','Classification and access notes','Evidence','Open questions / coverage limits']}

def issue(code,level,path,msg): return {'code':code,'level':level,'path':str(path),'message':msg}
def allowed_folder(rel, info):
    folder=info.get('folder','**')
    if folder=='**': return True
    if folder=='.': return rel.as_posix()==info.get('file','package.md')
    return rel.as_posix().startswith(folder.rstrip('/')+'/')
def index_contains(root,p,fm):
    typ=fm['type']; base={'atlas.component':'components','atlas.flow':'flows','atlas.infra':'infra','atlas.schema-info':'schema-info','atlas.business-concept':'business-concepts','atlas.standard':'standards','atlas.runbook':'runbooks','atlas.incident-learning':'incidents'}.get(typ)
    if not base:return True
    idx=root/'_curated'/base/'index.md'; text=idx.read_text() if idx.exists() else ''
    rel=p.relative_to(idx.parent).as_posix()
    if fm.get('status')=='archived': return fm.get('id') not in text and rel not in text
    # Empty scaffold has no concept pages; real/fixture concept pages must be listed unless under tests.
    return fm.get('id') in text or rel in text

def lint(root):
    root=root.resolve(); out=[]; types=load_types(root); reltypes=load_relationships(root); statuses=load_statuses(root); cats=load_standard_categories(root); ids={}
    governed=[]
    for p in sorted(root.rglob('*.md')):
        rel=p.relative_to(root)
        if any(x in rel.parts for x in ('.git','.venv')) or 'tests' in rel.parts: continue
        if SECRET_RE.search(p.read_text(errors='ignore')): out.append(issue('ATLAS019','ERROR',rel,'obvious secret pattern'))
        for target in unresolved_links(p,root): out.append(issue('ATLAS008','ERROR',rel,f'unresolved relative link: {target}'))
        if p.name in EXEMPT or 'reviews' in rel.parts or ('.claude' in rel.parts): continue
        if rel.parts and rel.parts[0] in {'_curated','_staging'} and rel.suffix=='.md':
            try: fm,body=parse_frontmatter(p)
            except Exception as e: out.append(issue('ATLAS001','ERROR',rel,str(e))); continue
            if fm is None: continue
            governed.append((p,rel,fm,body))
    # package separately
    try: pfm,_=parse_frontmatter(root/'package.md')
    except Exception as e: out.append(issue('ATLAS001','ERROR','package.md',str(e))); pfm=None
    if pfm:
        info=types.get(pfm.get('type'))
        if not info or info.get('status')!='active': out.append(issue('ATLAS002','ERROR','package.md','inactive/unknown type'))
        if pfm.get('package')!='teama': out.append(issue('ATLAS004','ERROR','package.md','package must equal teama'))
    for p,rel,fm,body in governed:
        typ=fm.get('type'); info=types.get(typ)
        if not info or info.get('status')!='active' or not allowed_folder(rel,info): out.append(issue('ATLAS002','ERROR',rel,'type inactive/unknown or wrong folder')); continue
        if info.get('status')=='reserved': out.append(issue('ATLAS005','ERROR',rel,'reserved type cannot have pages'))
        if fm.get('package')!='teama': out.append(issue('ATLAS004','ERROR',rel,'package must equal teama'))
        if rel.parts[0]=='_curated':
            ident=fm.get('id'); pref=info.get('id_prefix')
            if not pref or not valid_curated_id(ident,pref): out.append(issue('ATLAS003','ERROR',rel,'invalid curated id'))
            elif ident in ids: out.append(issue('ATLAS003','ERROR',rel,f'duplicate id also in {ids[ident]}'))
            else: ids[ident]=rel.as_posix()
            st=fm.get('status')
            if st not in statuses['curated_status']: out.append(issue('ATLAS006','ERROR',rel,'invalid curated status'))
            if st=='curated' and (not fm.get('reviewed_by') or not fm.get('last_reviewed') or not fm.get('evidence')): out.append(issue('ATLAS007','ERROR',rel,'curated page needs reviewer/date/evidence'))
            if st!='archived' and not index_contains(root,p,fm): out.append(issue('ATLAS013','ERROR',rel,'non-archived page missing from index'))
            if st=='archived' and not index_contains(root,p,fm): out.append(issue('ATLAS014','ERROR',rel,'archived page appears in normal index'))
            if typ=='atlas.standard':
                cat=fm.get('standard_category'); actual=rel.parts[2] if len(rel.parts)>3 else None
                if cat not in cats or actual!=cat: out.append(issue('ATLAS017','ERROR',rel,'standard category invalid or storage mismatch'))
            for sec in REQ_SECTIONS.get(typ,[]):
                m=re.search(rf'^## {re.escape(sec)}\s*\n(.*?)(?=^## |\Z)',body,re.M|re.S)
                if not m or not m.group(1).strip(): out.append(issue('ATLAS016','ERROR',rel,f'empty/missing section: {sec}'))
            lr=fm.get('last_reviewed')
            if lr and lr!='YYYY-MM-DD':
                try:
                    d=datetime.strptime(str(lr),'%Y-%m-%d').date()
                    if (date.today()-d).days>180: out.append(issue('ATLAS020','WARN',rel,'page review older than 180 days'))
                except ValueError: pass
        else:
            if not valid_staging_id(fm.get('id')): out.append(issue('ATLAS003','ERROR',rel,'invalid staging id'))
        for ev in fm.get('evidence') or []:
            if isinstance(ev,str) and not ev.startswith(('http://','https://')):
                ep=root/ev
                if not ep.exists(): out.append(issue('ATLAS015','ERROR',rel,f'evidence path does not resolve: {ev}'))
        for r in fm.get('relationships') or []:
            if not isinstance(r,dict): out.append(issue('ATLAS009','ERROR',rel,'relationship must be object')); continue
            rt=r.get('type'); conf=r.get('confidence')
            if rt not in reltypes: out.append(issue('ATLAS009','ERROR',rel,f'unknown relationship: {rt}'))
            if rt in REQ_KIND and r.get('kind') not in KINDS: out.append(issue('ATLAS011','ERROR',rel,'relationship kind required/invalid'))
            if conf not in statuses['relationship_confidence']: out.append(issue('ATLAS012','ERROR',rel,'invalid relationship confidence'))
            elif conf!='reviewed' and not str(r.get('note','')).strip(): out.append(issue('ATLAS012','ERROR',rel,'non-reviewed relationship needs explanatory note'))
    # local target validation after id collection
    for p,rel,fm,body in governed:
        if rel.parts[0]!='_curated': continue
        for r in fm.get('relationships') or []:
            if isinstance(r,dict) and r.get('confidence')=='reviewed':
                tgt=r.get('target','')
                if isinstance(tgt,str) and tgt.startswith('atlas-') and tgt not in ids:
                    out.append(issue('ATLAS010','ERROR',rel,f'reviewed local target missing: {tgt}'))
        if fm.get('type')=='atlas.component':
            for dep in fm.get('deployed_as') or []:
                if dep and dep not in ids: out.append(issue('ATLAS022','WARN',rel,f'deployed_as has no corresponding curated ID: {dep}'))
    # map drift
    import subprocess
    cp=subprocess.run([sys.executable,str(root/'scripts/rebuild_maps.py'),'--check','--root',str(root)],capture_output=True,text=True)
    if cp.returncode: out.append(issue('ATLAS018','ERROR','_curated/maps',cp.stdout.strip() or 'generated map drift'))
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('path',nargs='?',default='.'); ap.add_argument('--format',choices=['text','json'],default='text'); ap.add_argument('--warn-as-error',action='store_true'); a=ap.parse_args(); issues=lint(Path(a.path))
    if a.format=='json': print(json.dumps(issues,indent=2))
    else:
        for i in issues: print(f"{i['level']} {i['code']} {i['path']}: {i['message']}")
        print(f"{sum(i['level']=='ERROR' for i in issues)} error(s), {sum(i['level']=='WARN' for i in issues)} warning(s)")
    fail=any(i['level']=='ERROR' or (a.warn_as_error and i['level']=='WARN') for i in issues); raise SystemExit(1 if fail else 0)
if __name__=='__main__': main()
