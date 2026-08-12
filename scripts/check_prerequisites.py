#!/usr/bin/env python3
"""Read-only preflight for installing the connector bundle."""

from __future__ import annotations

import importlib.util
import platform
import shutil
import subprocess


def main() -> int:
    print(f"platform: {platform.system()} {platform.machine()}")
    for command in ("python3", "codex", "security", "node", "pnpm"):
        print(f"{command}: {'ok' if shutil.which(command) else 'missing'}")
    print(f"imaplib: {'ok' if importlib.util.find_spec('imaplib') else 'missing'}")
    if shutil.which("codex"):
        result = subprocess.run(["codex", "mcp", "list"], text=True, capture_output=True, check=False)
        print("registered MCP servers:")
        print(result.stdout.strip() or "(none)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
