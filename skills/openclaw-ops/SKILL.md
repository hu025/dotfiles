---
name: openclaw-ops
description: OpenClaw lifecycle management — install, upgrade, watchdog, health, common failures. OpenClaw is the QQ bot gateway that runs as a Node.js process behind a bash watchdog.
triggers:
  - openclaw
  - qqbot
  - openclaw upgrade
  - openclaw status
  - openclaw掉线
  - restart openclaw
---

## 版本检查

```bash
openclaw --version
# 输出: OpenClaw 2026.7.1-2 (0790d9f)
```

**不要**用 `node dist/index.js --version`（路径和 node 环境不一定对）。

---

## 健康检查

```bash
curl -s http://127.0.0.1:18888/health
# 正常: {"ok":true,"status":"live"}
```

- 端口 `18888` 必须处于 LISTEN 状态
- Node 进程 CPU 高（100%+) 是正常的启动阶段，不是卡死

---

## 进程管理

### 查看状态

```bash
ps aux | grep -E 'openclaw|node' | grep -v grep
ss -tlnp | grep 18888
```

### 完整停止（升级前必须）

必须先杀 watchdog 再杀 node，否则 watchdog 会立即拉新进程：

```bash
# 1. 杀掉所有 openclaw 相关进程
pkill -f openclaw-watchdog 2>/dev/null
pkill -f "node dist/index.js gateway" 2>/dev/null

# 2. 等待并确认（socket 释放需要 2-3 秒）
sleep 3
ps aux | grep -E 'node.*gateway|openclaw' | grep -v grep || echo "已停止"
```

如果进程还在，用 `kill -9 <PID>` 强杀。

---

## 升级流程（标准步骤）

> 参考: `references/openclaw-upgrade-workflow.md`

### 阶段0：验证上游真实最新版本

> ⚠️ **不要**只看本地缓存、PyPI 页面或 npm view 的 "latest" 标签——它们常因版本兼容性或 tag 延迟而落后于真实上游。必须实际查上游 API 确认。

```bash
# OpenClaw: 用 npm view 查 dist-tags（比 latest tag 更可靠）
npm view openclaw version
npm view openclaw dist-tags

# hermes-agent（GitHub releases）:
curl -s https://api.github.com/repos/NousResearch/hermes-agent/releases/latest | python3 -c "
import sys, json; data = json.load(sys.stdin); print('Latest:', data['tag_name'], 'Published:', data['published_at'])
"

# 对比本地版本后再决定是否升级
openclaw --version
```

### 阶段1：停止
pkill -f openclaw-watchdog 2>/dev/null
sleep 1
pkill -f "node dist/index.js gateway" 2>/dev/null || kill -9 <PID>
sleep 2

# === 阶段2：升级 ===
npm install -g openclaw@latest

# === 阶段3：确认版本 ===
openclaw --version

# === 阶段4：启动（用 watchdog）===
terminal(background=true, command="bash /home/saber/.hermes/openclaw-watchdog.sh")
# 注意：用 background=true 而非 nohup/&，否则 Hermes 会跟踪不了进程

