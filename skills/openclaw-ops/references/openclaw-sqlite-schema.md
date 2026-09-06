# OpenClaw SQLite 数据库结构参考

## 数据库路径

| 数据库 | 路径 | 主要用途 |
|--------|------|----------|
| Agent 认证状态 | `~/.openclaw/agents/main/agent/openclaw-agent.sqlite` | API Key 存储、Provider Cooldown |
| Gateway 状态 | `~/.openclaw/state/openclaw.sqlite` | Boot Lifecycle、Auth Profile Stores、Device Token |
| Task Runs | `~/.openclaw/.openclaw/tasks/runs.sqlite` | 任务执行记录 |

---

## agents/main/agent/openclaw-agent.sqlite

### auth_profile_store（API Key 实际存储位置）

```sql
CREATE TABLE auth_profile_store (
  store_key  TEXT PRIMARY KEY,   -- 通常是 'primary'
  store_json TEXT,               -- JSON，见下方结构
  updated_at INTEGER             -- 毫秒时间戳
);
```

store_json 结构：
```json
{
  "version": 1,
  "profiles": {
    "minimax:cn": {
      "type": "api_key",
      "provider": "minimax",
      "key": "sk-cp-..."    // ← 实际 API Key，125 chars
    }
  }
}
```

> **注意**：OpenClaw 优先读 SQLite 里的 key，JSON 配置文件里的 `apiKey` 字段只是兜底。

### auth_profile_state（Cooldown/失败统计）

```sql
CREATE TABLE auth_profile_state (
  state_key  TEXT PRIMARY KEY,  -- 通常是 'primary'
  state_json TEXT               -- JSON，见下方结构
);
```

state_json 结构：
```json
{
  "version": 1,
  "lastGood": {
    "minimax": "minimax:cn"    // 上次成功的 profile
  },
  "usageStats": {
    "minimax:cn": {
      "lastUsed": 1782179631811,
      "cooldownUntil": 1785172410129,   // 0 = 无 cooldown
      "cooldownReason": "auth",          // auth | rate | error | null
      "errorCount": 1,
      "failureCounts": { "auth": 1 },
      "lastFailureAt": 1785172380129
    }
  }
}
```

**cooldownReason 含义**：
- `auth`：401 认证失败
- `rate`：429 限流
- `error`：其他错误

---

## state/openclaw.sqlite

### gateway_boot_lifecycle（启动历史）

```sql
CREATE TABLE gateway_boot_lifecycle (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  started_at_ms   INTEGER,
  completed_at_ms INTEGER,
  outcome         TEXT,          -- "clean_stop" | "startup_failed" | "unclean_stop"
  plugin_count    INTEGER,
  error_message   TEXT
);
```

用途：crash-loop breaker 计算 5 分钟窗口内的 unclean boots 次数。

### auth_profile_stores（Gateway 级认证存储）

同 agent 库结构，但存储的是 Gateway 层的认证配置。

### auth_profile_state（同 agent 库）

Gateway 层的 cooldown 状态。

---

## 常用调试 SQL

```sql
-- 查看所有 profile 的 cooldown 状态
SELECT 
  store_key,
  json_extract(store_json, '$.usageStats."minimax:cn".cooldownReason') as reason,
  json_extract(store_json, '$.usageStats."minimax:cn".cooldownUntil') as until,
  json_extract(store_json, '$.usageStats."minimax:cn".errorCount') as errors
FROM auth_profile_state;

-- 清除某个 profile 的 cooldown
UPDATE auth_profile_state 
SET store_json = json_replace(
    store_json,
    '$.usageStats."minimax:cn".cooldownUntil', 0,
    '$.usageStats."minimax:cn".cooldownReason', null,
    '$.usageStats."minimax:cn".errorCount', 0
)
WHERE store_key = 'primary';

-- 重置 gateway_boot_lifecycle 中的所有失败记录
UPDATE gateway_boot_lifecycle
SET outcome = 'clean_stop', completed_at_ms = started_at_ms + 100
WHERE outcome = 'startup_failed';
```

---

## 注意事项

1. **两个库都有 auth_profile_state**：修改时需同时清理两个库，否则重启后可能被另一个库的状态覆盖
2. **store_json 是 JSON 字符串**：用 `json_extract()` 查询
3. **updated_at/state_key**：都是毫秒时间戳，用于排序和定位
