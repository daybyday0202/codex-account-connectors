# Feishu OAuth MCP (optional remote alternative)

## Why remote

A local Feishu MCP is the default in this bundle and matches the source Mac setup. A remote MCP is an optional alternative for teams that later want a shared HTTPS service.

## Server contract

The deployed service must provide:

- MCP Streamable HTTP endpoint, e.g. `https://feishu-mcp.example.com/mcp`.
- OAuth authorization and callback endpoints.
- Per-user encrypted storage for Feishu user access/refresh tokens.
- Feishu API calls made only on behalf of the authenticated user.
- No hard-coded user token or App Secret in the client bundle.

## Feishu developer console

Add the cloud callback URL to the app's security settings. Keep the callback URL HTTPS and exact. Retain only the scopes needed by the tools. A conservative read/write set is:

```text
docs:doc docs:document:import docs:document:export docx:document:readonly wiki:wiki search:docs:read sheets:spreadsheet base:table:read base:field:read base:record:retrieve base:record:create base:record:update
```

Enable `base:record:delete` only when the user explicitly needs deletion.

## Codex client

```bash
codex mcp add feishu-cloud --url https://feishu-mcp.example.com/mcp
codex mcp login feishu-cloud
codex mcp get feishu-cloud
```

The first command is client configuration; the second opens OAuth. Repeat `codex mcp login feishu-cloud` on each Codex installation that needs access. If the server advertises OAuth scopes, Codex prefers those scopes.

## Deployment note

This bundle does not deploy the Feishu server because deployment requires a hosting account, domain, app secret, token database, and a choice of runtime. Do not pretend that a local stdio process is account-level.
