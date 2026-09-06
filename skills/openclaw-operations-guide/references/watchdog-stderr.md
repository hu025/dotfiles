# Watchdog stderr Redirect

## Problem

The watchdog script `openclaw-watchdog.sh` captures openclaw's stdout/stderr output, writing to `/home/saber/.hermes/openclaw-watchdog.log`.

However, if the watchdog itself runs in background mode (`background=true`), its output is not automatically captured to the log.

## Diagnostic Method

Watchdog log file: `/home/saber/.hermes/openclaw-watchdog.log`

```bash
# Real-time monitoring of watchdog log (includes all console.error output)
tail -f /home/saber/.hermes/openclaw-watchdog.log

# View latest entries
tail -20 /home/saber/.hermes/openclaw-watchdog.log

# Filter key information
grep -i 'FATAL\|MSG\|error\|processing' /home/saber/.hermes/openclaw-watchdog.log | tail -20
```

## Key Log Timeline Example

```
2026-06-09T17:24:58.455+08:00 [qqbot] [qqbot:default] Starting gateway — appId=1903866159
2026-06-09T17:24:59.470+08:00 [qqbot] [default] ✅ Access token obtained successfully
2026-06-09T17:25:00.285+08:00 [qqbot] [default] WebSocket connected
2026-06-09T17:25:00.418+08:00 [qqbot] [qqbot:default] Gateway resumed
```

## Common Exit Codes

- `code=78`: port already occupied (another instance running), auto-restart triggered
- `code=0`: normal exit (WebSocket disconnect etc.)
- Non-zero other codes: abnormal exit, check specific error