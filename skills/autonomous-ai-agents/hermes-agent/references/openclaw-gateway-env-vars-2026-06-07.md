# OpenClaw Gateway — 环境变量加载与 systemd

## 核心教训

**OpenClaw Gateway 从环境变量读取 provider API Key，不从 `openclaw.json` 读取。**

当 Gateway 以 systemd service 运行时，不继承用户 shell 的环境变量（包括 `~/.hermes/.env` 里定义的 `MINIMAX_API_KEY` 等），导致 agent 初始化失败，QQ Bot 无法回复。

## 症状

```
[qqbot] [default] Message processing failed:
  Cannot read properties of undefined (reading 'run')
[gateway] Unhandled promise rejection: Error: Response timeout
```

日志里只看到 "Cannot read properties of undefined"，真正的根因是 **provider 的 apiKey 为 undefined**（未从环境变量读取）。

## 诊断方法

```bash
# 1. 检查 gateway 日志
journalctl --user -u openclaw-gateway.service -n 200 | grep -E "agent|minimax|provider|model|initialize"

# 2. 确认 MINIMAX_API_KEY 是否在 service 环境里
systemctl --user show openclaw-gateway.service | grep MINIMAX

# 3. 手动验证 API key 是否有效（从 ~/.hermes/.env）
source ~/.hermes/.env 2>/dev/null; curl -s -H "Authorization: Bearer $MINIMAX_API_KEY" \
  "https://api.minimaxi.com/anthropic/v1/models" | head -3
```

## 修复方案

在 systemd service drop-in 里加载 `.env` 文件：

```bash
mkdir -p ~/.config/systemd/user/openclaw-gateway.service.d/
```

创建 `~/.config/systemd/user/openclaw-gateway.service.d/env.conf`：

```ini
[Service]
EnvironmentFile=/home/saber/.hermes/.env
```

然后重载：

```bash
systemctl --user daemon-reload
systemctl --user restart openclaw-gateway.service
```

## 验证

重启后检查日志：

```bash
journalctl --user -u openclaw-gateway.service --since "20 seconds ago" | grep -E "agent model|minimax|provider|Gateway ready"
```

应该看到：

```
[gateway] agent model: minimax/MiniMax-M2.7 (thinking=medium, fast=off)
[gateway] http server listening (4 plugins: ...; 14.3s)
[qqbot] [qqbot:default] Gateway ready
```

## 根因：openclaw.json 重复 key 导致 provider 配置损坏

`openclaw.json` 里 `providers.minimax` 有多个重复声明，Python `json.load()` 按最后出现的值覆盖，导致 `apiKey` 被空对象 `{}` 覆盖。

症状：直接 `python3 -c "import json; print(json.load(open('~/.openclaw/openclaw.json'))['providers']['minimax'])"` 输出 `{}`。

但这不影响 OpenClaw，因为 OpenClaw 读环境变量而非 JSON。真正的问题是 **systemd service 缺少 `EnvironmentFile`**。

## 相关路径

- OpenClaw 配置：`~/.openclaw/openclaw.json`
- OpenClaw state DB：`~/.openclaw/state/openclaw.sqlite`
- Gateway service：`~/.config/systemd/user/openclaw-gateway.service`
- Service drop-in：`~/.config/systemd/user/openclaw-gateway.service.d/`
- 环境变量源：`~/.hermes/.env`
