#!/usr/bin/env python3
from pathlib import Path
import argparse, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.lib.maps import build_maps, stable_bytes

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); a=ap.parse_args()
    outdir=ROOT/'_curated/maps'; expected=build_maps(ROOT); drift=[]
    for name,obj in expected.items():
        p=outdir/name; data=stable_bytes(obj)
        if a.check:
            if not p.exists() or p.read_bytes()!=data: drift.append(str(p.relative_to(ROOT)))
        else: p.write_bytes(data)
    if drift:
        print('Map drift: '+', '.join(drift)); return 1
    print('Maps clean' if a.check else 'Maps rebuilt'); return 0
if __name__=='__main__': raise SystemExit(main())
