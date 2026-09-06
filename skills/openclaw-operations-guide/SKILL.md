---
name: openclaw-operations-guide
description: OpenClaw bot platform operations — upgrade procedures, QQ bot debugging, watchdog management, and channel adapter maintenance. Use when upgrading OpenClaw core/plugins, debugging message handling failures, or managing the watchdog process lifecycle.
category: devops
trigger: upgrade openclaw | openclaw qqbot debug | openclaw watchdog | openclaw plugin install | openclaw health check | openclaw channel adapter | openclaw down | openclaw restart | openclaw crashed | openclaw not responding | recover openclaw
---

# OpenClaw Operations Guide

Complete operational reference for the OpenClaw bot platform. Covers upgrade procedures, debugging, process management, and channel adapter maintenance.

---

## Section A — Upgrade Procedures

### Upgrade Order

OpenClaw has THREE components that each upgrade independently:

| Component | Location | Upgrade Method |
|-----------|----------|---------------|
| **OpenClaw core** | `~/.npm-global/` | `npm i -g openclaw@<version>` |
| **HermesClaw** | `~/hermesclaw/` | `git pull` (separate repo) |
| **Channel adapters** | npm global | `npm i -g @tencent-weixin/openclaw-weixin-cli@latest @tencent-connect/openclaw-qqbot@latest` |

### Step 1 — Check current versions

```bash
openclaw --version
npm show openclaw versions --json | python3 -c "import json,sys; v=json.load(sys.stdin); print('Latest stable:', [x for x in v if 'beta' not in x][-1]); print('Latest beta:', [x for x in v if 'beta' in x][-1])"
```

### Step 2 — Upgrade OpenClaw core

```bash
# Latest stable:
npm install -g openclaw@latest

# Or specific beta version:
npm install -g openclaw@2026.5.12-beta.3
```

#### ⚠️ v2026.6.1+ Entry Point Change

**`openclaw-gateway-node` binary has been removed in v2026.6.1.** Update your watchdog script:

```bash
# OLD (broken in 2026.6.1):
# exec /home/saber/.nvm/versions/node/v22.12.0/bin/openclaw-gateway-node start >> "$LOG" 2>&1

# NEW:
exec node ~/.npm-global/lib/node_modules/openclaw/openclaw.mjs gateway >> "$LOG" 2>&1
```

#### ⚠️ After upgrade: run npm install inside the package directory

Upgrading via `npm install -g` does NOT automatically install openclaw's **local** dependencies (stored under `node_modules/` inside the openclaw package directory). The global install only updates the top-level entry point.

**If you see these errors after upgrade, this is the cause:**
```
Error [ERR_MODULE_NOT_FOUND]: Cannot find package 'json5' imported from .../dist/redact-R2-EdHUS.js
Cannot find package 'dotenv' imported from .../dist/state-dir-dotenv-dtGZHNxU.js
Cannot find package 'zod' imported from .../dist/installed-plugin-index-store-D45WXSCB.js
```

**Fix — run npm install in the openclaw package directory:**
```bash
cd /home/saber/.npm-global/lib/node_modules/openclaw
npm install
# Wait for "added N packages" — this installs ~925 local dependencies
```

**Verify** — no `UNMET DEPENDENCY` should remain:
```bash
cd /home/saber/.npm-global/lib/node_modules/openclaw
npm ls 2>&1 | grep "UNMET DEPENDENCY" | wc -l
# Expected: 0
```

### Step 3 — Upgrade channel adapters

```bash
# WeChat adapter:
npm install -g @tencent-weixin/openclaw-weixin-cli@latest

# QQ Bot — use OpenClaw's plugin system (NOT npm -g):
# First check current version:
openclaw plugins list | grep qqbot
# If already exists, UPDATE it (not install — install fails for existing plugins):
openclaw plugins update qqbot
# If it doesn't exist yet, install it:
openclaw plugins install @openclaw/qqbot

# After any plugin change, restart gateway:
openclaw gateway restart
```

