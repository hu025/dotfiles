---
name: openclaw-adapter-migration
description: Build or fix platform adapters (Discord, Telegram) using OpenClaw's architecture — @buape/carbon for Discord, plain gramJS v1.42 for Telegram. Includes version pinning gotchas and discovery methods.
---

# OpenClaw Adapter Migration Skill

## Context
When migrating or building platform adapters (Discord, Telegram, etc.) for a Gateway that uses OpenClaw's architecture, the approach differs significantly from naive SDK usage. This skill captures the discovered patterns from reverse-engineering OpenClaw v2.x source.

## Trigger Condition
Any time you need to build or fix a platform adapter that must coexist with or replicate OpenClaw's gateway architecture.

---

## Discord: @buape/carbon (NOT discord.js)

### Package
```
@buape/carbon@0.15.0
```
**Important**: v0.16.0 removed the `gateway` subpath export. Always pin to 0.15.0.

### Two-Part Architecture

**Part 1 — HTTP (Interactions):** `Client` from `@buape/carbon`
- Handles Discord's `/interactions` (SLASH_COMMANDS, buttons, modals) and `/events` (webhook pings)
- Constructor needs: `clientId`, `publicKey`, `token`, `baseUrl`
- The Client owns an internal Hono server with routes `/deploy`, `/interactions`, `/events`
- Does NOT expose the underlying HTTP server publicly
- For Gateway integration: need to route Discord HTTP callbacks through the Gateway's own HTTP server, then call `client.handleInteraction()` manually

**Part 2 — WebSocket (Gateway):** `GatewayPlugin` from `@buape/carbon/gateway`
- Manages WebSocket connection to `wss://gateway.discord.gg/`
- Handles opcodes 0 (Dispatch), 1 (Heartbeat), 7 (Reconnect), 10 (Hello), 11 (Heartbeat ACK)
- Handles session resume
- Constructor needs: `token` + `gatewayBot` (from `GET /gateway/bot`)

### Integration Pattern (discovered from OpenClaw source)
```
1. Create GatewayPlugin with token + gatewayBot info
2. GatewayPlugin.connect() starts WebSocket
3. Register message listeners via gatewayPlugin.registerListener(listener)
4. For HTTP: register /discord/interactions on the Gateway's own HTTP server,
   parse raw body + headers, call client.handleInteraction(rawBody, headers)
```

### Signature Verification
```typescript
import { createHmac, timingSafeEqual } from 'node:crypto';

function verifyDiscordRequest(
  rawBody: string,
  signature: string,
  timestamp: string,
  publicKey: string
): boolean {
  const payload = timestamp + rawBody;
  const expected = createHmac('sha256', publicKey)
    .update(payload, 'utf8')
    .digest('hex');
  const signatureBytes = Buffer.from(signature.replace('sha256=', ''), 'hex');
  return timingSafeEqual(
    Buffer.from(expected, 'hex'),
    signatureBytes
  );
}
```

---

## Telegram: gramJS v1.42 (plain, NO plugins)

### Package
```
grammy@^1.42.0
```

**Important**: Do NOT install `@grammyjs/conversations` or `@grammyjs/files` — these were for v1.21 and are not needed in v1.42.

### API Changes from v1.21 → v1.42

| v1.21 (REMOVED) | v1.42 |
|---|---|
| `bot.canUseWebhookMechanism` | Deleted entirely |
| `bot.api.setWebhook(url, { allowed_updates } )` | `allowed_updates` (snake_case, not camelCase) |
| `User.photo` | Deleted — construct avatar from `from.id`: `https://t.me/i/avatars/{id}/.jpg` |
| `@grammyjs/conversations` | Not needed |
| `@grammyjs/files` | Not needed |

### Webhook Pattern (v1.42)
```typescript
import { Bot } from 'grammy';
import { webhookCallback } from 'grammy/webhook';

const bot = new Bot(token);

// Register handlers
bot.on('message', handler);
bot.on('callback_query', handler);

// In your Express/Fastify handler:
app.post(`/telegram/${token}`, webhookCallback(bot, 'express'));
```

Or for raw handleUpdate (when you control the server):
```typescript
app.post('/telegram/webhook', async (req, res) => {
  await bot.handleUpdate(req.body);
  res.status(200).send();
});
```

---

## QQ Bot: Version Compatibility & Critical Bug Fix

