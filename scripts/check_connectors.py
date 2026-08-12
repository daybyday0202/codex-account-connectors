#!/usr/bin/env python3
"""Report local connector registration without printing secrets."""

from __future__ import annotations

import json
import shutil
import subprocess


def main() -> int:
    if shutil.which("codex"):
        result = subprocess.run(["codex", "mcp", "list"], text=True, capture_output=True, check=False)
        print(result.stdout.strip() or "No MCP servers registered.")
    else:
        print("Codex CLI not found; inspect the desktop app's MCP settings.")
    keychain = subprocess.run(
        ["security", "find-generic-password", "-a", "qqmail", "-s", "codex-qqmail", "-w"],
        text=True,
        capture_output=True,
        check=False,
    )
    if keychain.returncode == 0:
        try:
            print(f"qqmail keychain account: {json.loads(keychain.stdout)['email']}")
        except Exception:
            print("qqmail keychain entry: present")
    else:
        print("qqmail keychain entry: not configured")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