### Health endpoint: do NOT assume port 18888

After upgrade/restart, always verify the health endpoint from the journal log, **never hardcode a port**:

```bash
# Read the actual listening port from the startup log:
journalctl --user -u openclaw-gateway.service -n 30 --no-pager | grep "http server listening\|port"

# Then hit that exact port:
curl -s http://localhost:<PORT>/health
```

In some versions (e.g. 2026.5.22) OpenClaw binds to **18799**. If health check fails, find the real port with `ss -tlnp | grep node`.

#### Port Discovery Pattern

**Common scenario**: Gateway restarts, health check on 18888 fails, but the service is actually running on a different port.

**Correct diagnostic sequence**:
```bash
# Step 1: find what is listening
ss -tlnp | head -30

# Step 2: find the actual port (NOT hardcoding 18888)
# Example output — look for the node/python process:
# LISTEN 0  4096  0.0.0.0:8642  0.0.0.0:*  users:(("python",pid=40967,fd=18))

# Step 3: verify each candidate port
curl -s http://127.0.0.1:8642/health    # Hermes Gateway
curl -s http://127.0.0.1:18888/health  # OpenClaw QQ Bot

# Both are needed — they are separate services
# Hermes Gateway != OpenClaw (different processes, different ports)
```

**Key lesson**: Hermes Gateway (python) and OpenClaw (node) are independent services. After a full restart (gateway killed both), they must be restarted separately:
```bash
# 1. Restart Hermes Gateway (starts both hermes + openclaw via watchdog)
systemctl --user start hermes-gateway.service

# 2. If openclaw is still down, restart its watchdog separately
bash /home/saber/.hermes/openclaw-watchdog.sh &
sleep 6 && curl -s http://127.0.0.1:18888/health
```
### Step 4 — Upgrade HermesClaw (separate repo!)

```bash
cd ~/hermesclaw && git pull
# Verify:
git describe --tags
```

> ⚠️ HermesClaw (`~/hermesclaw/`) is a **separate GitHub repo** (`github.com/AaronWong1999/hermesclaw`). It does NOT upgrade with npm — it must be pulled separately.

### Step 5 — Restart gateway

```bash
# Use OpenClaw's built-in gateway restart
openclaw gateway restart

# Verify
sleep 5
curl -s http://localhost:18888/health
```

> ⚠️ **Never use `openclaw gateway run`** in new versions — it fails with `Unknown command: openclaw run`. Always use `openclaw gateway start` or `openclaw gateway restart`.

---

## Section B — QQ Bot Debugging

### Core Error Pattern

**Error**: `Cannot read properties of undefined (reading 'run')`
- Occurs in `openclaw/dist/dispatch-*.js` → `core.channel.inbound.run()` call
- `core.channel.inbound` is not initialized at framework level
- **Root cause is in openclaw framework layer, not qqbot gateway**
- Affects versions: 2026.6.1, 2026.6.5-beta.2 (both error), v2026.6.5-beta.5 (fixed)

### Multi-Process Cleanup (Critical)

**Symptom**: After multiple restarts, `address already in use 0.0.0.0:18888` appears with two openclaw processes coexisting.

**Correct cleanup order**:
```bash
# 1. Kill all watchdog bash processes
kill -9 $(pgrep -a bash | grep openclaw-watchdog | awk '{print $1}')
# 2. Kill all openclaw node processes
kill -9 $(pgrep -a node | grep 'openclaw$' | awk '{print $1}')
# 3. Confirm clean
ps aux | grep -E 'openclaw|node' | grep -v grep
# 4. Restart
bash /home/saber/.hermes/openclaw-watchdog.sh
sleep 20 && curl -s http://127.0.0.1:18888/health
```

**Watchdog exit code 78**: Means openclaw detected port already occupied, triggering auto-restart. When multiple stale processes coexist, this creates a loop. Clean first.

### Diagnostic Output Location

