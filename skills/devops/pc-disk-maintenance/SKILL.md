---
name: pc-disk-maintenance
description: PC 磁盘状态检查与安全清理 — 分析磁盘占用、识别可清理目标、清理不常用项目。触发词：检查磁盘、清理磁盘、磁盘满了、哪些不常用、磁盘占用、检查电脑磁盘
triggers:
  - 检查磁盘
  - 清理磁盘
  - 磁盘满了
  - 哪些不常用
  - 磁盘占用
  - 检查电脑磁盘
  - 清理不安全的
---

# PC 磁盘维护

## 一句话结论优先

用户只问磁盘状态或问"哪些不常用" → 先给总览表格，再给可清理项列表。

## 磁盘占用总览

```bash
df -h / && echo "---" && du -sh /home/saber/* /home/saber/.* 2>/dev/null | sort -rh | head -20
```

## 大目录深度分析

识别出大目录后，深度查看内容：
```bash
# .gradle 构建缓存
du -sh /home/saber/.gradle/* 2>/dev/null | sort -rh

# venvs
du -sh /home/saber/.venvs/* 2>/dev/null | sort -rh

# .local/share (pnpm/uv/icons)
du -sh /home/saber/.local/share/* 2>/dev/null | sort -rh | head -10

# npm 全局包
ls /home/saber/.npm-global/lib/node_modules

# .cache 细项
du -sh /home/saber/.cache/* 2>/dev/null | sort -rh | head -10
```

## 安全清理清单

**可安全清理**（不影响运行）：

| 目标 | 大小参考 | 命令 |
|------|---------|------|
| npm 全局缓存 | ~1-3G | `rm -rf ~/.npm` |
| npm 全局已安装包 | ~300-500M | `rm -rf ~/.npm-global/lib/node_modules/openclaw` |
| uv 下载缓存 | ~300MB-4G | `rm -rf ~/.cache/uv/*` |
| pip 缓存 | ~100-200M | `rm -rf ~/.cache/pip` |
| openclaw cache | ~40M | `rm -rf ~/.cache/openclaw` |
| Espressif IDF 缓存 | ~300-800M | `rm -rf ~/.cache/Espressif` |
| hermes sessions 旧文件 | >3天 | `find ~/.hermes/sessions/ -name "*.json" -mtime +3 -delete` |
| /tmp 构建产物 | 不固定 | `rm -f /tmp/xiaoclaw_build*.log /tmp/idf-build*.log` |

**需确认后再删**：

| 目标 | 风险 | 判断方法 |
|------|------|---------|
| `.gradle` | Android/Flutter 构建缓存 | 巨大时确认是否还用 Android/Flutter |
| `.espressif` | ESP-IDF 工具链 | ESP32 项目已清理则可删（~2.5G） |
| `.pub-cache` | Dart/Flutter 包缓存 | Flutter 不再使用则可删 |
| `.idf-venv` | ESP-IDF Python 环境 | esp-idf 删除后无用（~89M） |
| `.agent-reach-venv` | Agent Reach 虚拟环境 | 不再使用则可删（~83M） |
| `.local/share/pnpm` | pnpm 全局存储 | 旧项目残留，通常可删（~1.4G） |
| `.cache/Espressif` | ESP 工具链缓存 | esp-idf 删除后无用（~260M） |
| 项目目录 | xiaoclaw/xiaozhi/esp-idf | ESP32 不再用则全删（~6G） |

## OpenClaw 彻底清理（含 npm 全局包 + systemd）

**核心原则：npm uninstall ≠ 彻底卸载。必须同时清理全局已安装包和 systemd。**

```bash
# 1. npm uninstall（清理包）
npm uninstall -g openclaw openclaw-qqbot @tencent-connect/openclaw-qqbot @martian-engineering/lossless-claw 2>&1 | tail -3

# 2. 清理 OpenClaw 主目录（1-2GB，容易漏！）
du -sh ~/.openclaw/ ~/openclaw.log ~/openclaw-*.tgz 2>/dev/null
rm -rf ~/.openclaw ~/openclaw.log ~/openclaw-*.tgz

# 3. 清理 npm 全局 node_modules（仅 uninstall 不够）
du -sh ~/.npm-global/lib/node_modules/openclaw 2>/dev/null
rm -rf ~/.npm-global/lib/node_modules/openclaw \
       ~/.npm-global/lib/node_modules/openclaw-qqbot \
       ~/.npm-global/lib/node_modules/.openclaw-update-stage-* \
       ~/.npm-global/node_modules/.bin/openclaw

# 4. 清理 watchdog 脚本和配置
rm -f ~/.hermes/openclaw-watchdog.sh \
       ~/.hermes/openclaw-watchdog.log \
       ~/.config/fix-openclaw-config.sh

# 5. 清理 hermes_workspace 里的 openclaw 残留
rm -rf ~/hermes_workspace/openclaw-portable \
       ~/hermes_workspace/downloads/oc

# 6. 清理 systemd user service（关键！）
systemctl --user stop openclaw 2>/dev/null
systemctl --user disable openclaw 2>/dev/null
rm -f ~/.config/systemd/user/openclaw.service
rm -rf ~/.config/systemd/user/openclaw.service.d
systemctl --user daemon-reload

# 7. 验证：确认 not-found（unit文件不存在=干净）
systemctl --user list-units --type=service 2>/dev/null | grep openclaw
# 期望输出: "not-found" 而非 "loaded failed failed"
```

**清理完成后最终验证**：
```bash
ps aux | grep openclaw | grep -v grep          # 期望: 0行
ss -tlnp | grep 18888                          # 期望: 无输出
find ~/.npm-global/lib/node_modules/ -iname "*openclaw*" 2>/dev/null | wc -l  # 期望: 0
systemctl --user list-units --type=service 2>/dev/null | grep openclaw | grep "not-found"  # 期望: 匹配
```

## 项目级完整清理

ESP32/语音AI项目彻底清理（示例：xiaozhi）：
```bash
# 1. 先查 Docker 容器（skill删除后容器往往还在跑！）
docker ps -a --format "table {{.ID}}\t{{.Image}}\t{{.Status}}" | grep -i xiaozhi

# 2. 停止并删除容器
docker stop $(docker ps -a -q --filter "ancestor=*xiaozhi*") 2>/dev/null
docker rm $(docker ps -a -q --filter "ancestor=*xiaozhi*") 2>/dev/null

# 3. 删除镜像（释放磁盘空间）
docker rmi $(docker images -q --filter "reference=*xiaozhi*") 2>/dev/null

# 4. 删除所有未使用的悬空镜像
docker image prune -a -f

# 5. 清理源代码目录
rm -rf /home/saber/xiaoclaw \
       /home/saber/xiaozhi-esp32-server \
       /home/saber/xiaozhi-esp32-server-golang \
       /home/saber/xiaozhi-server \
       /home/saber/py-xiaozhi \
       /home/saber/esp-idf
```

**关键原则：skill/代码删除 ≠ Docker容器停止。检查 `docker ps -a` 是项目清理的第一步。**

## 清理后验证

```bash
df -h /
```