# === 阶段5：等待就绪 ===
# ⚠️ 端口绑定需要 20-25 秒，不要提前 curl（会得到 exit code 7）
sleep 25
curl -s http://127.0.0.1:18888/health
# 正常: {"ok":true,"status":"live"}
```

---

## Watchdog 管理

看门狗脚本位于 `/home/saber/.hermes/openclaw-watchdog.sh`。

关键设计点：
- 用 `while true` 循环，任何退出码都重启
- 5 秒重启间隔
- 工作目录切换到 `~/.npm-global/lib/node_modules/openclaw`
- 日志重定向到 `/home/saber/.hermes/openclaw-watchdog.log`

日志文件：
- Watchdog 主日志：`/home/saber/.hermes/openclaw-watchdog.log`
- OpenClaw 运行日志：`/tmp/openclaw/openclaw-YYYY-MM-DD.log`

---

## xiaoclaw 项目澄清

> ⚠️ **2026-07-28 发现的关键混淆**：`xiaoclaw` 和 `xiaozhi-esp32` 是两个完全不同的项目，不要混淆。

### 什么是 xiaoclaw？

`xiaoclaw` = OpenClaw QQ Bot 的项目名（GitHub: `github.com/xiaoclaw/xiaoclaw`）

- **本质**：Node.js 桌面应用（内置 Windows Node.js 二进制 + OpenClaw 模块）
- **用途**：在电脑上运行的 QQ Bot 客户端（和 Linux 服务器上的 OpenClaw 是同一样东西）
- **硬件**：**没有任何 ESP32/嵌入式固件** — 就是一个桌面 App，不需要烧录到硬件
- GitHub releases 的 zip 包（225MB）= 打包了 Windows Node.js + OpenClaw

### 什么时候说"xiaoclaw + ESP32"是错的？

用户问"把 xiaoclaw 刷到 ESP32-S3"是**概念混淆**。如果用户的 ESP32-S3 需要刷固件，他想要的很可能是：

- **`xiaozhi-esp32`**（小智）：ESP32 语音 AI 固件，GitHub `78/xiaozhi-esp32`，有 100+ 款开发板的预编译固件
- 其他 ESP32 固件项目（如 voice assistant、esp-adf 示例等）

### 如何识别用户想要的是什么？

| 用户描述 | 实际项目 | 处理方式 |
|----------|----------|----------|
| xiaoclaw + ESP32 | **xiaozhi-esp32** | 下载预编译固件并烧录 |
| xiaoclaw（桌面/服务器） | **OpenClaw** | 用 `openclaw-ops` / `openclaw-operations-guide` |
| xiaozhi-esp32 + ESP32 | **xiaozhi-esp32** | 直接烧录预编译固件 |
| ESP32 + 语音 AI | **xiaozhi-esp32** | 同上 |

### 如果用户要 ESP32 固件（xiaozhi-esp32）

参考 `esp32-firmware-workflow` 技能，完整流程：
1. 检测设备型号和端口
2. 从 GitHub releases 下载对应 board 的固件
3. 用 esptool 擦除并烧录
4. 验证启动日志

---

## 常见失败模式

### 1. 进程启动后立即退出（exit=0）
- 原因：QQ WebSocket 连接正常后主动关闭，不是崩溃
- 解决：看门狗会在 5 秒后自动重启，这是正常行为
- 验证：检查日志中有无 `[qqbot:default] Gateway ready`

### 2. 健康检查 curl 返回 exit code 7（无法连接）
- 原因：进程还在启动，或端口未监听
- 解决：`sleep 25` 再试（不要用 20 秒，端口绑定需要 20-25 秒），或 `ss -tlnp | grep 18888` 确认监听状态

### 3. 端口被占（exit code 78）
- 日志：`Another process is listening on this port`
- 根因：前一个 node 进程还没完全释放 socket（TIME_WAIT）
- 解决：杀光所有进程后 `sleep 3` 再重新拉起

### 4. 双重实例 & crash-loop breaker

**双重实例检测**：
```bash
ps aux | grep -E "node.*gateway|openclaw-watchdog" | grep -v grep
# 正常：1个node进程 + 1个watchdog bash
# 异常：2个node 或 2个watchdog
```

**清理流程**（不论是双重实例还是触发 breaker，都要走这步）：
```bash
pkill -f openclaw-watchdog 2>/dev/null
pkill -f "node dist/index.js gateway" 2>/dev/null
sleep 3
# 确认已停止
ps aux | grep -E "node.*gateway|openclaw" | grep -v grep || echo "已全部停止"
```

### 5. Crash-Loop Breaker 拦截频道启动

**症状**：日志出现 `crash-loop breaker tripped: N unclean boot(s) within 300000ms; suppressing channel/provider account auto-start`，QQBot 和飞书频道均不启动。

**触发条件**：5分钟内（300000ms）有 ≥3 次 `startup_failed` 启动。

**根因**：配置错误、端口冲突、npm包损坏等导致的反复重启。正常 kill 信号（exit 0）不触发 breaker。

**SQLite 恢复步骤**（推荐）：
```bash
python3 -c "
import sqlite3
db = '/home/saber/.openclaw/state/openclaw.sqlite'
conn = sqlite3.connect(db)
# 将所有 startup_failed 改为 clean_stop（completed_at_ms = started_at_ms + 100）
n = conn.execute('''
    UPDATE gateway_boot_lifecycle
    SET outcome = \"clean_stop\", completed_at_ms = started_at_ms + 100
    WHERE outcome = \"startup_failed\"
''').rowcount
conn.commit()
print(f'Reset {n} failed boot record(s)')
conn.close()
"
# 然后重启
bash /home/saber/.hermes/openclaw-watchdog.sh
```

重启后 breaker 自动检测到窗口内无 unclean boots，输出 `restart-loop breaker recovered; channel auto-start restored`，两个频道自动上线。

**日志确认**：
```bash
strings /home/saber/.hermes/openclaw-watchdog.log | grep -E "qqbot.*ready|feishu.*ready|breaker recovered"
```

> 详细流程见 `references/openclaw-crashloop-recovery.md`

### 6. 模型调用返回 401 / content 为 null

> ⚠️ **关键发现**：OpenClaw 的 API Key **优先从 SQLite 读取**，不读 `openclaw.json`。修改 key 时必须同步更新数据库，否则不会生效。

**三层存储（优先级从高到低）**：
1. **SQLite `auth_profile_store`**（优先级最高，OpenClaw 实际读取这里）
   - 路径：`~/.openclaw/agents/main/agent/openclaw-agent.sqlite`
   - 表：`auth_profile_store` → 列 `store_json` → JSON 内 `profiles.{profile_name}.key`
2. **SQLite `auth_profile_state`**（存放 cooldown 状态）
3. **`openclaw.json`**（最低优先级，只在 SQLite 无记录时兜底）

**一次性同步 key + 清除 cooldown 脚本**：
```python
import json, sqlite3

