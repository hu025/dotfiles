---
name: py-xiaozhi-setup
description: Complete setup workflow for py-xiaozhi local voice assistant — install, configure, activate, and run with local xiaozhi-server + Hermes Gateway as LLM backend.
triggers:
  - py-xiaozhi
  - 小智 语音助手
  - pyxiaozhi 安装
  - py-xiaozhi 激活
  - local voice assistant ESP32
---

# py-xiaozhi 完整配置指南

## 架构

```
麦克风(唤醒词"你好小智") → py-xiaozhi(ASR+VAD) → xiaozhi-server(WS路由) → Hermes Gateway(LLM大脑) → edge-tts(TTS) → 音箱
```

**关键**：LLM 完全走 Hermes Gateway（`/v1/chat/completions`），xiaozhi-server 只做协议路由。

## 前置条件

- xiaozhi-server 运行中（端口 8080/8989）
- Hermes Gateway 运行中（端口 8642），API key 已知
- 网络可访问 `api.tenclass.net`（激活流程）

## 安装步骤

```bash
# 1. 克隆项目
cd /home/saber && git clone https://github.com/huangjunsen0406/py-xiaozhi.git

# 2. 依赖已安装（用 uv 管理）
cd /home/saber/py-xiaozhi
# venv 路径：/home/saber/py-xiaozhi/.venv
```

## 配置（每次启动前执行）

配置文件：`~/.local/share/py-xiaozhi/config/config.json`

```python
import json
cfg = json.load(open('~/.local/share/py-xiaozhi/config/config.json'))

# 指向本地 xiaozhi-server WebSocket
cfg['SYSTEM_OPTIONS']['NETWORK']['WEBSOCKET_URL'] = 'ws://192.168.31.50:8989/xiaozhi/v1/'

# 激活URL必须用 xiaozhi.me（不是本地服务器，否则hang）
cfg['SYSTEM_OPTIONS']['NETWORK']['AUTHORIZATION_URL'] = 'https://xiaozhi.me/'

json.dump(cfg, open('~/.local/share/py-xiaozhi/config/config.json','w'), indent=2, ensure_ascii=False)
```

⚠️ **AUTHORIZATION_URL 必须用 `https://xiaozhi.me/`**，不能指向本地 xiaozhi-server。py-xiaozhi 用此 URL 拼接激活端点，指向本地会导致激活流程 hang（异步等待 HTTP 202 响应，本地服务器不响应此路径）。

## 配置 xiaozhi-server 的 LLM 指向 Hermes

文件：`/home/saber/xiaozhi-server/xiaozhi_server-linux-amd64-v0.6.4/xiaozhi_server-linux-amd64/main_config.yaml`

```yaml
llm:
  provider: "hermes"
  hermes:
    type: "openai"
    model_name: "minimax-m2.5-highspeed"
    api_key: "hermes-api-43f0bff8e7d6b79bbec9d17e1243bec0"
    base_url: "http://127.0.0.1:8642/v1"
    max_tokens: 500
```

改完需重启 xiaozhi-server：

```bash
pkill -f xiaozhi_server && sleep 1
cd /home/saber/xiaozhi-server/xiaozhi_server-linux-amd64-v0.6.4/xiaozhi_server-linux-amd64
./xiaozhi_server &
```

## 获取激活码

⚠️ **必须先拿到激活码，才能让用户去 xiaozhi.me 激活**

```bash
cd /home/saber/py-xiaozhi && source .venv/bin/activate && timeout 15 python main.py --mode cli 2>&1 | grep -A2 "验证码"
```

输出包含6位激活码（如 `271682`）。进程超时自动退出，不影响。

⚠️ 用 `timeout 15` 不用后台进程：execute_code 的 terminate/kill 均无法杀死此进程（asyncio 事件循环阻塞），terminal 的 timeout 可正常终止。

## 激活流程

1. 运行上面命令获取激活码（如 `271682`）
2. 用户在浏览器打开 [xiaozhi.me](https://xiaozhi.me) → 登录 → 添加设备 → 输入激活码
3. 激活成功后，启动完整程序

## 启动完整程序

```bash
bash /home/saber/.hermes/start-pyxiaozhi.sh
```

启动脚本内容：
```bash
#!/bin/bash
CONFIG="$HOME/.local/share/py-xiaozhi/config/config.json"
python3 -c "
import json
with open('$CONFIG') as f: cfg = json.load(f)
cfg['SYSTEM_OPTIONS']['NETWORK']['WEBSOCKET_URL'] = 'ws://192.168.31.50:8989/xiaozhi/v1/'
cfg['SYSTEM_OPTIONS']['NETWORK']['AUTHORIZATION_URL'] = 'https://xiaozhi.me/'
with open('$CONFIG', 'w') as f: json.dump(cfg, f, indent=2, ensure_ascii=False)
"
cd /home/saber/py-xiaozhi && source .venv/bin/activate && python main.py --mode cli
```

## 日志位置

- py-xiaozhi: `~/.local/share/py-xiaozhi/logs/app.log`
- xiaozhi-server: `/tmp/xiaozhi_server.log`
- Hermes Gateway: `~/.hermes/logs/gateway.log`

## 关键发现

- **execute_code 无法杀死 py-xiaozhi**：进程启动后 asyncio 事件循环阻塞，terminate/kill 均超时 → 用 terminal timeout 命令代替
- **AUTHORIZATION_URL 陷阱**：设本地地址 → 激活流程 hang；必须用 `https://xiaozhi.me/`
- **Hermes API Server**：端口 8642，OpenAI 兼容格式，key = `hermes-api-43f0bff8e7d6b79bbec9d17e1243bec0`
- **py-xiaozhi 的 LLM 请求路径**：py-xiaozhi → WebSocket → xiaozhi-server → Hermes /v1/chat/completions → 返回
