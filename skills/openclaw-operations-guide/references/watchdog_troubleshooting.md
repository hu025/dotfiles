# OpenClaw Watchdog & Troubleshooting

## Watchdog Script Location
`/home/saber/.hermes/openclaw-watchdog.sh`

**Start command (run in background):**
```bash
bash /home/saber/.hermes/openclaw-watchdog.sh >> /home/saber/.hermes/openclaw-watchdog.log 2>&1
```

**Log locations:**
- `/home/saber/.hermes/openclaw-watchdog.log` — watchdog-level (start/stop/restart events)
- `/tmp/openclaw/openclaw-YYYY-MM-DD.log` — openclaw framework JSON logs

**Health check:**
```bash
curl -s http://127.0.0.1:18888/health
# Expected: {"ok":true,"status":"live"}
```

## SIGTERM Pattern (known)
OpenClaw logs `signal SIGTERM received` → `received SIGTERM; shutting down` → clean exit.
This is **not a crash** — something sent SIGTERM. Common causes:
- `systemctl --user stop` invoked
- Parent process (watchdog's `wait` loop) exited naturally, then cleanup SIGTERM'd the child
- Manual `kill` by user or cron

If watchdog should restart but doesn't: check if the `wait $OPENCLAW_PID` loop is still running.
```bash
ps aux | grep watchdog | grep -v grep
```

## Systemd Service (not currently used)
Service name: `openclaw-watchdog.service` — NOT installed/active.
Direct bash invocation is the working approach.

## Watchdog Log Interpretation
```
[2026-06-28 04:44:47] Watchdog stopping      ← cleanup() trap fired
[gateway] signal SIGTERM received             ← openclaw received SIGTERM
[gateway] received SIGTERM; shutting down      ← openclaw graceful shutdown
[gateway] started: gateway stopping             ← shutdown complete

[2026-06-28 05:04:08] OpenClaw Watchdog starting  ← restart
[2026-06-28 05:04:08] OpenClaw started, PID=9959
[gateway] http server listening (5 plugins...)  ← online ~17s later
```

Normal startup time: ~15-20 seconds. If health check fails beyond 30s, check logs.

## Process Cleanup (if residue)
If old processes won't die:
```bash
kill $(pgrep -f openclaw)
kill $(pgrep -f openclaw-watchdog)
sleep 2
bash /home/saber/.hermes/openclaw-watchdog.sh >> /home/saber/.hermes/openclaw-watchdog.log 2>&1 &
```