KEY = "wisemodel-oijjdgzxpoasvgnpnrqm"  # 替换为实际 key

for db_path in [
    '/home/saber/.openclaw/agents/main/agent/openclaw-agent.sqlite',
]:
    conn = sqlite3.connect(db_path)

    # --- 同步 key 到 auth_profile_store ---
    for tbl in ['auth_profile_store']:
        cols = [r[1] for r in conn.execute(f'PRAGMA table_info({tbl})').fetchall()]
        if 'store_json' in cols:
            key_col = [c for c in cols if '_key' in c][0]
            for row in conn.execute(f'SELECT * FROM {tbl}').fetchall():
                d = dict(zip(cols, row))
                store = json.loads(d['store_json'])
                for profile, cfg in store.get('profiles', {}).items():
                    if cfg.get('key', '').startswith('sk-cp-') or cfg.get('key', '') != KEY:
                        print(f'{tbl}: updating {profile}: {cfg.get("key","?")[:15]}... → {KEY[:15]}...')
                        cfg['key'] = KEY
                conn.execute(f"UPDATE {tbl} SET store_json = ? WHERE {key_col} = ?",
                             (json.dumps(store), d[key_col]))
            conn.commit()

    # --- 清除 cooldown 在 auth_profile_state ---
    for tbl in ['auth_profile_state']:
        cols = [r[1] for r in conn.execute(f'PRAGMA table_info({tbl})').fetchall()]
        if 'state_json' in cols:
            key_col = [c for c in cols if '_key' in c][0]
            for row in conn.execute(f'SELECT * FROM {tbl}').fetchall():
                d = dict(zip(cols, row))
                state = json.loads(d['state_json'])
                for profile, stats in state.get('usageStats', {}).items():
                    if stats.get('cooldownReason') in ('auth', 'cooldown'):
                        print(f'{tbl}: clearing cooldown for {profile}')
                        stats['cooldownUntil'] = 0
                        stats['cooldownReason'] = None
                        stats['errorCount'] = 0
                        stats['failureCounts'] = {}
                conn.execute(f"UPDATE {tbl} SET state_json = ? WHERE {key_col} = ?",
                             (json.dumps(state), d[key_col]))
            conn.commit()
    conn.close()
    print(f'{db_path}: done')
