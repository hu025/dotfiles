# System Maintenance Workflow (Linux / Arch)

## Quick Health Check

```bash
# One-liner summary
echo "=== Gateway ===" && systemctl --user is-active hermes-gateway.service && \
echo "=== OpenClaw ===" && ps aux | grep -E "openclaw|wechat" | grep -v grep | head -3 && \
echo "=== Disk ===" && df -h / /home | tail -2 && \
echo "=== Memory ===" && free -h | tail -2 && \
echo "=== Uptime ===" && uptime
```

## Safe Cache Cleaning

### systemd journal (primary)
```bash
# Clean archived journals to max size (safe — never deletes active journal)
sudo journalctl --vacuum-size=50M    # main system journals
journalctl --user --vacuum-size=10M  # user journals
# Frees ~46M+ on typical install
```

### systemd journal (by time)
```bash
sudo journalctl --vacuum-time=7d    # keep last 7 days
journalctl --user --vacuum-time=7d
```

### pip cache
```bash
pip cache purge   # frees ~6-10M typically
```

### pacman cache (requires root, beware locks)
```bash
# Check for pacman lock (another pacman process running)
ls /var/lib/pacman/db.lck && echo "PACMAN LOCKED — skip"

# Safe: only remove old package versions, keep current
# paccache (part of pacman-contrib) — removes all but last 3 versions per package
sudo pacman -S pacman-contrib 2>/dev/null || true
paccache -r    # remove cached packages (keep last 3 versions)
```

### npm cache (if needed)
```bash
npm cache clean --force
```

## Disk Usage Investigation

```bash
# Find large directories
du -sh ~/.cache/* 2>/dev/null | sort -rh | head -10
du -sh /var/log/* 2>/dev/null | sort -rh | head -10
du -sh /tmp/* 2>/dev/null | sort -rh | head -5

# Find files > 100M
find ~ -type f -size +100M 2>/dev/null | head -10
```

## Old Kernel Cleanup (Arch-specific)

Arch Linux keeps old kernels in `/var/lib/pacman/local/`. Safe check:
```bash
# List installed kernels
ls /var/lib/pacman/local/ | grep '^linux-[0-9]'

# Current running kernel
uname -r

# Remove old kernel (NEVER remove the currently running one)
# Check it's not in use first:
pacman -Q linux

# If old kernel exists and not running:
OLD_KERN=$(ls /var/lib/pacman/local/ | grep '^linux-[0-9]' | grep -v "$(uname -r)")
[ -n "$OLD_KERN" ] && sudo pacman -Rcs "$OLD_KERN" --noconfirm
```

**Common pitfall**: `pacman -Rcs` fails with "cannot lock database" if another pacman process is running. Check `ps aux | grep pacman` before retrying.

## systemd Service Management

```bash
# Check status
systemctl --user status hermes-gateway.service

# Restart (after config/code changes)
systemctl --user restart hermes-gateway.service

# Reset failed state (clears crash loop flags)
systemctl --user reset-failed hermes-gateway.service

# View recent logs
journalctl --user -u hermes-gateway.service -n 30 --no-pager

# Reload systemd after unit file changes
systemctl --user daemon-reload
```

## SQLite Integrity Checks

After cleaning or as part of routine maintenance:
```bash
# Check state.db (sessions)
sqlite3 ~/.hermes/state.db "PRAGMA integrity_check;"
sqlite3 ~/.hermes/state.db "SELECT COUNT(*) FROM sessions;"

# Check memory_store.db
sqlite3 ~/.hermes/memory_store.db ".tables"
# If "no such table" — database is wrong type (not损坏, just a different schema)
```

## Known Saber-specific Paths

| What | Path |
|------|------|
| hermes-agent source | `~/.hermes/hermes-agent/` |
| hermes config | `~/.hermes/config.yaml` |
| hermes logs | `~/.hermes/logs/` |
| hermes sessions | `~/.hermes/sessions/` |
| pip cache | `~/.cache/pip/` |
| pacman log | `/var/log/pacman.log` |
| systemd journals | `/var/log/journal/` |
| user journals | `/var/log/journal/<machine-id>/user-1000/` |
| OpenClaw WeChat | `~/.npm-global/lib/node_modules/openclaw/` |
