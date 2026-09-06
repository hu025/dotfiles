---
name: system-status-check
description: PC + ESP32 状态一键检查 — 诊断 PC 所有后台服务和 ESP32 连接状态。触发词：检查电脑状态、PC状态、系统状态、ESP32好了吗、ESP32什么情况
triggers:
  - 检查电脑状态
  - PC 状态
  - ESP32 好了吗
  - ESP32 什么情况
  - 系统状态
---

# PC + ESP32 状态检查

## 一句话结论优先

用户只问"ESP32好了吗"或"ESP32什么情况" → 直接给结论 + 关键数据，不要铺垫。

## 快速检查（all-in-one 命令）

```bash
# 1. 服务端口
ss -tlnp | grep -E '8090|8080|8989|18888|8642'

# 2. ESP32 串口（fcntl 非阻塞）
python3 -c "
import serial, fcntl, os, time
s = serial.Serial('/dev/ttyACM0', 115200, timeout=5)
fd = s.fd
flags = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
time.sleep(3)
data = os.read(fd, 8192)
if data:
    lines = data.decode('utf-8', errors='replace').split('\n')
    for l in lines[-20:]:
        if l.strip(): print(l.strip()[-180:])
else:
    print('No serial data')
"

# 3. xiaozhi-server 今日设备日志
TODAY=$(date +%Y%m%d)
grep '28:84:85:88:f7:e0' /home/saber/xiaozhi-server/xiaozhi_server-linux-amd64-v0.6.4/xiaozhi_server-linux-amd64/logs/server.log."$TODAY" 2>/dev/null | tail -3

# 4. PC 网络
ip route get 8.8.8.8 2>&1 | head -1
```

## 服务端口速查表

| 端口 | 服务 | 命令 |
|------|------|------|
| 8090 | OTA 代理 | `ss -tlnp \| grep 8090` |
| 8080 | xiaozhi HTTP | `ss -tlnp \| grep 8080` |
| 8989 | xiaozhi WebSocket | `ss -tlnp \| grep 8989` |
| 18888 | OpenClaw QQ Bot | `ss -tlnp \| grep 18888` |
| 8642 | Hermes Gateway | `ss -tlnp \| grep 8642` |

## ESP32 串口判断

| 串口输出 | 含义 |
|---------|------|
| `SystemInfo: free sram: XX` + `Display: System time is not set`，uptime 递增 | ✅ 正常运行 idle |
| `SystemInfo` 循环 + 无 WiFi 日志 + 有 boot 日志序列 | ⚠️ 重启后未连 WiFi |
| `WifiStation: WiFi connected` / `Got IP` | WiFi 已连 |
| `waiting for download` | 下载模式，无需干预 |
| `abort()` / `Guru Meditation` | 崩溃，修复见 esp32-xiaoclaw-diagnostics |

## xiaozhi-server 日志文件名规律

日志按**日期滚动**：`server.log.YYYYMMDD`，今天是 `server.log.20260802`。

不要 grep `server.log`（可能是空符号链接），要找对日期文件：
```bash
TODAY=$(date +%Y%m%d)
grep '28:84:85:88:f7:e0' /home/saber/xiaozhi-server/xiaozhi_server-linux-amd64-v0.6.4/xiaozhi_server-linux-amd64/logs/server.log."$TODAY"
```

## 服务恢复（自动处理）

### 第一步：诊断根因（先查 binary 是否存在）

```bash
# 检查 xiaozhi-server systemd service 状态
systemctl --user status xiaozhi-server.service 2>&1 | head -15

# 检查 xiaozhi-server 二进制是否存在
find /home/saber -name "xiaozhi_server" -type f 2>/dev/null

# 检查 OTA 代理进程
ss -tlnp | grep 8090
```

### 根因判断矩阵

| 症状 | 根因 | 处理 |
|------|------|------|
| service: `activating (auto-restart)` | ❌ 二进制缺失或损坏 | 无法自动恢复，需重新部署 |
| service: `active (running)` 但端口未监听 | ❌ 配置错误 | 检查 main_config.yaml |
| binary 存在但进程挂了 | ✅ 可自动拉起 | 手动重启 service |
| binary 不存在 | ❌ 需重新下载 | 用户需重新部署 |

### 拉起步骤（仅在 binary 存在时执行）

```bash
# 1. OTA 代理（端口 8090）
# 必须用 background=true，不允许 foreground 加 &
cd /home/saber && python3 xiaozhi-ota-proxy.py
# 验证
curl -s "http://127.0.0.1:8090/xiaozhi/ota/check?mac=test"

# 2. xiaozhi-server（端口 8080 + 8989）
systemctl --user start xiaozhi-server.service
systemctl --user status xiaozhi-server.service 2>&1 | head -10
```

## PC 缓存清理

```bash
# /tmp 构建日志和测试文件
rm -f /tmp/xiaoclaw_build*.log /tmp/idf-build*.log /tmp/build*.log
rm -f /tmp/nvs_*.bin /tmp/wifi_nvs.bin /tmp/partitions_*.bin /tmp/pt*.bin

# xiaozhi-server 旧日志（保留近3天）
rm -f /home/saber/xiaozhi-server/xiaozhi_server-linux-amd64-v0.6.4/xiaozhi_server-linux-amd64/logs/server.log.20260{728,729,730}*

# pip/uv/pnpm 缓存（慎用，重新下载）
# pip cache clean --all
# uv cache clean
```

## 相关技能

- `devops/esp32-xiaoclaw-diagnostics` — ESP32 深度诊断
- `devops/openclaw-ops` — OpenClaw QQ Bot 状态
- `devops/xiaozhi-server` — xiaozhi 后端