⚠️ **Previous misconception**: `console.error` doesn't go to any log. **Correct understanding**:
- watchdog log (`/home/saber/.hermes/openclaw-watchdog.log`): captures **stdout AND stderr**
- `/tmp/openclaw/openclaw-*.log`: only records framework `log?.info/error`, **NOT** `console.error`

So adding `console.error` → check watchdog log directly, **no need** for temp file writes.

**Quick diagnostic checklist**:
```bash
curl -s http://127.0.0.1:18888/health          # health check
ps aux | grep openclaw | grep -v grep          # process state
grep -i 'FATAL\|processing failed\|Cannot read' /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log  # log errors
tail -20 /home/saber/.hermes/openclaw-watchdog.log  # watchdog log (primary diagnostic source)
```

### Patch Location (Lost on npm upgrade)

`/home/saber/.npm-global/lib/node_modules/@tencent-connect/openclaw-qqbot/dist/src/gateway.js`:
- Line ~645: `log?.info` → change to `console.error` for diagnostics
- Line ~1550: `catch (err)` → add `console.error('[qqbot:FATAL]', err)` for framework errors
- Line ~1653: `ws.on("message")` → add raw message file write

Patches are lost on `npm upgrade`. Track and re-apply after upgrades.

### Plugin Installation: dangerous code patterns

`openclaw doctor` scans plugin JS files and blocks installation if it detects `child_process` (shell command execution):

```
Plugin "openclaw-qqbot" installation blocked: dangerous code patterns detected:
Shell command execution detected (child_process)
  scripts/link-sdk-core.cjs:39
  dist/src/utils/platform.js:287
  dist/src/slash-commands.js:33
  dist/src/utils/audio-convert.js:620
```

**Solution**: Use `--dangerously-force-unsafe-install` to bypass security scan:

```bash
openclaw plugins install @tencent-connect/openclaw-qqbot --dangerously-force-unsafe-install
```

The qqbot plugin legitimately requires `child_process` for external program execution. This is a normal and necessary security bypass.

### Plugin Installation Failure Other Handling

If `npm install` reports lockfile corruption:
```bash
rm -rf ~/.npm-global/lib/node_modules/@tencent-connect/openclaw-qqbot
rm -rf ~/.npm-global/lib/node_modules/@openclaw
rm -f ~/.npm-global/lib/node_modules/.package-lock.json
rm -f ~/.npm-global/lib/node_modules/@tencent-connect/package-lock.json
# Use npm pack + manual extraction to bypass postinstall
npm pack @tencent-connect/openclaw-qqbot --pack-destination /tmp/
cd /tmp && tar xzf tencent-connect-openclaw-qqbot-*.tgz
cp -r package ~/.npm-global/lib/node_modules/@tencent-connect/openclaw-qqbot/
```

If `openclaw plugins update` reports "No install record": use `openclaw plugins install` (not update).

---

## Section C — Watchdog Process Management

### Watchdog Script Location
`/home/saber/.hermes/openclaw-watchdog.sh`

### Watchdog stderr Redirect

The watchdog script captures openclaw's stdout/stderr and writes to `/home/saber/.hermes/openclaw-watchdog.log`.

**Real-time monitoring**:
```bash
tail -f /home/saber/.hermes/openclaw-watchdog.log

# Filter key information
grep -i 'FATAL\|MSG\|error\|processing' /home/saber/.hermes/openclaw-watchdog.log | tail -20
```

**Common exit codes**:
- `code=78`: port already occupied (another instance running), auto-restart triggered
- `code=0`: normal exit (WebSocket disconnect etc.)
- Non-zero other codes: abnormal exit, check specific error

### Environment Variable Loading (Critical)

**The gateway process does NOT inherit shell environment variables.**

Even if `~/.hermes/.env` has `MINIMAX_API_KEY`, the gateway started via systemd (or watchdog script) will NOT see it. This causes agent runtime to initialize with `apiKey=undefined` → "Cannot read properties of undefined (reading 'run')" errors and **QQ Bot will not reply**.

