# ESP32/xiaoclaw OTA URL 与 xiaozhi-server 的关系

## 架构链路

```
ESP32 (xiaoclaw)
  ↓ OTA check (CONFIG_OTA_URL)
  ↓
xiaozhi-ota-proxy.py (端口 8090)
  ↓ 返回 WS URL
  ↓
ESP32 建立 WebSocket → xiaozhi-server (端口 8989)
  ↓ LLM 请求
  ↓
Hermes Gateway (端口 8642) ← 当前架构
  (或云端 api.tenclass.net ← 云端独立模式)
```

## 关键文件路径

| 组件 | 路径 |
|------|------|
| xiaoclaw 项目 | `/home/saber/xiaoclaw/` |
| xiaoclaw sdkconfig | `/home/saber/xiaoclaw/sdkconfig` |
| 编译产物 | `/home/saber/xiaoclaw/build/xiaozhi.bin` |
| xiaozhi-server | `/home/saber/xiaozhi-server/xiaozhi_server-linux-amd64-v0.6.4/xiaozhi_server-linux-amd64/` |
| OTA 代理 | `/home/saber/xiaozhi-ota-proxy.py` |

## CONFIG_OTA_URL 设置

`sdkconfig` 中的 `CONFIG_OTA_URL` 必须指向本地 OTA 代理：

```bash
# 改本地模式
grep "CONFIG_OTA_URL" /home/saber/xiaoclaw/sdkconfig
# 应为：http://192.168.31.50:8090/

# ⚠️ set-target esp32s3 后 Kconfig 会重置此值，每次编译前都要检查
```

## ESP32 当前状态判断（串口日志）

| 串口日志 | 含义 | 解法 |
|---------|------|------|
| `System time is not set` + `SystemInfo: free sram`（循环，无 WiFi 日志） | **NVS 无 WiFi 凭据**，ESP32 在等待配网或配网循环 | 需要刷修复版固件（含 WiFi NVS 持久化 + DEBUG 代码修复） |
| `Network connected` + `WS connected` | ✅ ESP32 已连上 xiaozhi-server | 无需操作 |
| `Got IP: 192.168.31.x` 但无 WS 日志 | WiFi 正常，但 WebSocket 未建立 | 检查 OTA 代理 + CONFIG_OTA_URL |
| 不断重启，串口全是 SystemInfo | OTA check 超时 → 初始化失败 → 重启循环 | 检查 OTA 代理是否在 8090 端口监听 |

## 串口读取技巧（无 TTY 时）

```python
import serial, fcntl, os, time
s = serial.Serial('/dev/ttyACM0', 115200, timeout=2)
fd = s.fd
flags = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
s.reset_input_buffer()
time.sleep(1)
data = os.read(fd, 4096)
print(data.decode('utf-8', errors='replace'))
```

## 三服务常驻检查

```bash
ss -tlnp | grep -E '8090|8080|8989'
```

8090 无输出 → OTA 代理死亡 → `cd /home/saber && python3 xiaozhi-ota-proxy.py &`
