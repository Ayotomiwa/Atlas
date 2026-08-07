#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib.maps import MapBuildError, build_maps, stable_bytes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", default=str(ROOT), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    try:
        expected, diagnostics = build_maps(root, include_diagnostics=True)
    except MapBuildError as exc:
        print(f"Map generation failed: {exc}", file=sys.stderr)
        return 1

    outdir = root / "_curated" / "maps"
    outdir.mkdir(parents=True, exist_ok=True)
    drift: list[str] = []
    for name, obj in expected.items():
        path = outdir / name
        data = stable_bytes(obj)
        if args.check:
            if not path.exists() or path.read_bytes() != data:
                drift.append(str(path.relative_to(root)))
        else:
            path.write_bytes(data)

    for diagnostic in diagnostics:
        print(f"INFO unprojected relationship: {diagnostic.render()}")

    if drift:
        print("Map drift: " + ", ".join(drift))
        return 1
    print("Maps clean" if args.check else "Maps rebuilt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
