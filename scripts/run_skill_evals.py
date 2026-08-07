#!/usr/bin/env python3
from pathlib import Path
import argparse, yaml
ROOT=Path(__file__).resolve().parents[1]
EXPECTED=['atlas-discover','atlas-impact','atlas-stage','atlas-onboard-service','atlas-onboard-standards','atlas-setup-repo','atlas-curate','implement-jira']
READONLY={'atlas-discover','atlas-impact'}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--deterministic',action='store_true'); ap.parse_args()
    errors=[]
    for n in EXPECTED:
        skill=ROOT/'.claude/skills'/n/'SKILL.md'; ev=ROOT/'tests/skill-evals'/f'{n}.yaml'
        if not skill.exists(): errors.append(f'missing skill {n}'); continue
        text=skill.read_text(encoding='utf-8')
        if n in READONLY and any(x in text.split('---',2)[1] for x in ['Write','Edit']): errors.append(f'{n} is not read-only')
        if not ev.exists(): errors.append(f'missing eval {n}')
        else:
            data=yaml.safe_load(ev.read_text(encoding='utf-8'))
            for key in ['should_trigger','should_not_trigger','expected_files','forbidden_actions','outcome_assertions']:
                if key not in data: errors.append(f'{n} eval missing {key}')
    curate=(ROOT/'.claude/skills/atlas-curate/SKILL.md').read_text(encoding='utf-8')
    for req in ['README.md','_template.md','index.md','status: proposed','Never merge']:
        if req not in curate: errors.append(f'atlas-curate missing contract {req}')
    setup=(ROOT/'.claude/skills/atlas-setup-repo/SKILL.md').read_text(encoding='utf-8')
    for marker in ['atlas:managed:start','atlas:managed:end','Preserve all existing content']:
        if marker not in setup: errors.append(f'atlas-setup-repo missing {marker}')
    if errors:
        print('\n'.join(errors)); return 1
    print('Deterministic skill evals passed'); return 0
if __name__=='__main__': raise SystemExit(main())
