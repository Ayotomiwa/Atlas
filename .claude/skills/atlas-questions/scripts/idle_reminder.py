#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import hashlib
import json
import sys
import tempfile
import time


ATLAS_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ATLAS_ROOT))

from scripts.lib.query import AtlasQuery


def _mark_once(session_id: str, context_ids: list[str]) -> bool:
    state_dir = Path(tempfile.gettempdir()) / "atlas-question-reminders"
    state_dir.mkdir(parents=True, exist_ok=True)
    cutoff = time.time() - (7 * 24 * 60 * 60)
    for path in state_dir.glob("*.seen"):
        try:
            if path.stat().st_mtime < cutoff:
                path.unlink()
        except OSError:
            pass
    key = hashlib.sha256(
        f"{session_id}|{'|'.join(sorted(context_ids))}".encode("utf-8")
    ).hexdigest()
    marker = state_dir / f"{key}.seen"
    if marker.exists():
        return False
    marker.write_text("shown\n", encoding="utf-8")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--hook-id", default="atlas-questions")
    parser.parse_args(argv)
    try:
        event = json.load(sys.stdin)
        if event.get("hook_event_name") != "Notification" or event.get("notification_type") != "idle_prompt":
            return 0
        session_id = str(event.get("session_id") or "")
        cwd = event.get("cwd")
        if not session_id or not isinstance(cwd, str) or not cwd:
            return 0
        query = AtlasQuery(ATLAS_ROOT)
        result = query.questions(path=cwd, scope="local")
        questions = result.get("results") or []
        context = result.get("context") or {}
        repositories = context.get("repositories") or []
        components = context.get("components") or []
        verified_repository = any(item.get("locator_match") == "matched" for item in repositories)
        path_specific_components = [
            item for item in components if item.get("match_basis") == "repository_path"
        ]
        unique_path_component = bool(path_specific_components) and not (
            (context.get("ambiguous") or {}).get("components")
        )
        if not verified_repository and not unique_path_component:
            return 0
        context_ids = result.get("context_ids") or []
        if not questions or not context_ids or not _mark_once(session_id, context_ids):
            return 0
        shown = ", ".join(context_ids[:2])
        if len(context_ids) > 2:
            shown += f" and {len(context_ids) - 2} more"
        message = (
            f"Atlas has {len(questions)} curated open question(s) related to {shown}. "
            "Run /atlas-questions if you would like to help."
        )
        print(json.dumps({"systemMessage": message, "suppressOutput": True}))
    except Exception:
        # A background reminder must never disrupt or block a Claude session.
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
