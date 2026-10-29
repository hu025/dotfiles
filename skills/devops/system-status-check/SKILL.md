---
name: system-status-check
description: PC 全维度状态一键检查 — 硬件/内存/磁盘/网络/端口/Docker容器/后台服务。触发词：检查电脑状态、PC状态、系统状态、检查整个电脑系统、电脑检查
triggers:
  - 检查电脑状态
  - PC状态
  - 系统状态
  - 检查整个电脑系统
  - 电脑检查
  - 全面检查
---

# PC 全维度状态检查

## 快速检查 all-in-one

```bash
# 1. Docker（先查！skill/代码删除 ≠ 容器停止，xiaozhi 等项目易遗漏）
docker ps -a --format "table {{.ID}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}" && echo "---镜像占用---" && docker images --format "table {{.Repository}}\t{{.Size}}"

# 2. 系统/内存/磁盘
uname -sr && free -h | head -2 && df -h / | tail -1

# 3. 端口服务（Hermes 为主，OpenClaw 已卸载）
ss -tlnp | grep -E "8642|8080|8090"

# 4. 进程内存TOP5
ps aux --sort=-%mem | grep -v grep | head -6

# 5. Cron 失败检查（HTTP 402 = MiniMax 额度耗尽；failure_streak 非 0 = 持续失败）
ls -lt ~/.hermes/cron/output/ 2>/dev/null | head -5
python3 -c "
import json
with open('/home/saber/.hermes/cron/jobs.json') as f:
    d = json.load(f)
for j in d['jobs']:
    en = '✓' if j.get('enabled') else '✗'
    fail = j.get('failure_streak', 0)
    ms = (j.get('model_snapshot') or '')[:12]
    name = j.get('name', '?')[:28]
    print(f'[{en}] [{fail}] {name} | {ms}')
"

# 6. MiniMax API 直接验证（gateway 正常 ≠ API key 有效）
key=$(python3 -c "
with open('/home/saber/.hermes/.env','rb') as f: c=f.read()
i=c.find(b'MINIMAX_API_KEY='); e=c.find(b'\n',i)
print(c[i+16:e].decode())
")
curl -s --max-time 15 -X POST "https://api.minimax.chat/v1/text/chatcompletion_v2" \
  -H "Authorization: Bearer $key" \
  -H "Content-Type: application/json" \
  -d '{"model":"minimax-m3","messages":[{"role":"user","content":"hi"}],"max_tokens":20}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); c=d.get('choices',[{}])[0].get('message',{}).get('content','空'); print('OK' if c else '空内容(M3 reasoning正常，加大max_tokens)')"

## 分项详解

### 1. 硬件状态
```bash
# CPU + 核心数
nproc && cat /proc/cpuinfo | grep "model name" | head -1

# 内存
free -h

# 磁盘
df -h /
```

### 2. 端口服务
| 端口 | 服务 | 备注 |
|------|------|------|
| 8642 | Hermes Gateway | 核心服务 |
| 181 | SSH | 非标准端口（从22改），正常 |
| 5355/53 | mDNS/DNS | 系统服务，正常 |

未知端口排查（按 inode 追踪进程）：
```bash
# 1. 确认端口响应
python3 -c "import socket; s=socket.socket(); s.settimeout(1); s.connect(('127.0.0.1', PORT)); print(s.recv(1024))"

# 2. 查 inode
cat /proc/net/tcp | awk 'NR>1 {split($2,a,":"); if(strtonum("0x"a[2])==PORT) print $10}'

