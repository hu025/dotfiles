# OpenClaw Diagnostic Patterns

## console.error Doesn't Go to Log Files

**Problem**: Adding `console.error` in gateway.js outputs to stderr, not to `/tmp/openclaw/openclaw-*.log`.

**Cause**: The `/tmp/openclaw/` log files only record openclaw framework `log?.info`/`log?.error` (via framework logging system). `console.error` goes directly to process stderr.

**Diagnostic methods**:

1. **Temp file write** (most reliable):
   ```javascript
   // At ws.on("message") start
   try { require('fs').writeFileSync('/tmp/qqbot-raw-msg.log', data.toString().slice(0,500)); } catch(e) {}
   ```
   Then `tail /tmp/qqbot-raw-msg.log`

2. **Monitor watchdog log**:
   ```bash
   tail -f /home/saber/.hermes/openclaw-watchdog.log
   ```
   watchdog script captures stdout and stderr

3. **strace trace** (extreme):
   ```bash
   strace -p <pid> -e write -s 200 2>&1 | grep -i 'qqbot\|raw\|FATAL'
   ```

## Multi-Process Cleanup

When multiple stale openclaw processes accumulate, you cannot just `pkill openclaw`. Correct order:

1. First kill all watchdog bash processes (prevents them from spawning more stale processes)
2. Then kill all openclaw node processes
3. Confirm clean before restarting

**Wrong approach**:
```bash
pkill -f "openclaw.mjs"  # kills only one, stale ones remain
bash openclaw-watchdog.sh  # watchdog spawns old processes again
```

**Correct approach**:
```bash
kill -9 $(pgrep -a bash | grep openclaw-watchdog | awk '{print $1}')
kill -9 $(pgrep -a node | grep 'openclaw$' | awk '{print $1}')
ps aux | grep -E 'openclaw|node' | grep -v grep  # confirm clean
bash /home/saber/.hermes/openclaw-watchdog.sh
```

## Quick Message Handling Troubleshooting

When QQ Bot doesn't receive messages or receives without reply:

1. **Confirm WebSocket connection**: check watchdog log for `[qqbot] WebSocket connected`
2. **Confirm message arrives**: add raw message write to `/tmp/qqbot-raw-msg.log`
3. **Confirm handleMessage called**: add `console.error` to gateway.js line ~645
4. **Confirm core.channel.reply**: check diagnostic log for `channel.reply=${typeof pluginRuntime?.channel?.reply}`
5. **Check log files**: watchdog log + `/tmp/openclaw/` log