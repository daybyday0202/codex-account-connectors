#!/usr/bin/env python3
"""Configure a portable local Feishu/Lark MCP wrapper and start OAuth."""

from __future__ import annotations

import getpass
import json
import os
import subprocess
import sys
from pathlib import Path

SERVICE = "codex-feishu"
ACCOUNT = "app-secret"
SCOPE = "offline_access,docs:doc,docs:document:import,docs:document:export,docx:document:readonly,wiki:wiki,search:docs:read,sheets:spreadsheet,base:app:create,base:table:create,base:table:read,base:field:read,base:record:create,base:record:retrieve,base:record:update"
TOOLS = "preset.doc.default,preset.base.default,preset.base.batch,docx.v1.document.rawContent,wiki.v2.space.getNode,sheets.v3.spreadsheet.get,sheets.v3.spreadsheetSheet.query,bitable.v1.appTable.list,bitable.v1.appTableField.list,bitable.v1.appTableRecord.search"


def main() -> int:
    app_id = (sys.argv[1] if len(sys.argv) > 1 else input("飞书 App ID（cli_...）: ")).strip()
    if not app_id.startswith("cli_"):
        print("App ID 应以 cli_ 开头。", file=sys.stderr)
        return 2
    app_secret = getpass.getpass("飞书 App Secret（不会显示）: ")
    if not app_secret:
        print("App Secret 不能为空。", file=sys.stderr)
        return 2
    payload = json.dumps({"app_id": app_id, "app_secret": app_secret}, ensure_ascii=False)
    subprocess.run(["security", "delete-generic-password", "-a", ACCOUNT, "-s", SERVICE], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    subprocess.run(["security", "add-generic-password", "-a", ACCOUNT, "-s", SERVICE, "-w", payload], check=True)

    codex_root = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser()
    wrapper = codex_root / "bin" / "feishu-mcp"
    wrapper.parent.mkdir(parents=True, exist_ok=True)
    wrapper.write_text(f'''#!/bin/sh
set -eu
secret_json=$(security find-generic-password -a "{ACCOUNT}" -s "{SERVICE}" -w)
APP_ID=$(printf '%s' "$secret_json" | python3 -c 'import json,sys; print(json.load(sys.stdin)["app_id"])')
APP_SECRET=$(printf '%s' "$secret_json" | python3 -c 'import json,sys; print(json.load(sys.stdin)["app_secret"])')
PNPM_BIN=$(command -v pnpm || true)
if [ -z "$PNPM_BIN" ]; then echo "需要 pnpm，请先安装 Node.js/pnpm。" >&2; exit 1; fi
if [ "$#" -eq 0 ]; then
  set -- mcp --oauth --port 3333 --language zh --token-mode user_access_token --scope '{SCOPE}' --tools '{TOOLS}'
fi
export APP_ID APP_SECRET LARK_DOMAIN="https://open.feishu.cn" LARK_TOKEN_MODE="user_access_token"
exec "$PNPM_BIN" dlx @larksuiteoapi/lark-mcp@0.5.1 "$@"
''')
    wrapper.chmod(0o700)
    codex = subprocess.run(["which", "codex"], capture_output=True, text=True, check=False).stdout.strip()
    if codex:
        subprocess.run([codex, "mcp", "remove", "feishu"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        subprocess.run([codex, "mcp", "add", "feishu", "--", str(wrapper)], check=True)
    print("飞书 App Secret 已保存到 macOS 钥匙串。")
    print("即将打开飞书授权页，请在浏览器中完成本机 OAuth 授权。")
    try:
        subprocess.run(
            [str(wrapper), "login", "--host", "localhost", "--port", "3333", "--scope", SCOPE],
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        print(f"OAuth 授权失败（退出码 {exc.returncode}）。可稍后重新运行本脚本重试。", file=sys.stderr)
        return exc.returncode or 1
    print("飞书 OAuth 授权完成。offline_access 已启用，访问令牌过期后会自动刷新。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
