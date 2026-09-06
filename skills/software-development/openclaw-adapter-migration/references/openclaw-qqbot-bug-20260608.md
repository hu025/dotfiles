# OpenClaw QQBot Bug — Debug Session Transcript

**Date**: 2026-06-09
**Bug**: `Message processing failed: Cannot read properties of undefined (reading 'run')`
**Status**: CONFIRMED framework-level bug, NOT version/plugin issue

---

## Verified: NOT a version issue

- Tested: 2026.5.27, 2026.6.1, 2026.6.5-beta.2 — all fail identically
- Full clean uninstall + reinstall (1039 packages removed, 295 reinstalled) — still fails
- Downgrading from beta to stable — still fails
- Full restart with all old processes killed — still fails
- **Conclusion**: framework-level bug, not plugin or version issue

---

## Root Cause (2026-06-09 update)

`pluginRuntime.channel.reply` is `undefined` at dispatch time.

The sequence:
1. QQ message arrives via WebSocket → `gateway.js` → `processQqMessage()`
2. `core = await coreFactory(...)` creates core object (core IS valid)
3. `runtime = await getQQBotRuntime(pluginRuntime, core, runtime)` → sets `pluginRuntime` (pluginRuntime IS valid)
4. `pluginRuntime.channel` IS a valid object — but it has NO `.reply` property
5. `pluginRuntime.channel.reply.dispatchReplyWithBufferedBlockDispatcher(...)` → crash: `.reply` is undefined

The qqbot's `runtime.js` is a 9-line stub:
```javascript
let runtime = null;
export function setQQBotRuntime(next) {
    runtime = next;
    setOpenClawVersion(next.version);
}
export function getQQBotRuntime() {
    if (!runtime) throw new Error("QQBot runtime not initialized");
    return runtime;
}
```

`setQQBotRuntime()` IS called (so `runtime` is not null), but the object it sets has no `.reply`.

---

## Error origin chain

| Step | Code location | What happens |
|------|---------------|-------------|
| 1 | `gateway.js:~635` | `ws = new WebSocket(gatewayUrl)` connects |
| 2 | `gateway.js:~637` | `setQQBotRuntime()` called → runtime set |
| 3 | `gateway.js:~1291` | `pluginRuntime.channel.reply.dispatchReplyWithBufferedBlockDispatcher({...})` → **CRASH** |
| 4 | `gateway.js:~1628` | catch block logs "Message processing failed" |

**Failing call** (line ~1291):
```javascript
const dispatchPromise = pluginRuntime.channel.reply.dispatchReplyWithBufferedBlockDispatcher({
    ctx: ctxPayload, cfg,
    dispatcherOptions: { ... },
    ...
});
```

---

## Defensive fix (applied)

Add a guard BEFORE the failing call to surface the real `channel` keys:

```javascript
// 防御性检查：确保 channel.reply 存在
if (!pluginRuntime?.channel?.reply?.dispatchReplyWithBufferedBlockDispatcher) {
    const avail = pluginRuntime?.channel ? Object.keys(pluginRuntime.channel) : ['undefined'];
    log?.error(`[qqbot:${account.accountId}] FATAL: pluginRuntime.channel.reply is undefined. Available channel keys: ${JSON.stringify(avail)}`);
    throw new Error(`pluginRuntime.channel.reply is undefined — channel keys: ${JSON.stringify(avail)}`);
}
```

**File**: `~/.npm-global/lib/node_modules/@tencent-connect/openclaw-qqbot/dist/src/gateway.js`

Also add console.error in catch block (bypasses log system):
```javascript
catch (err) {
    const errStr = String(err);
    console.error('[qqbot:FATAL]', errStr, err?.stack ? '\n' + err.stack.split('\n').slice(0,10).join('\n') : '');
    log?.error(`[qqbot:${account.accountId}] Message processing failed: ${err}...`);
}
```

---

## Diagnosis commands

```bash
# Verify process is clean (should show exactly 2 PIDs: watchdog + child)
ps aux | grep openclaw | grep -v grep | awk '{print $2}'

# Find the failing call
grep -n 'dispatchReplyWithBufferedBlockDispatcher' \
  ~/.npm-global/lib/node_modules/@tencent-connect/openclaw-qqbot/dist/src/gateway.js

# Find error logging
grep -n 'Message processing failed' \
  ~/.npm-global/lib/node_modules/@tencent-connect/openclaw-qqbot/dist/src/gateway.js

# Live log tail
tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log | python3 -c "
import sys, json
for line in sys.stdin:
    line=line.strip()
    if not line: continue
    try:
        d=json.loads(line)
        print(d.get('time','')[:19],'|',d.get('message','')[:200])
    except: print(line[:200])
"
```

---

## Restart procedure (critical)

MUST kill ALL old processes or patches won't take effect:

```bash
pkill -9 -f 'openclaw ' 2>/dev/null; sleep 2
bash /home/saber/.hermes/openclaw-watchdog.sh &
sleep 25 && curl -s http://127.0.0.1:18888/health
ps aux | grep openclaw | grep -v grep | awk '{print $2}'  # should show exactly 2 PIDs
```

Why `pkill -f 'openclaw '` (trailing space): prevents killing unrelated processes.

---

## Why `core.channel.inbound` was the wrong hypothesis

Early investigation focused on `core.channel.inbound.run` in `monitor-*.js`, but:
- That call is in a DIFFERENT execution path (HTTP inbound, not WebSocket qqbot path)
- The qqbot path uses `pluginRuntime.channel.reply.dispatchReplyWithBufferedBlockDispatcher`
- `core` is valid; `pluginRuntime.channel` is valid; `pluginRuntime.channel.reply` is the actual undefined

The preflight check at line ~348 already detects this:
```javascript
if (pluginRuntime?.channel?.reply?.dispatchReplyWithBufferedBlockDispatcher) {
    log?.info(`[qqbot] Runtime module preflight: OK`);
} else {
    log?.error(`[qqbot] ⚠️ Runtime preflight: dispatchReply API 不可用...`);
}
```

---

## Workarounds attempted

| Attempt | Result |
|---------|--------|
| Downgrade openclaw 2026.6.5-beta.2 → 2026.6.1 | Still fails |
| Full clean reinstall | Still fails |
| Kill all old processes + restart | Still fails |
| Patching `monitor-*.js` guard | Would be overwritten on update |
| Patching `subsystem-*.js` guard | Same, hash changes per build |
| Defensive check in `gateway.js` | Applied, surfaces real error |

---

## Recommended fix

**Disable the openclaw qqbot channel entirely.** Hermes has a stable built-in Python QQBot adapter — use that instead. In `~/.openclaw/openclaw.json`:
```json
"channels": { "qqbot": {} }
```