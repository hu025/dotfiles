# OpenClaw + Hermes Dual Agent Architecture (saber's system)

## Architecture Overview (2026-05-08 — FULLY INDEPENDENT)

saber's system runs **two completely independent AI agent processes** with no shared tools or subprocess bridges:

```
OpenClaw (Node.js, port 18789)
├── Primary LLM: MiniMax-M2.7 (via minimax provider)
├── QQ Bot platform adapter (openclaw-qqbot plugin)
├── TTS via MiniMax (speech-2.8-hd)
└── hermes-integration: REMOVED (decoupled 2026-05-08)

Hermes Gateway (Python, port 18799)
├── MiniMax provider
├── WeChat platform adapter (独立)
├── Agent loop (delegation, cron, skills)
└── Web Dashboard on port 18792
```

**重要变化 (2026-05-08)**: `hermes-integration` 插件已从 OpenClaw 中移除。两套系统现在完全独立运行，不再通过 subprocess 调用共享工具。

---

**⚠️ CRITICAL PITFALL (2026-05-08): 双重 QQ Bot 导致重复响应**

如果 OpenClaw (port 18789) 和 Hermes Gateway (port 18799) 的 QQ Bot 适配器同时启用，双方都会接收并响应同一条 QQ 消息——用户收到两条相同回复。

**症状**: 日志中完全相同的 C2C 消息同时到达两个 gateway。用户发送一条消息，收到两条回复。

**根因**: Hermes Gateway 有自己的 `qqbot` 适配器。当两个 gateway 都启用 QQ Bot 时，它们各自独立连接同一个 QQ Bot 账号。

**修复**: 选择其中一个处理 QQ Bot：
- **方案 A** (推荐): 只用 OpenClaw 处理 QQ，禁用 Hermes 的 QQ 适配器
- **方案 B**: 只用 Hermes 处理 QQ，停止 OpenClaw

```bash
# 方案 A: 禁用 Hermes QQ 适配器（编辑配置重启即可）

# 方案 B: 停止 OpenClaw
pkill -f "openclaw.*gateway --port 18789"
# Hermes Gateway 单独处理 QQ
```

**验证**: 发送一条 QQ 消息，应该只收到一条回复。

---

如需恢复工具调用（不推荐）：
```bash
# Add back hermes-integration to openclaw.json plugins.entries
# 然后重启 OpenClaw
```

## Key Paths

| Component | Path | Port |
|-----------|------|------|
| OpenClaw main | `/home/saber/.npm-global/lib/node_modules/openclaw/` | 18789 |
| Hermes Gateway | `~/.hermes/hermes-agent/` (git clone) | 18799 |
| Hermes Python tools source | `/home/saber/workspace/hermes_python_src/` | — |
| Hermes-integration plugin | `~/.openclaw/extensions/hermes-integration/` | — |
| hermes-integration build | `~/.openclaw/extensions/hermes-integration/dist/index.js` | — |

## Ports Summary

| Port | Service |
|------|---------|
| 18789 | OpenClaw Gateway (QQ Bot + hermes-integration) |
| 18799 | Hermes Gateway (WeChat + LLM agent) |
| 18792 | Hermes Web Dashboard |

Check: `ss -tlnp | grep -E "18789|18799|18792"`

## Processes

```
ps aux | grep -E "openclaw|hermes" | grep -v grep
```

Typical output:
```
saber  35772  ... /usr/bin/node ... openclaw dist/index.js gateway --port 18789
saber  41883  ... /bin/bash ... gateway-watchdog.sh
saber  41884  ... .../venv/bin/python -m hermes_cli.main gateway run --replace
```

## How hermes-integration Worked (NOW REMOVED)

Previously:
1. OpenClaw loaded `hermes-integration` plugin at startup
2. Plugin read `global._hermesToolRegistry` populated by openclaw internals
3. Each tool called `callPy(tool, func, args)` → spawned `python3 -c "from tools.{tool} import {func}; print(json.dumps(...))"`
4. Python path pointed to `/home/saber/workspace/hermes_python_src`

This created a soft dependency: OpenClaw's LLM could invoke Hermes Python tools via subprocess.

