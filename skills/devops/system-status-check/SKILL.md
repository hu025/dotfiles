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
```

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

### 5. 网络连通性
```bash
curl -s -m 3 http://localhost:8642/health 2>/dev/null && echo "Hermes OK"
# OpenClaw 已卸载，不需要检查 18888
```

### 6. OpenClaw 残留验证（彻底清理后）
```bash
# 期望全部为空/0
ps aux | grep openclaw | grep -v grep | wc -l   # 0
ss -tlnp | grep 18888 | wc -l                  # 0
find ~/.npm-global/lib/node_modules/ -iname "*openclaw*" 2>/dev/null | wc -l  # 0
systemctl --user list-units --type=service 2>/dev/null | grep openclaw | grep "not-found"  # 有输出=干净
```

### 已知端口说明
| 端口 | 服务 | 备注 |
|------|------|------|
| 8642 | Hermes Gateway | 核心服务 |
| 43703 | Hermes 内部通信 | 随机高端口，内部 socket |
| 181 | SSH | 非标准端口（从22改），正常 |
| 5355/53 | mDNS/DNS | 系统服务，正常 |

## 清理决策矩阵

| 发现 | 行动 |
|------|------|
| 已删项目的 Docker 容器还在跑 | `docker stop && docker rm` |
| 已删项目的 Docker 镜像占用空间 | `docker rmi` |
| 悬空镜像（dangling） | `docker image prune -f` |
| 未使用的 Docker 镜像 | `docker image prune -a -f` |
| /tmp 残留日志 | `rm -f /tmp/*.log /tmp/*build*` |

## 验证标准

| 项目 | 正常 | 异常 |
|------|------|------|
| 磁盘可用 | > 5GB | < 2GB 需清理 |
| 内存可用 | > 1GB | < 500MB 查泄漏 |
| Hermes Gateway | LISTEN 8642 | 未监听需重启 |
| Docker 容器 | 无残留项目容器 | 有则清理 |