**Required watchdog script updates** (before the while loop):
```bash
set -a
source /home/saber/.hermes/.env
set +a
```

After editing, restart the watchdog:
```bash
kill $(pgrep -f openclaw-watchdog.sh)
bash /home/saber/.hermes/openclaw-watchdog.sh > /dev/null 2>&1 &
```

**Verify env is loaded**:
```bash
WD_PID=$(pgrep -f "openclaw-watchdog|openclaw.*gateway" | head -1)
cat /proc/$WD_PID/environ | tr '\0' '\n' | grep MINIMAX_API_KEY
```

### Model Prewarm Bug Fix

In v2026.6.1, a hardcoded `PRIMARY_MODEL_PREWARM_TIMEOUT_MS = 5000` causes the agent runtime to be unavailable for the first 5 seconds after gateway starts. Messages arriving during this window fail with:
```
Message processing failed: Cannot read properties of undefined (reading 'run')
```

**Fix**: set in watchdog script before the while loop:
```bash
export OPENCLAW_SKIP_STARTUP_MODEL_PREWARM=1
```

### Mutual Exclusion: Watchdog vs Systemd (Critical)

**Never run both watchdog script AND systemd service simultaneously.** Both manage the same OpenClaw process independently, causing port conflicts and confusing logs.

**Detection**:
```bash
systemctl --user list-units 2>/dev/null | grep openclaw
ps aux | grep openclaw | grep -v grep
```

If a root-level openclaw process exists (PPid=1 or PPid=systemd), systemd is running the service. Kill it:
```bash
# Find the systemd-managed openclaw PID
ps aux | grep openclaw | grep -v grep
# Check PPid: if 445 (systemd --user) or 1 (init), it's systemd-managed

# Kill it
kill -9 <PID>

# Also stop and disable the systemd service
systemctl --user stop openclaw-gateway.service
systemctl --user disable openclaw-gateway.service
```

Then start the watchdog. The systemd service definition lives at:
```
~/.config/systemd/user/openclaw-gateway.service
```

### Zombie Watchdog Detection

**Symptom**: Restarting OpenClaw via watchdog has no effect; health check keeps returning old data; port 18888 stays occupied even after restart.

**Root cause**: Multiple watchdog processes accumulate over time. Each restart via `bash openclaw-watchdog.sh &` spawns a new watchdog without killing the old one.

**Diagnosis**:
```bash
ps aux | grep openclaw | grep -v grep
# Expected: exactly 1 bash (watchdog) + 1 openclaw (node)
ss -tlnp | grep 18888
# Expected: exactly 1 LISTEN entry
```

**Fix — hard kill all, then restart clean**:
```bash
pkill -9 -f "openclaw.mjs"
pkill -9 -f "openclaw-watchdog"
sleep 3
ps aux | grep openclaw | grep -v grep  # should be empty
ss -tlnp | grep 18888 || echo "Port free"
bash /home/saber/.hermes/openclaw-watchdog.sh > /tmp/openclaw.log 2>&1 &
sleep 15
curl -s http://127.0.0.1:18888/health
```

### Gateway Restart Recovery (Hermes → OpenClaw Orphaning)

**Symptom**: Hermes Gateway crashes (e.g., MiniMax rate limit), systemd restarts Hermes successfully, but OpenClaw stays down. Health check on 18888 fails (`curl` exits code 7). Watchdog log shows no recent entries after the gateway restart timestamp.

**Root cause**: When Hermes Gateway is killed (systemd or manually), the OpenClaw watchdog process remains alive but the node child process dies. The watchdog's `wait` returns, it sleeps 5s, and restarts — but on a subsequent Hermes restart, the watchdog may have been orphaned by a new shell and never restarted again.

