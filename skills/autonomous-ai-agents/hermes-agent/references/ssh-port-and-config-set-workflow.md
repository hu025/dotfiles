# SSH Port Migration + hermes config set Workflow

## SSH Port Migration (Linux)

Bidirectional migration between ports (e.g. 22 ↔ 181). Current state on this system: port **181**.

### 22 → 181（本次已完成）
```bash
# 编辑 sshd_config：注释原端口，加新端口
sudo sed -i 's/^Port 22/#Port 22\nPort 181/' /etc/ssh/sshd_config
sudo grep -E '^Port' /etc/ssh/sshd_config   # 验证

# 重启并检查
sudo systemctl restart sshd
ss -tlnp | grep ':181'   # 应有 LISTEN 行

# 防火墙检查
sudo iptables -L INPUT -n | grep 181 || echo "无阻断"
```

### 181 → 22（反向操作同理）
```bash
sudo sed -i 's/^Port 181/#Port 181\nPort 22/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

> 注意：SSH 换端口后，**本地会话保持不断**，新端口立即生效。远程客户端需更新连接命令：`ssh -p 181 user@host`。

> Note: Linux SSH port migration is a standard admin task — not hermes-agent-specific.

## Config Modification: ALWAYS use `hermes config set`

`~/.hermes/config.yaml` is a **protected system/credential file**. Direct patch/edit via `patch` tool or `write_file` will be denied with:
```
Write denied: '/home/saber/.hermes/config.yaml' is a protected system/credential file.
```

**Correct approach:**
```bash
# From hermes-agent venv
cd ~/.hermes/hermes-agent
source venv/bin/activate
hermes config set model.default mistralai/mistral-small-4-119b-2603

# Any config key works
hermes config set model.provider nvidia
hermes config set model.default <model_id>
```

Equivalent to `hermes config set section.key value` per CLI reference.

## Model Switching (NVIDIA)

NVIDIA provider is pre-configured in `providers.nvidia`. Available models:
- `mistralai/mistral-small-4-119b-2603` — main workhorse (default)
- `mistralai/mistral-nemotron` — fast auxiliary tasks
- `mistralai/mistral-medium-3.5-128b` — premium quality
- `nvidia/nvidia-nemotron-nano-9b-v2` — embedded/nano

Switch with:
```bash
hermes config set model.default mistralai/mistral-small-4-119b-2603
```

Changes take effect on next session (`/reset` in chat, or new `hermes` invocation). For gateway, use `/restart`.

## OpenClaw Health Check Sequence

```bash
# 1. Health endpoint
curl -s http://127.0.0.1:18888/health

# 2. Process status
ps aux | grep -E 'openclaw|node' | grep -v grep

# 3. Watchdog log (includes stderr)
tail -5 /home/saber/.hermes/openclaw-watchdog.log
```