### Version Independence
`@openclaw/qqbot` releases independently from the main `openclaw` package. The main `openclaw` version (checked via `npm view openclaw version`) does NOT reflect `@openclaw/qqbot` version. Always check both separately:

```bash
npm view @openclaw/qqbot version          # latest qqbot version
cat ~/.openclaw/node_modules/@openclaw/qqbot/package.json | python3 -c "import json,sys; print(json.load(sys.stdin).get('version'))"
```

The local `~/.openclaw/node_modules/@openclaw/qqbot/` is a SEPARATE installation from `~/.npm-global/lib/node_modules/openclaw/`. Global upgrade (`npm install -g openclaw`) does NOT update the local qqbot.

### Critical Bug: `core.channel.inbound.run` Fails (All Versions)
### Critical Bug: `pluginRuntime.channel.reply` is undefined (All Versions)

> ⚠️ This is a **framework-level bug** — NOT a qqbot plugin version issue. Affects ALL openclaw versions tested (2026.5.27, 2026.6.1, 2026.6.5-beta.2). **Reinstall does NOT fix it.**

**Symptom**: Every incoming QQ message triggers:
```
Message processing failed: Cannot read properties of undefined (reading 'run')
```

**Root cause**: `pluginRuntime.channel.reply` is `undefined` at dispatch time. `setQQBotRuntime()` IS called (setting `pluginRuntime.channel` to a valid object), but that object has no `.reply` property. When qqbot's `gateway.js` calls `pluginRuntime.channel.reply.dispatchReplyWithBufferedBlockDispatcher(...)`, it crashes.

**Diagnosis file**: `~/.npm-global/lib/node_modules/@tencent-connect/openclaw-qqbot/dist/src/gateway.js`

**Fix**: Add a defensive guard before the failing call (~line 1291):
```javascript
// 防御性检查：确保 channel.reply 存在
if (!pluginRuntime?.channel?.reply?.dispatchReplyWithBufferedBlockDispatcher) {
    const avail = pluginRuntime?.channel ? Object.keys(pluginRuntime.channel) : ['undefined'];
    log?.error(`[qqbot:${account.accountId}] FATAL: pluginRuntime.channel.reply is undefined. Available channel keys: ${JSON.stringify(avail)}`);
    throw new Error(`pluginRuntime.channel.reply is undefined — channel keys: ${JSON.stringify(avail)}`);
}
const dispatchPromise = pluginRuntime.channel.reply.dispatchReplyWithBufferedBlockDispatcher({...});
```

This throws a **clear error** and surfaces the real `channel` keys — enabling proper upstream investigation.

**Also add stack trace to catch block** (same file, ~line 1628):
```javascript
console.error('[qqbot:FATAL]', errStr, err?.stack ? '\n' + err.stack.split('\n').slice(0,10).join('\n') : '');
```