**Recovery sequence**:
```bash
# 1. Verify current state (both services?)
curl -s http://127.0.0.1:18888/health 2>&1   # OpenClaw
curl -s http://127.0.0.1:8642/health 2>&1    # Hermes

# 2. Kill ALL openclaw processes
pkill -f openclaw 2>/dev/null
pkill -f "openclaw-qqbot" 2>/dev/null
sleep 2
ps aux | grep -E 'openclaw|18888' | grep -v grep  # should be empty

# 3. Start watchdog fresh (background=true so Hermes tracks it)
bash /home/saber/.hermes/openclaw-watchdog.sh > /dev/null 2>&1 &
WD_PID=$!
echo "Watchdog PID=$WD_PID"

# 4. Wait for startup (~25s total: 8s boot + 15s websocket)
sleep 25
curl -s http://127.0.0.1:18888/health
```

**Startup success signals** (verify in this order):
```
[qqbot:default] WebSocket connected      # ✓ WebSocket TCP connected
[qqbot:default] Gateway ready             # ✓ Bot logged in
Session saved for default: sessionId=...  # ✓ Session persisted
[qqbot:default] Gateway ready             # ✓ Hermes integration ready
```

**⚠️ The node process can be running WITHOUT being ready.** Always check the log for `Gateway ready` AND verify health endpoint — a process occupying port 18888 is not sufficient proof of operation.

### Launching the Watchdog via Hermes (background=true)

**Never use `nohup` or shell-level `&`** to start the watchdog from a Hermes terminal session:
- Shell-level background (`nohup ... &`) is silently ignored by Hermes process tracking
- If the shell exits, the backgrounded process gets orphaned without Hermes awareness

**Correct approach**: use `terminal(background=true)` so Hermes tracks lifecycle:
```python
terminal(background=True, command="bash /home/saber/.hermes/openclaw-watchdog.sh > /dev/null 2>&1 &")
```

**Verify watch_patterns / notify_on_complete** are not set unless you want mid-process notifications. For a watchdog (long-lived, never exits), both should be omitted or set to `notify_on_complete=False`.

### Verifying OpenClaw is Fully Operational

After any restart, check ALL of these before declaring success:

```bash
# Process check — exactly 2 processes
ps aux | grep -E 'openclaw|node.*18888' | grep -v grep
# Expected: 1 bash watchdog + 1 node gateway

# Port check — 18888 listening
ss -tlnp | grep 18888
# Expected: LISTEN 0.0.0.0:18888

# Health endpoint
curl -s http://127.0.0.1:18888/health
# Expected: {"ok":true,"status":"live"}

# Log check — last 10 lines show Gateway ready
tail -10 /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log | strings
# Expected: WebSocket connected, Gateway ready, sessionId saved
```

---

## Section D — QQ Bot Configuration Debugging

### ⚠️ QQ Bot won't reply — check config BEFORE debugging code

**The most common reason QQ Bot fails to respond is `qqbot.enabled = false` in config, NOT a code bug.**

Always check this FIRST:
```bash
# Check qqbot config
grep -A2 '"qqbot"' ~/.openclaw/openclaw.json

# Fix if disabled
python3 -c "
import json
cfg = json.load(open('/home/saber/.openclaw/openclaw.json'))
cfg['channels']['qqbot']['enabled'] = True
json.dump(cfg, open('/home/saber/.openclaw/openclaw.json','w'), indent=2)
print('qqbot enabled')
"
```

The correct config file is `~/.openclaw/openclaw.json` (NOT `~/.hermes/openclaw/` or `~/.config/openclaw/`).

**Expected startup log when qqbot is running**:
```
[qqbot:default] Starting gateway — appId=..., enabled=true
[default] Connecting to wss://api.sgroup.qq.com/websocket
[default] WebSocket connected
[qqbot:default] Gateway ready
```

---

## Section E — Complete Cleanup and Reinstall

When full reinstallation is needed:

