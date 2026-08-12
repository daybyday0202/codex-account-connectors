#!/bin/sh
set -eu

BUNDLE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
CODEX_ROOT=${CODEX_HOME:-"$HOME/.codex"}
SKILL_TARGET="$CODEX_ROOT/skills/codex-account-connectors"

mkdir -p "$SKILL_TARGET"
cp -R "$BUNDLE_DIR/skill/." "$SKILL_TARGET/"

if command -v codex >/dev/null 2>&1; then
  if ! codex mcp get qqmail >/dev/null 2>&1; then
    codex mcp add qqmail -- python3 "$BUNDLE_DIR/scripts/qqmail_server.py"
  fi
fi

printf '%s\n' "Installed skill: $SKILL_TARGET"
printf '%s\n' "Local QQ Mail MCP: qqmail"
printf '%s\n' "Configure QQ Mail with: python3 $BUNDLE_DIR/scripts/qqmail_setup.py your-address@qq.com"
printf '%s\n' "Gmail is configured through the Codex connector UI."
printf '%s\n' "Feishu cross-computer use requires a deployed HTTPS OAuth MCP endpoint; see references/feishu-remote.md."