**Restart procedure** (critical — must kill ALL old processes or patches won't take effect):
```bash
pkill -9 -f 'openclaw ' 2>/dev/null; sleep 2
bash /home/saber/.hermes/openclaw-watchdog.sh &
sleep 25 && curl -s http://127.0.0.1:18888/health
# verify only 2 new PIDs exist (no old orphans)
ps aux | grep openclaw | grep -v grep | awk '{print $2}'
```

**How to find the exact failing call**: `grep -n 'dispatchReplyWithBufferedBlockDispatcher' ~/.npm-global/lib/node_modules/@tencent-connect/openclaw-qqbot/dist/src/gateway.js` — the call is at line ~1291. Patch there. `grep -n 'Message processing failed' ...gateway.js` — error logging is at ~line 1628.

**Why `pkill -f 'openclaw '` (with trailing space)** is important: prevents killing the wrong process. Use exact process name. Verify with `ps aux | grep openclaw | grep -v grep` — there should be exactly 2 PIDs (watchdog + child) after clean restart.

**Recommended fix**: **Disable the openclaw qqbot channel entirely.** Hermes has a stable built-in Python QQBot adapter — use that instead. In `~/.openclaw/openclaw.json`:
```json
"channels": { "qqbot": {} }
```
Then restart: `pkill -f openclaw; sleep 2; bash ~/.hermes/openclaw-watchdog.sh &`
**Do NOT wait for a version fix** — the bug is in openclaw framework code, not in the qqbot plugin, and there is no ETA for a fix.

### Hardcoded Warmup Timeout
The `startup model warmup timed out after 5000ms` message comes from a HARDCODED 5000ms timeout in the gateway startup code — **not from `timeoutMs` in openclaw.json**. Configurable `timeoutMs` controls per-message timeout, not startup warmup. This timeout is non-fatal (system continues), but it means the agent wasn't ready for the first message.

### `authHeader: true` Caveat
In `models.providers.{name}`, `authHeader: true` forces OpenClaw to inject `Authorization: Bearer *** into model requests. Most providers accept this. Remove `authHeader: true` if the provider uses a different auth header format (e.g., `X-Api-Key`).

## Key Discovery Method

When stuck on version incompatibilities or missing APIs:
1. Read actual `.js` source files in `node_modules/{package}/dist/` — this reveals the real API surface
2. Check `package.json` `"exports"` field for subpath resolution
3. For @buape/carbon: read `Client.js` constructor and `GatewayPlugin.js` connect method
4. For grammy: read `mod.d.ts` for exported types, `webhook.ts` for webhookCallback

---

## Critical: "gateway already running" After npm Update

**Symptom**: After `npm update -g openclaw`, the watchdog script starts but openclaw immediately dies with:
```
Gateway failed to start: gateway already running under systemd; existing gateway is healthy, exiting with code 78
Port 18888 is already in use.
- pid XXXX saber: openclaw (*:18888)
```

**Root cause**: The npm update killed and replaced the `openclaw` binary, but the **old running process (PID from before the update)** still holds port 18888. The watchdog script restarted the new binary, but the new binary can't bind the port.

**Complete fix sequence**:
```bash
# 1. Stop ALL watchdogs FIRST (prevents resurrection)
pkill -f 'openclaw-watchdog' 2>/dev/null

# 2. Kill all openclaw processes
pkill -9 -f 'openclaw ' 2>/dev/null
pkill -9 -f 'TencentConnect' 2>/dev/null
sleep 1

# 3. Verify port is free
lsof -i :18888 2>/dev/null | grep -v '^COMMAND' || echo "端口已释放"

# 4. Verify no orphan PIDs
pgrep -fa "openclaw\|TencentConnect" 2>/dev/null | grep -v grep || echo "无残留进程"

# 5. Start fresh
/bin/bash /home/saber/.hermes/openclaw-watchdog.sh &
sleep 5 && curl -s http://127.0.0.1:18888/health
```

**Why stop watchdogs first**: `pkill -f 'openclaw '` kills the child process, then the watchdog immediately restarts it — the old PID stays alive. Stop the watchdog first, then kill the children.

**Watch for the orphan PID**: After `pkill -f openclaw`, an old PID may still be alive. Find it with `lsof -i :18888` and `kill -9 <PID>` explicitly.

### Version Update Workflow (npm global packages)

When updating `openclaw`, `@martian-engineering/lossless-claw`, or `pnpm`:
1. Check outdated first: `npm outdated -g --depth=0`
2. Stop ALL processes (watchdogs FIRST, then children — see "Critical: gateway already running" above)
3. Run: `npm update -g openclaw @martian-engineering/lossless-claw pnpm`
4. Verify versions: `npm list -g openclaw @martian-engineering/lossless-claw pnpm`
5. Restart via watchdog (NOT `systemctl start`, use the watchdog script directly)

**npm update vs npm install -g**: `npm update -g` updates to latest matching semver range; `npm install -g` installs exact version. Use `update -g` for routine updates.

**EBADENGINE warning**: Node v25.9.0 triggers `EBADENGINE Unsupported engine` for `hosted-git-info@10.1.1` — safe to ignore, does not affect openclaw.

## Pitfalls

- **@buape/carbon 0.16.0**: Removed `gateway` subpath — always use 0.15.0
- **Carbon Client internal server**: You can't access its router. Must use your own HTTP server and call `client.handleInteraction()` manually.
- **grammy v1.21 plugins**: Don't install `@grammyjs/conversations` or `@grammyjs/files` with v1.42
- **Discord intents**: Must match what the bot needs. `GatewayIntents` from `@buape/carbon/gateway`
- **tsconfig exclude**: If you exclude adapter files from compilation, TypeScript won't catch real errors. Keep them in the build.

---

## Project Context

- Aether Gateway: `/home/saber/workspace/aether/gateway/`
- OpenClaw reference: `/home/saber/.openclaw/node_modules/openclaw/dist/extensions/discord/`
- Gateway port: 18799
- npm registry: `https://registry.npmmirror.com`
