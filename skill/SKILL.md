---
name: codex-account-connectors
description: Set up and troubleshoot reusable account-level connections for Feishu, Gmail, and QQ Mail across Codex computers. Use when a user wants to migrate local MCP credentials, connect the same accounts on another computer, install the connector bundle, or check connector status.
metadata:
  short-description: Configure Feishu, Gmail, and QQ Mail for Codex
---

# Codex Account Connectors

Use this skill to configure the three mail/document services consistently on a new computer. The bundle never contains access tokens, app secrets, passwords, or QQ Mail authorization codes.

## Supported connection models

- Gmail: account-level Codex connector. Sign into the same Codex/OpenAI account and authenticate Gmail when prompted.
- Feishu: OAuth-backed MCP. The recommended account-level deployment is a remote HTTPS MCP server. A local Feishu MCP is machine-scoped and should only be used for development or a trusted single Mac.
- QQ Mail: local IMAP/SMTP MCP with the authorization code stored in macOS Keychain. To make it account-level, deploy the same server behind HTTPS and add OAuth/session storage; do not put the authorization code in a shared config file.

## Installation flow on a new computer

1. Read `references/install.md` and ask which services the user wants.
2. Run `scripts/check_prerequisites.py` for a read-only preflight.
3. Configure Gmail through the Codex connector UI or its existing connector flow. Never ask for a Gmail password.
4. For Feishu, prefer `templates/feishu-remote-mcp.toml` and follow `references/feishu-remote.md`. For local development, use `templates/feishu-local-mcp.toml` and re-authorize locally.
5. For QQ Mail, run the local setup script described in `references/qqmail.md`; the script validates IMAP/SMTP before storing credentials in Keychain.
6. Run `scripts/check_connectors.py` and report only account identifiers and connection status. Never print secrets.

## Safety rules

- Do not copy the source machine's `~/.codex/auth.json`, Keychain database, Feishu token, App Secret, or QQ authorization code.
- Keep Feishu write/delete tools disabled until the user explicitly asks for them. Read-only is the default for a new machine.
- Treat OAuth callback URLs and MCP HTTPS URLs as configuration, not credentials.
- Ask for confirmation immediately before destructive actions such as deleting Feishu records or mail.

## References

- `references/install.md`: cross-computer installation checklist.
- `references/feishu-remote.md`: remote Feishu OAuth MCP architecture and deployment contract.
- `references/qqmail.md`: QQ Mail IMAP/SMTP and Keychain setup.
- `references/gmail.md`: Gmail account connector setup and verification.
- `templates/`: sanitized configuration examples.
