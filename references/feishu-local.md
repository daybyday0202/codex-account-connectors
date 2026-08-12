# Local Feishu MCP

The local setup matches the source Mac's model: a wrapper reads the App Secret from macOS Keychain and launches `@larksuiteoapi/lark-mcp@0.5.1` in user OAuth mode. The local user access token and refresh token are managed by Lark MCP on that Mac.

The default read-only tool set covers document raw content, wiki node lookup, sheet reads, and Bitable table/field/record search. Write and delete scopes are intentionally excluded from the portable setup. Add them only for a specific task after reviewing the risk.

The Feishu app must have `http://localhost:3333/callback` configured as an OAuth redirect URL. Run `python3 scripts/feishu_setup.py` on each Mac and complete authorization in that Mac's browser. The setup requests `offline_access`, so the access token can be refreshed automatically after its normal short lifetime. Reauthorization is only needed if the app permission is revoked, the refresh token is invalidated, or additional scopes are required.

Feishu is local per computer, not an account-level connector. Each computer stores its own App Secret in macOS Keychain and completes its own OAuth consent. No Feishu token or secret is copied by this repository.
