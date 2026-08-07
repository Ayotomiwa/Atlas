from scripts.lib.maps import build_maps, stable_bytes

def test_maps_deterministic():
    a=build_maps("."); b=build_maps(".")
    assert {k:stable_bytes(v) for k,v in a.items()}=={k:stable_bytes(v) for k,v in b.items()}
