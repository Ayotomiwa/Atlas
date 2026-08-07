#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from scripts.lib.maps import generate_maps
NAMES={'flow-component':'flow-component-map.json','repo-dependency':'repo-dependency-map.json','infra-dependency':'infra-dependency-map.json'}

def rendered(data): return (json.dumps(data,indent=2,sort_keys=True,ensure_ascii=False)+'\n').encode()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); ap.add_argument('--root',default='.')
    a=ap.parse_args(); root=Path(a.root).resolve(); maps=generate_maps(root); bad=False
    for key,name in NAMES.items():
        p=root/'_curated/maps'/name; b=rendered(maps[key])
        if a.check:
            if not p.exists() or p.read_bytes()!=b: print(f'MAP DRIFT: {p.relative_to(root)}'); bad=True
        else:
            p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(b)
    raise SystemExit(1 if bad else 0)
if __name__=='__main__': main()