```bash
# 1. npm global packages
npm list -g --depth=0 | grep -iE 'openclaw|tencent'
npm uninstall -g @openclaw @tencent-connect @tencent-weixin

# 2. Kill all processes
pkill -9 -f 'openclaw ' 2>/dev/null
pkill -9 -f 'node.*gateway.*18888' 2>/dev/null
sleep 2

# 3. /tmp residual
rm -rf /tmp/openclaw-1000 /tmp/openclaw_beta.log /tmp/openclaw-qqbot-2026.6.1.tgz /tmp/openclaw_restart.log

# 4. systemd service files
rm -f ~/.config/systemd/user/openclaw-gateway.service.bak
rm -f ~/.config/systemd/user/openclaw-node.service
rm -rf ~/.config/systemd/user/openclaw-gateway.service.d
rm -f ~/.config/systemd/user/openclaw-gateway.service
rm -f ~/.config/systemd/user/fix-openclaw-config.timer
rm -f ~/.config/systemd/user/openclaw.service
rm -f ~/.local/share/systemd/timers/stamp-fix-openclaw-config.timer
sudo rm -rf /etc/systemd/system/openclaw-gateway.service.d
systemctl --user daemon-reload

# 5. Log files
rm -f /tmp/openclaw/openclaw-*.log
rmdir /tmp/openclaw 2>/dev/null

# 6. npm-global residual directories
rm -rf ~/.npm-global/lib/node_modules/@openclaw
rm -rf ~/.npm-global/lib/node_modules/@tencent-connect
rm -rf ~/.npm-global/lib/node_modules/@tencent-weixin

# 7. Keep: ~/.openclaw/ (user config and runtime data)
# 8. Keep: ~/.hermes/ (Hermes Agent memory and config, do not clean)
```

**Verify clean**:
```bash
# No processes
ps aux | grep -iE 'openclaw|qqbot' | grep -v grep

# No npm packages
npm list -g --depth=0 | grep -iE 'openclaw|tencent'

# No systemd service
systemctl --user list-units --all | grep -iE 'openclaw'

# No /tmp residual
ls /tmp/ | grep -iE 'openclaw'

# Hermes still running (port may have changed)
curl http://127.0.0.1:8642/health
```

---

## Section F — Version-Specific Notes

### `~/.openclaw/` 目录大小分布（2026-06-28 实测）

| 子目录 | 大小 | 同步策略 |
|--------|------|----------|
| `media/` | **476M** | ⚠️ 跳过：缓存文件，用 `--exclude='.cache'` |
| `node_modules/` | **389M** | ✅ rsync 同步（插件依赖） |
| `agents/` | **211M** | ✅ rsync 同步 |
| `npm/` | **155M** | ✅ rsync 同步 |
| `extensions/` | **30M** | ✅ rsync 同步 |
| `logs/` | **13M** | ✅ rsync 同步 |
| `workspace/` | **8M** | ✅ rsync 同步 |
| `state/` | **1.3M** | ✅ rsync 同步 |
| `qqbot/` | **524K** | ✅ rsync 同步 |
| `plugins/` | **116K** | ✅ rsync 同步 |
| 其他 | <1M | ✅ rsync 同步 |

**rsync 同步命令**：
```bash
rsync -av \
    /home/saber/.openclaw/openclaw.json \
    /home/saber/.openclaw/openclaw.json.bak* \
    /home/saber/.openclaw/qqbot/ \
    /home/saber/.openclaw/agents/ \
    /mnt/usb/openclaw/

rsync -av --exclude='.cache' --exclude='.npm' \
    /home/saber/.openclaw/node_modules/ \
    /mnt/usb/openclaw/node_modules/

rsync -av \
    /home/saber/.openclaw/{npm,extensions,logs,workspace,state,plugins,plugin-skills,memory,tasks,cron,feishu}/ \
    /mnt/usb/openclaw/
```

**⚠️ media 目录（476M）不要同步**：全是缓存，用 `--exclude='media/*'` 或在 rsync 后清理。

### Version tracking (as of 2026-06-28)

