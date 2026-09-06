# Hermes MCP Server Configuration

## MCP Config Format (config.yaml)

**Correct format** — `command`/`args`/`env`:
```yaml
mcp_servers:
  <name>:
    command: "npx"           # or absolute path e.g. "/usr/bin/python3"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/saber"]
    env: {}                 # empty dict — NOT {KEY: VAL}
```

**Wrong format** — `type`/`args` split is NOT valid:
```yaml
# ❌ WRONG
mcp_servers:
  <name>:
    type: "stdio"    # 'type' key is not recognized
    args: ["..."]
```

## Installed Servers (2026-05-13)

| Server | Package | Args | Status |
|--------|---------|------|--------|
| filesystem | `@modelcontextprotocol/server-filesystem` | `/home/saber` | ✅ running, 14 tools |
| memory | `@modelcontextprotocol/server-memory` | — | ✅ running |
| everything | `@modelcontextprotocol/server-everything` | — | ✅ running |

All three are installed via npx and configured in `config.yaml`.

## Available MCP Servers

### github — needs token
```bash
# Requires: GITHUB_PERSONAL_ACCESS_TOKEN in ~/.hermes/.env
npm install -g @modelcontextprotocol/server-github
```
Tools: search_code, search_repositories, get_file_content, list_commits, etc.

### brave-search — deprecated
```bash
# BRAVE_API_KEY is deprecated at this endpoint
npm install -g @modelcontextprotocol/server-brave-search
```

### sqlite — unavailable
```bash
npm install @modelcontextprotocol/server-sqlite  # Returns 404
```

## Verify MCP Servers Are Running

After editing `config.yaml`, restart the gateway:
```bash
systemctl --user daemon-reload
systemctl --user reset-failed
systemctl --user start hermes-gateway.service
```

Check MCP tools are discovered:
```python
from hermes_cli.mcp_tool import discover_mcp_tools
tools = discover_mcp_tools()
print(f"MCP tools discovered: {len(tools)}")
```

Or check journalctl:
```bash
journalctl --user -u hermes-gateway.service -n 100 | grep -i "mcp\|discover"
```

## Troubleshooting

### MCP server won't start
1. Verify `command` is correct (full path or `npx`)
2. For `npx`, verify npx is in PATH in the systemd service environment
3. Check journalctl for the specific error

### MCP tools not appearing after restart
- Gateway must be fully restarted (`daemon-reload` + `reset-failed` + `start`)
- Old PID may still be running — verify with `ps aux | grep mcp`

### npx not in systemd PATH
The systemd service sets a custom `PATH`. npx must be reachable:
```ini
Environment="PATH=...:/home/saber/.npm-global/bin:..."
```
Verify with: `systemctl --user show hermes-gateway.service | grep PATH`