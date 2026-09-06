# OpenClaw Crash-Loop Breaker 恢复流程

## 什么是 crash-loop breaker

OpenClaw gateway 内置启动稳定性保护。检测逻辑在 `run-CSvF3r1e.js` 中：

- **窗口**：5 分钟（300000ms）
- **阈值**：≥3 次 `startup_failed` 启动
- **效果**：所有 channel（qqbot、feishu 等）的 auto-start 被抑制，日志输出 `suppressing channel/provider account auto-start`
- **不触发**：正常的 kill 信号（`gateway.stop`、`planned_restart`）不计入

Breaker 在内存中维护状态，但同时**写入 SQLite 持久化**，使重启后依然保持抑制状态直到条件解除。

## 数据库位置与结构

```bash
db_path = /home/saber/.openclaw/state/openclaw.sqlite
table = gateway_boot_lifecycle
```

列结构：

| 列 | 类型 | 说明 |
|---|---|---|
| `boot_id` | TEXT (UUID) | 启动记录唯一 ID |
| `pid` | INTEGER | 进程 PID |
| `started_at_ms` | INTEGER | 启动时间戳（毫秒） |
| `completed_at_ms` | INTEGER | 完成时间戳（毫秒），NULL=仍在运行 |
| `outcome` | TEXT | `clean_stop` / `startup_failed` / `planned_restart` |
| `startup_reason` | TEXT | 启动原因（`crash-loop-breaker` 等） |
| `reason` | TEXT | 附加信息（错误消息等） |

## 查询 breaker 当前状态

```python
import sqlite3, datetime
db = '/home/saber/.openclaw/state/openclaw.sqlite'
conn = sqlite3.connect(db)
rows = conn.execute('''
    SELECT boot_id, pid, started_at_ms, completed_at_ms, outcome
    FROM gateway_boot_lifecycle
    ORDER BY started_at_ms DESC
    LIMIT 10
''').fetchall()
for r in rows:
    started = datetime.datetime.fromtimestamp(r[2]/1000).strftime('%H:%M:%S')
    completed = datetime.datetime.fromtimestamp(r[3]/1000).strftime('%H:%M:%S') if r[3] else 'RUNNING'
    print(f'{r[0][:8]} PID={r[1]} started={started} completed={completed} outcome={r[4]}')
conn.close()
```

## 恢复步骤（推荐）

只需要把所有 `startup_failed` 记录改成 `clean_stop`：

```python
import sqlite3
db = '/home/saber/.openclaw/state/openclaw.sqlite'
conn = sqlite3.connect(db)
n = conn.execute('''
    UPDATE gateway_boot_lifecycle
    SET outcome = "clean_stop", completed_at_ms = started_at_ms + 100
    WHERE outcome = "startup_failed"
''').rowcount
conn.commit()
print(f'Reset {n} failed boot record(s)')
conn.close()
```

然后重启 gateway，breaker 会自动恢复：

```
[gateway] restart-loop breaker recovered; channel auto-start restored
[qqbot] [qqbot:default] Gateway ready
[feishu] feishu[default]: WebSocket client started
```

## 什么时候会触发 breaker

1. 配置 JSON 无效（`Invalid config at .../openclaw.json: <root>: Invalid input`）
2. 端口被占用（`EADDRINUSE`）
3. npm 包损坏或缺失
4. 多次手动杀进程后立即重启（重启过于频繁时）

**正常停止不会触发**：`gateway.stop`、`planned_restart`、`kill` 信号都被计为 `clean_stop`。

## 不需要清除 stability 文件的情况

`/home/saber/.openclaw/logs/stability/` 下的 JSON 文件只是诊断包，不需要删除。 breaker 的状态完全由 SQLite `gateway_boot_lifecycle` 表驱动。

## 注意事项

- 每次重启 gateway 都会在该表中写入一条新记录
- `openclaw doctor --fix` 会尝试修复配置，但不修改数据库
- 如果窗口内（5分钟）没有任何 unclean boots，breaker 自动恢复
