# Install On Another Computer

This bundle is intentionally credential-free. Copy or unzip it on the target computer, then open the folder in Codex.

## Preflight

```bash
python3 scripts/check_prerequisites.py
```

The preflight checks Python, Codex CLI, Node.js/pnpm, macOS Keychain access, and whether the local MCP names are already registered. It does not contact any mail or Feishu API. Node.js 20 or newer and pnpm are required by the local Feishu MCP.

## Configure services

### Gmail

Gmail is an account-level Codex connector. In Codex Settings, open the connectors/apps section, choose Gmail, sign into the intended Google account, and approve the requested scopes. Do not use a Gmail password in a script.

### Feishu

This bundle uses a local MCP matching the source Mac. Run:

```bash
python3 scripts/feishu_setup.py
```

The setup asks for the Feishu App ID and App Secret, stores the App Secret in macOS Keychain, registers the local `feishu` MCP, and starts OAuth at `http://localhost:3333/callback`. Complete the Feishu consent page in the browser. The requested scope includes `offline_access`, so Lark MCP can refresh the short-lived user access token automatically. Each computer must complete this local authorization once; credentials are not copied between computers. Reauthorize only after revoking access, invalidating the refresh token, or adding scopes.

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
