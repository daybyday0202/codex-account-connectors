# Codex Account Connectors

Portable, credential-free setup bundle for connecting Codex to Feishu, Gmail, and QQ Mail.

This repository is intentionally safe to publish. It contains setup code and sanitized templates,
not any account token, Feishu App Secret, Google credential, mailbox password, or QQ authorization code.

## Install

```bash
git clone https://github.com/daybyday0202/codex-account-connectors.git
cd codex-account-connectors
./install_local.sh
python3 scripts/check_prerequisites.py
```

Alternatively download a versioned ZIP from the repository's Releases page and run the same commands.

Then follow `skill/references/install.md`.

## What this package does

- Documents Gmail account-level authentication through the Codex connector.
- Documents remote HTTPS Feishu MCP with OAuth for cross-computer use.
- Provides a local read-only QQ Mail IMAP MCP and Keychain setup helper.
- Never includes tokens, app secrets, passwords, or QQ authorization codes.

## Important

The Feishu remote server and QQ Mail cloud gateway are deployment choices, not files that can safely be copied with credentials. The templates contain placeholders only.

This repository includes a local read-only QQ Mail MCP for macOS. The installer registers it with Codex and the setup helper stores the QQ authorization code in Keychain.

## Release model

Versioned GitHub Releases contain the same credential-free source bundle. Each new version should be
installed on the target computer after reviewing its release notes.
