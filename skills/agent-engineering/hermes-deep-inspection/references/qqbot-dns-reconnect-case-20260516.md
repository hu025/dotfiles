# QQBot DNS Reconnection Failure — Case Study (2026-05-16)

## Symptoms
日志出现：
```
WARNING gateway.platforms.qqbot.adapter: [QQBot:1903866099] Reconnect failed: Failed to get QQ Bot gateway URL: [Errno -5] No address associated with hostname
WARNING gateway.platforms.qqbot.adapter: [QQBot:1903866099] Still not connected after 15s
```

反复重连失败，`api.sgroup.qq.com` DNS 解析间歇性失败。

## Root Cause
DNS 解析 `api.sgroup.qq.com` 失败（可能是腾讯服务器端 DNS 抖动，或 DNS 服务临时不可达），导致获取 QQ Gateway URL 的 HTTP 请求失败。

## Why SIGUSR1 Alone Doesn't Fix It
SIGUSR1 触发 `restart_signal_handler()` → 调用 `restart_gateway()` → 但 `_listen_loop`（WebSocket 监听循环）内部的 reconnect 逻辑有 bug：当 `_running=True` 且 `is_connected=False` 时，loop 不会自动唤醒重连，导致 listener 永久卡在 disconnected 状态。

## 正确修复
```bash
systemctl --user restart hermes-gateway.service
```
完全重启服务，重新初始化所有 adapter。

## Verification
```bash
tail -5 ~/.hermes/logs/gateway.log | grep -i "qqbot\|qq"
# 应看到：
# INFO gateway.platforms.qqbot.adapter: [QQBot:1903866099] Ready
```

## 端口映射参考
- OpenClaw (node): port **18888** — HTTP health check: `curl -s http://localhost:18888/health` → `{"ok":true}`
- Hermes Gateway (python): 无 HTTP 端点，纯 WebSocket，不可用 HTTP 健康检查