**现状**: 2026-05-08 已移除。现在 OpenClaw 和 Hermes Gateway 完全独立，无共享工具。

## Decoupling Procedure (已执行)

从 OpenClaw 移除 hermes-integration：
```bash
# 1. 编辑 openclaw.json，移除 hermes-integration
python3 -c "
import json
with open('/home/saber/.openclaw/openclaw.json') as f:
    d = json.load(f)
if 'plugins' in d:
    d['plugins']['allow'] = [x for x in d['plugins'].get('allow',[]) if x != 'hermes-integration']
    d['plugins']['entries'].pop('hermes-integration', None)
with open('/home/saber/.openclaw/openclaw.json','w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
"

# 2. 重启 OpenClaw
pkill -f "openclaw.*gateway --port 18789"
openclaw gateway --port 18789 &
```

## WeChat Issue: Session Expiry + No TTY for QR Login

Hermes Gateway handles WeChat. When the WeChat session expires:
- Gateway logs show `qr_login` being triggered every minute
- `qr_login` needs a TTY to render the QR code
- In systemd service, there's no TTY → QR code can't be scanned
- Manual fix: stop gateway, run `hermes gateway` interactively to scan QR, restart

## Update Strategy

When updating Hermes Agent via git:
```bash
cd ~/.hermes/hermes-agent
git fetch origin main --depth=1  # shallow fetch, avoids large history
git log --oneline FETCH_HEAD ^HEAD  # what am I about to pull?
# If satisfied:
git reset --hard FETCH_HEAD
pip install -e . --quiet
systemctl --user restart hermes-gateway.service
```

After any code update to hermes-agent, `pip install -e .` is required to pick up changes (editable install).

## OpenClaw Crashes After Running — Manual Restart Required

**Symptom**: OpenClaw process dies silently after running for a while. `ps aux | grep openclaw` shows nothing, `ss -tlnp | grep 18789` shows no listener.

**Root cause**: OpenClaw's `cleanStaleGatewayProcessesSync` race condition can still kill the process even with `Restart=no` in systemd. The process also appears to be killed by some internal error that doesn't produce crash logs.

**Restart procedure** (use `background=true` terminal, not `nohup &`):
```
terminal(background=true, command="openclaw gateway --port 18789", watch_patterns=["Gateway ready", "started", "listening", "ERROR", "Traceback"])
```
Then verify with `sleep 8 && curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:18789/` → 200.

**Why nohup & fails**: The tool disallows foreground `&` backgrounding. Must use `background=true`.

**Long-term fix**: The watchdog script at `~/.hermes/gateway-watchdog.sh` with its own systemd service (`hermes-gateway-watchdog.service`) handles Hermes Gateway restarts but NOT OpenClaw restarts. If OpenClaw keeps dying, the watchdog approach needs to be extended to cover OpenClaw too.

---

## OpenClaw Event Loop Latency Warnings (Non-Fatal)

OpenClaw may emit `liveness warning` with `eventLoopDelayMaxMs` up to 7000ms under heavy load (e.g., running QQ Bot automation). This is **not a crash** — the process continues running. The gateway remains responsive; responses are just delayed.

- `eventLoopDelayP99Ms=20-30ms` normal → ignore
- `eventLoopDelayMaxMs=1000-7000ms` under load → observe, no action needed unless responses fail

If you need clean state: `pkill -f "openclaw.*gateway --port 18789"` then restart.

---

## Current Process State (2026-05-08 下午)

```
OpenClaw   pid 45676  port 18789  ✅  HTTP 200
Hermes     pid 44956  port --     进程存在但未监听端口（gateway run 方式启动，QQ Bot 已停用）
```

**Recommended configuration**: OpenClaw handles QQ only, Hermes Gateway handles WeChat only. They are true siblings with no shared state.

---

- hermes-integration plugin at `~/.openclaw/extensions/hermes-integration/` is built TypeScript
- If only hermes-agent (gateway/agent) was updated, just `pip install -e .`
- If hermes-integration plugin itself was updated (new tools, API changes), rebuild it:
  ```bash
  cd ~/.openclaw/extensions/hermes-integration
  npm run build
  systemctl --user restart hermes-gateway.service
  ```
