import json,shutil,subprocess,sys
from pathlib import Path
from scripts.lib.maps import generate_maps
def test_empty_maps_have_metadata():
    root=Path(__file__).resolve().parents[2]; m=generate_maps(root); assert all(v['generated'] for v in m.values())
def test_map_check_clean():
    root=Path(__file__).resolve().parents[2]; cp=subprocess.run([sys.executable,str(root/'scripts/rebuild_maps.py'),'--check','--root',str(root)]); assert cp.returncode==0
