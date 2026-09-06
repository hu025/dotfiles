# Gateway & Memory Troubleshooting Reference

## Semantic Memory Layer DB Schema Mismatch

**Symptom**: `SemanticMemoryLayer` raises `sqlite3.OperationalError: no such column: trust_score`

**Root Cause**: `semantic.db` was created with an older schema lacking columns required by the current `holographic/store.py`. The FTS virtual table columns point to a `facts` source table that no longer matches the current `_SCHEMA`.

- Old schema: `facts(rowid, entity, content, category, tags, created_at)` — FTS indexed `entity, content, category, tags`
- Current schema: `facts(fact_id, content, category, tags, trust_score, ...)` — FTS indexes `content, tags`

**Fix**:
```bash
# 1. Backup old db (check if it has data first)
cp ~/.hermes/memory/semantic.db ~/.hermes/memory/semantic.db.backup_$(date +%Y%m%d)

# 2. Remove corrupted db — auto-recreates with correct schema on next init
rm ~/.hermes/memory/semantic.db

# 3. Verify new layer works
python3 -c "
import sys; sys.path.insert(0, '/home/saber/.hermes/hermes-agent')
from plugins.memory.multilayer.semantic import SemanticMemoryLayer
sm = SemanticMemoryLayer()
result = sm.search('x')  # query arg required
print('OK')
"
```

**Note**: Always check `facts` table row count before deleting. If it has data, migrate rather than delete.

---

## QQ Bot Session Error 4009 — NOT an Error

**Symptom** (in gateway.log):
```
WebSocket closed: code=4009 reason=Session timed out
Session error (4009), clearing session for re-identify
```
Occurs every ~30 minutes at a consistent interval.

**Cause**: **Expected QQ platform behavior.** QQ server proactively closes WebSocket connections after its session TTL. The gateway handles this correctly:
1. Detects WebSocket close code 4009
2. Clears session and re-identifies automatically
3. Restores with a new `session_id`

**Confirmation**: Log shows `Identify sent` → `Ready, session_id=<new>` after each occurrence.

**Action Required**: None. If messages stop after a 4009, wait 30s — session restores automatically.

---

## WeChat (Weixin) Rate Limiting

**Symptom**:
```
[Weixin] send failed to=b2bc9122: iLink sendmessage rate limited: ret=-2 errcode=None errmsg=rate limited
```

**Cause**: iLink/WeChat platform enforces per-account sending rate limits — platform-side, not configurable from gateway.

**Gateway behavior**: Automatic retry with backoff. Queue delivers when limit lifts.

**If persistent**: Reduce automated message volume through WeChat channel.

---

## Memory Layer 5-Layer Smoke Test

Each layer has a different method signature — wrong args cause misleading errors.

| Layer | Class | Method | Args |
|-------|-------|--------|------|
| Flash | `FlashMemoryLayer` | `get_all()` | none |
| Semantic | `SemanticMemoryLayer` | `search()` | query string |
| Procedural | `ProceduralMemoryLayer` | `get_procedures()` | none |
| Episodic | `EpisodicMemoryLayer` | `get_recent_episodes()` | int (count) |
| Working | `WorkingMemoryLayer` | `get_context()` | none |

```python
import sys; sys.path.insert(0, '/home/saber/.hermes/hermes-agent')
from plugins.memory.multilayer import (FlashMemoryLayer, SemanticMemoryLayer,
    ProceduralMemoryLayer, EpisodicMemoryLayer, WorkingMemoryLayer)
for name, cls, method, *args in [
    ('flash',     FlashMemoryLayer,      'get_all'),
    ('semantic',  SemanticMemoryLayer,   'search',     'x'),
    ('procedural',ProceduralMemoryLayer, 'get_procedures'),
    ('episodic',  EpisodicMemoryLayer,   'get_recent_episodes', 1),
    ('working',   WorkingMemoryLayer,    'get_context'),
]:
    getattr(cls(), method)(*args)
    print(f'  {name}: OK')
```

---

## Gateway Process Diagnostics

**Find gateway process**:
```bash
ps aux | grep hermes_cli.main | grep gateway
ss -tlnp | grep <PID>
```

**Hermes Gateway** is a Python systemd service — does NOT expose an HTTP health endpoint. **OpenClaw** (Node.js) exposes port 18888.

**Restart**: `systemctl --user restart hermes-gateway.service`
**Reset crash loop**: `systemctl --user reset-failed hermes-gateway.service`
