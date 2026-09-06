---
name: py-xiaozhi-ops
description: py-xiaozhi 运维补丁 — LD_LIBRARY_PATH 修复、Hermes LLM 桥接、激活流程。三服务（xiaozhi-server + OTA代理 + py-xiaozhi）协同运维。
triggers:
  - py-xiaozhi
  - 小智激活
  - xiaozhi-server LD_LIBRARY_PATH
  - libten_vad.so
  - py-xiaozhi 启动
---

# py-xiaozhi 运维补丁

## 关键修复（2026-08-02）

### xiaozhi-server 启动依赖 LD_LIBRARY_PATH

**错误信号**：`error while loading shared libraries: libten_vad.so: cannot open shared object file`

**解决方案**：
```bash
bash /home/saber/.hermes/start-xiaozhi-server.sh
```

内容：
```bash
#!/bin/bash
XD="/home/saber/xiaozhi-server/xiaozhi_server-linux-amd64-v0.6.4/xiaozhi_server-linux-amd64"
VAD="$XD/ten-vad/lib/Linux/x64"
export LD_LIBRARY_PATH="$VAD:$LD_LIBRARY_PATH"
cd "$XD" && ./xiaozhi_server -c "$XD/main_config.yaml"
```

用 `terminal(background=true)` 启动，禁止 foreground + `&`。

### py-xiaozhi CLI 模式在服务器上立即退出

**症状**：`python main.py --mode cli` 启动后日志显示工具加载正常，但 2-3 秒后输出"正在关闭应用..."进程退出，exit code 1。

**根因**：CLI 模式依赖实时键盘输入循环（`_keyboard_input_loop()`），服务器无 TTY → 立即退出。这是**正常行为**，不代表配置错误。

**解决方案**：
- **不要**在服务器上用 CLI 模式跑 py-xiaozhi（它需要真实麦克风，应该在有音频设备的客户端电脑上运行）
- 若需验证连接：改用 `--skip-activation` 并检查日志中的 WebSocket 连接状态
- py-xiaozhi 的正确定位：**语音客户端**（麦克风输入端），不是服务器端组件

### py-xiaozhi 配置中的 AUTHORIZATION_URL 必须为 xiaozhi.me

**症状**：`python main.py --mode cli` 启动后挂住（无输出），timeout 25s 后进程退出。

**根因**：`config/config.json` 中 `AUTHORIZATION_URL` 指向了本地 xiaozhi-server（`http://192.168.31.50:8989`），而激活流程需要访问 `https://xiaozhi.me/` 域名验证 license。指向本地地址导致请求挂住。

**修复**：
```json
"AUTHORIZATION_URL": "https://xiaozhi.me/"
```
配置路径：`~/.local/share/py-xiaozhi/config/config.json`

### xiaozhi-server LLM → Hermes Gateway（新架构）

让语音设备的 LLM 请求走 Hermes Gateway：

```yaml
# main_config.yaml
llm:
  provider: "hermes"
  hermes:
    type: "openai"
    model_name: "minimax-m2.5-highspeed"
    api_key: "hermes-api-43f0bff8e7d6b79bbec9d17e1243bec0"
    base_url: "http://127.0.0.1:8642/v1"
    max_tokens: 500
```

链路：`麦克风 → py-xiaozhi(ASR) → xiaozhi-server(WS:8989) → Hermes(/v1/chat/completions)`

## 三服务端口检查

```bash
ss -tlnp | grep -E '8090|8080|8989'
```

| 端口 | 组件 | 说明 |
|------|------|------|
| 8090 | python OTA 代理 | ESP32 OTA check |
| 8080 | xiaozhi-server | Web 管理后台 |
| 8989 | xiaozhi-server | WebSocket（ESP32 + py-xiaozhi） |

> 📄 ESP32/xiaoclaw OTA URL 与固件路径详见 `references/esp32-ota-url-xiaoclaw.md`