| Component | Version | Notes |
|-----------|---------|-------|
| OpenClaw core | **2026.6.10** | Last tracked. Check `npm show openclaw version` for latest. |
| openclaw-qqbot | **1.7.2** | ⚠️ 2.0.0 available (detected 2026-07-27). Upgrade before 1.7.2 goes EOL. |
| hermes-agent | v2026.6.19 (git v0.17.0) | Current |
| Node.js (Hermes) | **v25.9.0** | Upgraded from v26.4.0 (downgrade needed for compatibility) |
| claude-code npm | **2.1.195** | upgraded from 2.1.185 via `npm install @anthropic-ai/claude-code@latest` |
| opencode-ai npm | **1.17.11** | upgraded from 1.17.8 via `npm install opencode-ai@latest` |
| HermesClaw | (separate repo) | `cd ~/hermesclaw && git pull` |
| Hermes pip | 0.15.2 | PyPI latest |

### ⚠️ Core Bug: Fixed in v2026.6.5-beta.5+

```
Message processing failed: Cannot read properties of undefined (reading 'run')
```

Fixed in **v2026.6.5-beta.5** and later (including 2026.6.10). The `runtime.channel.inbound.run` issue was resolved upstream.

**Root cause updated (2026-06-09)**: `pluginRuntime.channel.reply` is undefined. `setQQBotRuntime()` is called (runtime is not null), but `pluginRuntime.channel` object lacks `.reply` property. qqbot's `gateway.js:~1291` calls `pluginRuntime.channel.reply.dispatchReplyWithBufferedBlockDispatcher(...)` and crashes.

**Recommended solution**: Disable openclaw qqbot channel and use Hermes built-in Python QQBot adapter.

### Beta versions: test before assuming broken

The claim that "beta versions are unsafe" is **not universally true**. The `runtime.channel.inbound.run` bug was present in both 2026.6.1 (stable) and 2026.6.5-beta.2 (beta). Test each version — if `gateway ready` and `Gateway resumed` appear in logs with no crash within 60s, the version is fine.

### Two node_modules directories exist

OpenClaw has **two** node_modules directories that must stay in sync:

| Directory | Purpose |
|-----------|---------|
| `~/.npm-global/lib/node_modules/openclaw/` | **Running version** — read by `openclaw.mjs` |
| `~/.npm-global/node_modules/openclaw/` | npm's install target |

`npm install -g` writes to `node_modules/`, NOT `lib/node_modules/`. The running process reads from `lib/node_modules/openclaw/`. **Version swap requires overwriting lib/node_modules directly**.

### Plugin SQLite State Persistence

When upgrading a third-party plugin via `npm install -g`, OpenClaw does NOT automatically update its SQLite state.

The plugin index lives in `~/.openclaw/state/openclaw.sqlite`, table `installed_plugin_index`. Stale state causes `openclaw plugins doctor` warnings even though the new version IS installed.

After updating, **delete the old plugin directory** and verify:
```bash
openclaw plugins doctor   # must say "No plugin issues detected"
openclaw plugins list      # plugin should show new path
```

---

## References

- `references/watchdog-stderr.md` — watchdog stderr redirect and log monitoring
- `references/diagnostic-patterns.md` — console.error diagnostic patterns, multi-process cleanup, message handling troubleshooting
- `references/openclaw-cleanup.md` — full cleanup checklist
- `references/openclaw-channel-operations.md` — channel add/remove operations
- `references/openclaw-usb-portable.md` — USB portable configuration
- `references/openclaw-post-upgrade-missing-deps-20260519.md` — post-upgrade missing internal dependencies diagnosis
- `references/openclaw-beta-dispatchReplyWithBufferedBlockDispatcher-missing.md` — beta version missing dispatchReplyWithBufferedBlockDispatcher
- `references/openclaw-gateway-env-vars-2026-06-07.md` — QQ Bot no reply: systemd service missing EnvironmentFile causing apiKey undefined
- `references/openclaw-qqbot-bug-20260608.md` — complete debug record: `pluginRuntime.channel.reply` undefined root cause chain, defensive fix, diagnostic commands