#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json
import os
import shlex
import subprocess
import sys
import tempfile


HOOK_ID = "atlas-questions"
HOOK_MARKER = f"--hook-id {HOOK_ID}"
IDLE_SCRIPT = Path(__file__).resolve().with_name("idle_reminder.py")
DEFAULT_SETTINGS = Path.home() / ".claude" / "settings.json"


class SettingsError(ValueError):
    pass


def _hook_command() -> str:
    arguments = [sys.executable, str(IDLE_SCRIPT), "--hook-id", HOOK_ID]
    return subprocess.list2cmdline(arguments) if os.name == "nt" else shlex.join(arguments)


def _load_settings(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SettingsError(f"{path}: settings must be valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise SettingsError(f"{path}: settings root must be an object")
    return value


def _notifications(settings: dict, *, create: bool) -> list:
    hooks = settings.get("hooks")
    if hooks is None and create:
        hooks = {}
        settings["hooks"] = hooks
    if hooks is None:
        return []
    if not isinstance(hooks, dict):
        raise SettingsError("settings hooks must be an object")
    notifications = hooks.get("Notification")
    if notifications is None and create:
        notifications = []
        hooks["Notification"] = notifications
    if notifications is None:
        return []
    if not isinstance(notifications, list):
        raise SettingsError("settings hooks.Notification must be a list")
    return notifications


def _is_ours(hook: object) -> bool:
    return isinstance(hook, dict) and HOOK_MARKER in str(hook.get("command") or "")


def _remove_entries(settings: dict) -> int:
    notifications = _notifications(settings, create=False)
    removed = 0
    retained_groups = []
    for group in notifications:
        if not isinstance(group, dict):
            raise SettingsError("each Notification hook group must be an object")
        handlers = group.get("hooks")
        if not isinstance(handlers, list):
            raise SettingsError("each Notification hook group requires a hooks list")
        retained = []
        for hook in handlers:
            if _is_ours(hook):
                removed += 1
            else:
                retained.append(hook)
        group["hooks"] = retained
        if retained:
            retained_groups.append(group)
    notifications[:] = retained_groups
    if removed and not notifications:
        hooks = settings.get("hooks")
        if isinstance(hooks, dict):
            hooks.pop("Notification", None)
            if not hooks:
                settings.pop("hooks", None)
    return removed


def _install_entry(settings: dict) -> None:
    notifications = _notifications(settings, create=True)
    group = next(
        (
            item
            for item in notifications
            if isinstance(item, dict) and item.get("matcher") == "idle_prompt"
        ),
        None,
    )
    if group is None:
        group = {"matcher": "idle_prompt", "hooks": []}
        notifications.append(group)
    handlers = group.get("hooks")
    if not isinstance(handlers, list):
        raise SettingsError("idle_prompt Notification group requires a hooks list")
    handlers.append(
        {
            "type": "command",
            "command": _hook_command(),
            "timeout": 10,
        }
    )


def _entries(settings: dict) -> list[tuple[str, dict]]:
    entries: list[tuple[str, dict]] = []
    for group in _notifications(settings, create=False):
        if not isinstance(group, dict) or not isinstance(group.get("hooks"), list):
            raise SettingsError("Notification hook groups must contain hooks lists")
        entries.extend(
            (str(group.get("matcher") or ""), hook)
            for hook in group["hooks"]
            if _is_ours(hook)
        )
    return entries


def _write_settings(path: Path, settings: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(settings, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
        os.replace(temporary, path)
    except Exception:
        try:
            Path(temporary).unlink()
        except OSError:
            pass
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manage the optional Atlas question idle reminder.")
    parser.add_argument("action", choices=("install", "check", "remove"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--settings", type=Path, default=DEFAULT_SETTINGS)
    args = parser.parse_args(argv)
    path = args.settings.expanduser().resolve()
    try:
        settings = _load_settings(path)
        if args.action == "check":
            entries = _entries(settings)
            if len(entries) != 1:
                print(f"Atlas question reminder is not cleanly installed ({len(entries)} entries found).")
                return 1
            matcher, hook = entries[0]
            if (
                matcher != "idle_prompt"
                or hook.get("command") != _hook_command()
                or not IDLE_SCRIPT.exists()
            ):
                print("Atlas question reminder points at a different or missing checkout; run install again.")
                return 1
            print(f"Atlas question reminder is installed in {path}.")
            return 0

        removed = _remove_entries(settings)
        if args.action == "install":
            _install_entry(settings)
            verb = "replace" if removed else "install"
            if args.dry_run:
                print(f"Would {verb} the Atlas question reminder in {path}.")
                return 0
            _write_settings(path, settings)
            print(f"Installed the Atlas question reminder in {path}.")
            return 0

        if args.dry_run:
            print(f"Would remove {removed} Atlas question reminder entr{'y' if removed == 1 else 'ies'} from {path}.")
            return 0
        if removed:
            _write_settings(path, settings)
        print(f"Removed {removed} Atlas question reminder entr{'y' if removed == 1 else 'ies'} from {path}.")
        return 0
    except (OSError, SettingsError) as exc:
        print(f"Atlas question reminder setup failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
