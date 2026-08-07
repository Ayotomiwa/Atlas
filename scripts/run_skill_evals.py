#!/usr/bin/env python3
import argparse,sys,yaml
from pathlib import Path
REQ={'should_trigger','should_not_trigger','expected_reads','expected_writes','forbidden_actions','outcome_assertions'}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--deterministic',action='store_true'); a=ap.parse_args(); root=Path(__file__).resolve().parents[1]; errors=[]
    for p in sorted((root/'tests/skill-evals').glob('*.yaml')):
        d=yaml.safe_load(p.read_text()) or {}; missing=REQ-set(d)
        if missing: errors.append(f'{p.name}: missing {sorted(missing)}')
        skill=root/'.claude/skills'/p.stem/'SKILL.md'
        if not skill.exists(): errors.append(f'{p.name}: missing skill')
        else:
            text=skill.read_text()
            for s in d.get('must_contain',[]):
                if s not in text: errors.append(f'{p.name}: skill missing assertion text {s!r}')
            for s in d.get('must_not_contain',[]):
                if s in text: errors.append(f'{p.name}: forbidden text {s!r}')
    if errors:
        print('\n'.join(errors)); raise SystemExit(1)
    print(f'deterministic skill evals: PASS ({len(list((root/"tests/skill-evals").glob("*.yaml")))} skills)')
if __name__=='__main__': main()
