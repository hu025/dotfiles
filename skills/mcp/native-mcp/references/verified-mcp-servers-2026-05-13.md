# Verified MCP Servers on This System

## Filesystem MCP Server

**Status**: ✅ Verified working (2026-05-13)

**Installation**:
```bash
npx -y @modelcontextprotocol/server-filesystem /home/saber
```

**Config** (`~/.hermes/config.yaml`):
```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/saber"]
    env: {}
```

**Discovered tools** (14 total):
- `mcp_filesystem_read_file`
- `mcp_filesystem_read_text_file`
- `mcp_filesystem_list_directory`
- `mcp_filesystem_create_directory`
- `mcp_filesystem_write_file`
- `mcp_filesystem_move_file`
- `mcp_filesystem_copy_file`
- `mcp_filesystem_delete_file`
- `mcp_filesystem_directory_tree`
- `mcp_filesystem_get_file_info`
- `mcp_filesystem_search_files`

**Process**: `node /home/saber/.npm/_npx/a3241bba59c344f5/node_modules/.bin/mcp-server-filesystem /home/saber`

---

## GitHub MCP Server

**Status**: ⚠️ Requires `GITHUB_PERSONAL_ACCESS_TOKEN`

**Config** (add when token is available):
```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_..."
```

**Token setup**: GitHub PAT with `repo` scope for full access. SSH key `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIC39Ac6MW1H5doAekiabKFbCnH2smhyIIo4fNjXwwFUD hermes-saber@local` is configured but MCP GitHub servers require PAT, not SSH.

---

## Available but Not Yet Configured

| Server | npm package | Status |
|--------|-----------|--------|
| `@context7/mcp-server` | Not published to npm (404) | Skip |
| `mcp-server` (Python) | `pip install mcp-server` | Not tested stdio transport |
| `@modelcontextprotocol/inspector` | Debug MCP connections | Optional |

---

## Quick Test Commands

```bash
# Verify filesystem MCP is running
ps aux | grep mcp-server-filesystem | grep -v grep

# Verify tools are discoverable (Python)
cd /home/saber/.hermes/hermes-agent
source venv/bin/activate
python3 -c "
import sys; sys.path.insert(0, '.')
from tools.mcp_tool import discover_mcp_tools
tools = discover_mcp_tools()
print(f'Discovered {len(tools)} MCP tools')
for t in tools: print(' ', t['name'])
"
```
