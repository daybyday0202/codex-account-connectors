# Install On Another Computer

This bundle is intentionally credential-free. Copy or unzip it on the target computer, then open the folder in Codex.

## Preflight

```bash
python3 scripts/check_prerequisites.py
```

The preflight checks Python, Codex CLI, macOS Keychain access, and whether the local MCP names are already registered. It does not contact any mail or Feishu API.

## Configure services

### Gmail

Gmail is an account-level Codex connector. In Codex Settings, open the connectors/apps section, choose Gmail, sign into the intended Google account, and approve the requested scopes. Do not use a Gmail password in a script.

### Feishu

For one Mac, a local MCP is enough. For cross-computer use, deploy an HTTPS Streamable HTTP MCP server with per-user Feishu OAuth. See `feishu-remote.md` and `templates/feishu-remote-mcp.toml`.

### QQ Mail

Run the bundled local setup after enabling IMAP/SMTP in QQ Mail:

```bash
python3 scripts/qqmail_setup.py your-address@qq.com
```

The setup prompts for the QQ Mail authorization code, verifies both IMAP and SMTP, and stores the credential in the macOS Keychain service `codex-qqmail`. It never writes the code to a file.

## Verify

```bash
python3 scripts/check_connectors.py
```

Then restart Codex and test one read-only operation per service.