```

**调试：提取当前实际使用的 key**：
```python
import sqlite3, json
conn = sqlite3.connect('/home/saber/.openclaw/agents/main/agent/openclaw-agent.sqlite')
row = conn.execute("SELECT store_json FROM auth_profile_store WHERE store_key = 'primary'").fetchone()
conn.close()
store = json.loads(row[0])
for name, cfg in store.get('profiles', {}).items():
    print(f'{name}: {cfg.get("key", "")[:20]}... ({len(cfg.get("key",""))} chars)')
```

#### 根因 A：API Key 不匹配

**症状**：`Authentication failed (provider returned HTTP 401)` + `content: null`

SQLite 中存储的 key 与实际 provider 的 key 不一致。常见场景：之前用 `sk-cp-` 格式的 MiniMax CN key 注册，后来切换到 wisemodel 代理，只更新了 `openclaw.json` 没更新 SQLite。

#### 根因 B：Provider Cooldown（认证失败后被自动拦截）

**症状**：一次 401 后，后续所有请求均失败，直到 cooldown 过期或手动清除。

OpenClaw 在 401 后自动给该 provider profile 设置 cooldown（冷却期），后续请求直接被拦截。

#### 根因 C：wisemodel reasoning_content 吃满 max_tokens

**症状**：`content: null` 但 `reasoning_content` 有内容，`finish_reason: length`

wisemodel（`open.ospreyai.cn`）在短 `max_tokens` 场景下，reasoning 过程先吃满整个 budget，导致 `content` 为空。`max_tokens=30` 时极易复现，`max_tokens=200` 时正常。

---

### 7. Hermes/OpenClaw QQ 双通道冲突
- 两者可能用同一 QQ 账号，消息被重复处理
- 建议：禁用 OpenClaw 的 `channels.qqbot.enabled`（保留 Hermes 内置 QQBot）
- 操作：`~/.openclaw/openclaw.json` → `"qqbot": {"enabled": false, ...}`

### 8. Hermes Gateway 崩溃导致 openclaw 插件异常
- 症状：`core.channel.inbound undefined` 错误
- 根因：openclaw 框架层问题，不是 qqbot 插件问题
- 参考：`references/openclaw-dispatch-bug.md`
- 上报：需要 upstream 修复

### 9. npm install 报权限错误
- 解决：`sudo npm install -g openclaw@latest` 或确保 `.npm-global` 属主正确

---

## 日志位置汇总

| 日志 | 路径 |
|------|------|
| Watchdog 主日志 | `/home/saber/.hermes/openclaw-watchdog.log` |
| OpenClaw 运行日志 | `/tmp/openclaw/openclaw-YYYY-MM-DD.log` |
| Hermes Gateway | systemd journal |

日志是 JSONL 格式，可用 `strings` 或 `cat | python -m json.tool` 读取。

---

## 相关技能

- `openclaw-qqbot-debugging` — 消息处理错误诊断
- `openclaw-adapter-migration` — 平台适配器迁移
- `xiaozhi-server` — xiaozhi-esp32-server 后端部署（WebSocket/LLM/TTS/OpenClaw集成）

## 参考文档

> 升级流程见 `references/openclaw-upgrade-workflow.md`
> Crash-Loop Breaker 恢复见 `references/openclaw-crashloop-recovery.md`
> SQLite 数据库 schema（API Key/Cooldown）见 `references/openclaw-sqlite-schema.md`
