# QQ Mail

## Local mode

QQ Mail normally uses IMAP/SMTP plus an authorization code rather than a personal OAuth flow.

1. In QQ Mail web settings, enable IMAP/SMTP.
2. Generate the mailbox authorization code.
3. Run:

```bash
python3 scripts/setup_qqmail_keychain.py your-address@qq.com
```

The script connects to `imap.qq.com:993` and `smtp.qq.com:465`, then stores `{email, password}` in macOS Keychain under service `codex-qqmail` and account `qqmail`.

## Account-level mode

To use QQ Mail on multiple computers without repeating setup, deploy a private HTTPS mailbox gateway. The gateway should expose MCP over Streamable HTTP, authenticate Codex users with OAuth, and store each user's QQ authorization code in an encrypted server-side secret store. Do not place the authorization code in a shared TOML file, Git repository, or plugin archive.

## Limitations

The local bundle is read-only: folders, search, and message reading. Add send/archive/delete only after explicit user approval and separate tool policy review.