# 3. inode→进程
for pid in /proc/[0-9]*; do for fd in $pid/fd/*; do [ -L "$fd" ] && readlink "$fd" 2>/dev/null | grep -q "socket:\[INODE\]" && echo "PID: $(basename $pid)"; done; done
```

### 3. Docker 容器（重要！项目清理时容易遗漏）
```bash
# 检查是否有残留容器
docker ps -a

# 检查镜像占用
docker images

# 删除残留容器（如 xiaozhi 等已清理项目）
docker stop $(docker ps -a -q --filter "ancestor=*xiaozhi*") 2>/dev/null
docker rm $(docker ps -a -q --filter "ancestor=*xiaozhi*") 2>/dev/null
docker rmi $(docker images -q --filter "reference=*xiaozhi*") 2>/dev/null
```

**关键原则：skill/代码删除 ≠ Docker 容器停止。检查 `docker ps -a` 是项目清理的第一步。**

### 4. 后台进程
```bash
ps aux --sort=-%mem | head -10
```

### 5. Cron 健康检查
```bash
# 检查最新失败任务的错误类型
ls -lt ~/.hermes/cron/output/ | head -3
cat ~/.hermes/cron/output/$(ls -t ~/.hermes/cron/output/ | head -1)/$(ls -t ~/.hermes/cron/output/$(ls -t ~/.hermes/cron/output/ | head -1)/ | head -1) 2>/dev/null | grep -E "402|410|Error|Traceback" | head -5

# 查看 cron 模型配置
python3 -c "
import json
with open('/home/saber/.hermes/cron/jobs.json') as f:
    d = json.load(f)
for j in d['jobs']:
    ms = j.get('model_snapshot') or '(default)'
    print(f'{j[\"name\"]:25s} model={ms} fail={j.get(\"failure_streak\",0)}')
"

# HTTP 402 = 模型额度耗尽；HTTP 410 = 模型 EOL（已下线）；
# 应检查 ~/.hermes/self-improvement/agent_core.py 中的模型名是否仍有效
```

**Pitfall**: `hermes cron create --script <path>` 只接受相对路径（相对 `~/.hermes/scripts/`）。绝对路径会报 "Script path must be relative to /home/saber/.hermes/scripts/"。先 `cp script.py ~/.hermes/scripts/`，再 `--script script.py`。

### 5b. 网络连通性
```bash
curl -s -m 3 http://localhost:8642/health 2>/dev/null && echo "Hermes OK"
```

### OpenClaw 彻底清理（多层级检查）

```bash
# Layer 1: 进程
ps aux | grep openclaw | grep -v grep | wc -l  # 期望 0

# Layer 2: npm 全局包
npm list -g --depth=0 2>/dev/null | grep openclaw
npm uninstall -g openclaw openclaw-qqbot @tencent-connect/openclaw-qqbot 2>/dev/null

# Layer 3: npm global node_modules
find ~/.npm-global -iname "*openclaw*" 2>/dev/null
# 连带清理 openclaw 插件（如 @martian-engineering/lossless-claw）
npm uninstall -g @martian-engineering/lossless-claw 2>/dev/null

# Layer 4: npm cache
rm -rf ~/.npm
du -sh ~/.npm  # 确认清理

# Layer 5: 运行时目录和日志
rm -rf ~/.openclaw ~/openclaw.log
du -sh ~/.openclaw  # 确认清理

# Layer 6: systemd user service
systemctl --user stop openclaw 2>/dev/null
systemctl --user disable openclaw 2>/dev/null
rm -f ~/.config/systemd/user/openclaw.service
systemctl --user daemon-reload
systemctl --user list-units --type=service 2>/dev/null | grep openclaw
# "not-found" = 干净；"failed" = 有历史记录但 unit 文件已删

# Layer 7: hermes skills 中的迁移参考文档
find ~/.hermes/skills ~/dotfiles/skills -iname "*openclaw*" -type d -not -path "*/.git/*" 2>/dev/null
# 删除 openclaw-adapter-migration、openclaw-migration 等迁移 skill

# Layer 8: hermes scripts 中的 openclaw 硬编码
grep -r "openclaw" ~/.hermes/scripts/ --include="*.py" -l 2>/dev/null
grep -r "openclaw" ~/dotfiles/bin/ --include="*.py" --include="*.sh" -l 2>/dev/null
# ETF 监控等脚本的 openclaw QQ 告警调用需重写

# Layer 9: 环境变量
env | grep -i openclaw
```

**关键原则：skill/代码删除 ≠ 进程/容器/配置清理。逐层检查才能彻底。**

**已知 openclaw 残留位置（非运行组件，无需删除）：**
- `~/package/` — Hermes 源码（root 权限），内置测试数据，非 openclaw 组件
- `/mnt/usb/` — 外接 U 盘备份，物理隔离，不影响本机

### 已知端口说明
| 端口 | 服务 | 备注 |
|------|------|------|
| 8642 | Hermes Gateway | 核心服务 |
| 43703 | Hermes 内部通信 | 随机高端口，内部 socket，无法通过 fuser 追踪进程 |
| 181 | SSH | 非标准端口（从22改），安全措施，正常 |
| 5355/53 | mDNS/DNS | 系统服务，正常 |

## 清理决策矩阵

| 发现 | 行动 |
|------|------|
| 已删项目的 Docker 容器还在跑 | `docker stop && docker rm` |
| 已删项目的 Docker 镜像占用空间 | `docker rmi` |
| 悬空镜像（dangling） | `docker image prune -f` |
| 未使用的 Docker 镜像 | `docker image prune -a -f` |
| /tmp 残留日志 | `rm -f /tmp/*.log /tmp/*build*` |

## Hermes 升级 Troubleshooting

### GitHub 网络不通
```bash
# HTTPS 测速
curl -fsSL --max-time 10 https://github.com/NousResearch/hermes-agent/archive/refs/tags/v2026.8.27.tar.gz 2>&1

# SSH 测速
GIT_SSH_COMMAND="ssh -o ConnectTimeout=15" git ls-remote --tags origin 2>&1 | head -3
```

**症状：**
- HTTPS: `curl: (28) Operation timed out` 或 `Operation too slow. Less than 1000 bytes/sec`
- SSH fetch: `timeout` 但 `git ls-remote` 可以列出 tags
- PyPI: `pip index versions` 返回的版本低于 Gateway 实际版本

**当前环境：GitHub HTTPS 和 SSH fetch 均超时，Gateway 已是最新可运行版本。**

**已知最新版本：**
| 版本 | 日期 | 说明 |
|------|------|------|
| v0.22.0 | 2026.9.24 | 最新，600+ 插件，e06df9c2eae6 |
| v0.20.6 | 2026.8.27 | 525 PRs |
| v0.20.0 | 2026.8.3 | The Herald Release |

**注：Gateway 版本高于 CLI 版本是正常现象（Gateway 是独立升级路径）。**

## 验证标准

| 项目 | 正常 | 异常 |
|------|------|------|
| 磁盘可用 | > 5GB | < 2GB 需清理 |
| 内存可用 | > 1GB | < 500MB 查泄漏 |
| Hermes Gateway | LISTEN 8642 | 未监听需重启 |
| Cron 任务 | 检查失败任务 | 查看 `~/.hermes/cron/output/{job_id}/` 目录 |
| Cron 全部 worker 报 `ModuleNotFoundError: No module named 'ruamel.yaml'` | `~/.local/lib/python3.14/site-packages/ruamel.base-1.0.0-py3.4-nspkg.pth` 创建了空namespace package遮蔽site-packages的`ruamel/yaml/`。修复：`rm ~/.local/lib/python3.14/site-packages/ruamel.base-1.0.0-py3.4-nspkg.pth`。根因通常是 `pip install -e .` 重装源包时旧的pth文件未清理 |
| Cron 模型错误 | ⚠️ 402/410 | `agent_core.py` 硬编码 `minimax-m2.7` 需改为 `minimax-m3`；cron `model_snapshot` 也要同步 |
| 模型配置 | 需确认为 m3 | `grep 'model:' ~/.hermes/config.yaml` 查看主模型；`echo $HERMES_MODEL` 查看环境变量；当前 config 中 `model: minimax-m3` 在 line 298 |
| M3 reasoning 特性 | 正常现象 | M3 在 max_tokens 较小时 reasoning_content 会占满 token导致 content 为空，加大 max_tokens（≥200）即可正常 |

## 快速升级 Hermes（GitHub 不通时）

当 GitHub 访问超时时，用本地 tag 强制切换：
```bash
cd ~/.hermes/hermes-agent
# 确认 tag 在本地
git tag -l | grep v0.2
# 强制切换（不联网）
git reset --hard v0.22.0
# 重装包
# 先确认当前 hermes-agent 的 python 解释器路径 (venv 目录可能被迁移过)
HP=$(ls ~/.hermes/hermes-agent/venv/bin/python3 2>/dev/null || ls ~/.hermes/hermes-agent/.venv/bin/python3 2>/dev/null)
"$HP" -m pip install -e . --upgrade
# 验证
~/.hermes/hermes-agent/.hermes/bin/hermes --version
~/.hermes/hermes-agent/.hermes/bin/hermes update --check
```

**Pitfall**: `pip install -e .` 必须用 venv 中的 python3 执行，不能用系统 pip，否则破坏 venv。
**更严重**: `pip install -e .` 会重装依赖，可能让原本正常的包 import 失败 (2026-10-15 实测: 触发 `ruamel.base-1.0.0-py3.4-nspkg.pth` 创建空 namespace package `ruamel`, 遮蔽 site-packages 里的 `ruamel/yaml/`, 导致所有 Cron worker 报 ModuleNotFoundError)。
**执行前必须**: 1) 备份 ~/.hermes/config.yaml; 2) 记录 `~/.local/lib/python*/site-packages/*.pth` 现状; 3) 装完立刻验证 `python -c "import ruamel.yaml"`。
venv 路径不要写死, 先用 `ls ~/.hermes/hermes-agent/venv/bin/python3` 探测。

**Pitfall**: `hermes config set model` 命令有时超时（config 写入正常），用 `grep model: ~/.hermes/config.yaml` 验证实际值。
| Docker 容器 | 无残留项目容器 | 有则清理 |
