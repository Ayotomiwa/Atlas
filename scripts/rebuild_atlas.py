#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib.generated import build_index_outputs, build_page_view_outputs, generated_index_candidates
from scripts.lib.maps import MapBuildError, build_maps, curated_pages, map_output_paths, stable_bytes


def expected_outputs(root: Path) -> tuple[dict[Path, bytes], list]:
    pages = curated_pages(root)
    maps, diagnostics = build_maps(root, pages=pages, include_diagnostics=True)
    outputs: dict[Path, bytes] = {
        map_output_paths(root)[name]: stable_bytes(value) for name, value in maps.items()
    }
    outputs.update(build_index_outputs(root, pages=pages))
    outputs.update(build_page_view_outputs(root, compiled_maps=maps, pages=pages))
    return outputs, diagnostics


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Rebuild Atlas maps, catalogues and managed page views."
    )
    parser.add_argument("--check", action="store_true", help="report drift without writing")
    parser.add_argument("--root", default=str(ROOT), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    try:
        outputs, diagnostics = expected_outputs(root)
    except (MapBuildError, ValueError) as exc:
        print(f"Atlas generation failed: {exc}", file=sys.stderr)
        return 1

    drift: list[str] = []
    stale_indexes = sorted(
        generated_index_candidates(root) - {path.resolve() for path in outputs},
        key=lambda path: path.as_posix(),
    )
    for path, data in sorted(outputs.items(), key=lambda item: item[0].as_posix()):
        if args.check:
            if not path.exists() or path.read_bytes() != data:
                drift.append(path.relative_to(root).as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

    for path in stale_indexes:
        if args.check:
            drift.append(path.relative_to(root).as_posix())
        else:
            path.unlink()

    for diagnostic in diagnostics:
        print(f"INFO unprojected link: {diagnostic.render()}")
    if drift:
        print("Atlas generated drift: " + ", ".join(drift))
        return 1
    print("Atlas generated surfaces clean" if args.check else "Atlas generated surfaces rebuilt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
