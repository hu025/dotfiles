---
name: usb-portable-hermes
description: Hermes USB 便携部署 — 将 hermes-agent 完整部署到U盘，随插即用
tags: [hermes, openclaw, usb, portable, deployment]
created: 2026-05-30
updated: 2026-06-28
---

# Hermes USB 便携部署

## ⚠️ USB 挂载状态检测（第一步！）

USB 可能**未挂载**！访问 `/mnt/usb` 前必须先检查：

```bash
# 方法1：检查设备号（最可靠）
stat -f /mnt/usb
# ext2/ext3 → 本地目录，未挂载 U盘
# NTFS/FAT → 真实 U盘

# 方法2：blkid 查 UUID
blkid | grep sdb1
# /dev/sdb1: LABEL="agent" UUID="46BE8B4FBE8B3709" TYPE="ntfs"
# 有输出 → U盘存在

# 方法3：mount | grep sdb
mount | grep sdb1
# 无输出 → 未挂载
```

**未挂载时症状**：`/mnt/usb` 是本地 SSD 上的空目录（设备号 8,2 = /dev/sda2），看不到 Hermes/OpenClaw 目录。

**挂载命令**：
```bash
sudo mount -t ntfs-3g /dev/sdb1 /mnt/usb -o uid=1000,gid=1000,umask=0
```

⚠️ **不要 remount**（`mount -t ntfs-3g` 会覆盖现有挂载关系）。首次 mount 即可。

## 实际 USB 目录结构（2026-06-28）

```
U 盘根目录/
├── Hermes/              # hermes-agent 源码 git 仓库（大写 H，~12288 项）
│   └── hermes-agent/    # ← git reset --hard origin/main 升级
├── Hermes/node/         # Windows Node.js 便携版（PE32+可执行文件，仅Windows用）
├── OpenClaw/            # OpenClaw（大写 O，与小写并存）
├── openclaw/            # OpenClaw（小写 o，含 node_modules）
│   └── node_modules/@tencent-connect/openclaw-qqbot/  # ← npm install 升级
├── node/                # Windows Node.js 便携版（PE32+，与 Hermes/node/ 二选一）
├── codex/               # Codex CLI
├── opencode-portable/   # OpenCode 便携版
├── .claude/             # Claude 配置
├── .pnpm-store/         # pnpm 缓存
├── tmp/                 # 临时文件
├── $RECYCLE.BIN/        # Windows 回收站
└── System Volume Information/
```

> ⚠️ `hermes-venv/` + `hermes-home/` 旧目录已废弃。升级时：
> - **hermes-agent 源码** → `cd /mnt/usb/Hermes/hermes-agent && git reset --hard origin/main`
> - **openclaw-qqbot** → `cd /mnt/usb/openclaw && npm install @tencent-connect/openclaw-qqbot@latest`
> - **claude-code npm** → `cd /mnt/usb/node && npm install @anthropic-ai/claude-code@latest --prefer-offline`
> - **opencode-ai npm** → `cd /mnt/usb/opencode-portable/opencode && npm install opencode-ai@latest --prefer-offline`
> - **Windows 运行时（Node.js/Python/codex.exe）** → 必须在 Windows 上下载替换，Linux 无法操作 PE 文件

## USB 安全弹出

```bash
USB_DEV="/dev/sdb1"
USB_MNT="/mnt/usb"

sync && sudo umount "$USB_MNT"
sudo udisksctl power-off -b "$USB_DEV"
sleep 3
lsblk "$USB_DEV"   # SIZE=0B → 可安全拔除
```

⚠️ 残留挂载点：U盘拔出后 `/mnt/usb` 变成普通本地目录（设备号变 sda2），勿误认为 U盘内容。

## 实际 USB 目录结构（2026-05-30 重构后）

```
USB 根目录/
├── hermes-venv/              # 全新安装，Python 3.14 + hermes-agent 0.15.2 (153MB)
│   └── lib/python3.14/site-packages/
├── hermes-home/              # 旧数据保留 (~2.4GB)，含 sessions/skills/cron/logs
├── openclaw/                 # 全新安装，OpenClaw 2026.5.27 (~723MB)
├── bin/                      # wrapper 脚本（hermes/hermes-gateway/openclaw）
│   ├── hermes → hermes-venv/bin/hermes（符号链接或 shim）
│   ├── hermes-gateway        # 看门狗脚本
│   └── openclaw
├── portable/                 # Windows 便携 Python/Node（首次运行自动下载）
│   ├── python/
│   └── node/
├── hermes-agent.whl          # 源码 wheel 备份
├── start-hermes-usb.bat     # Windows 主入口
└── start.sh                  # Linux 主入口
```

> **重要**：`bin/hermes-gateway` 是看门狗脚本（bash while 循环），不是二进制。它用 venv Python 执行 `hermes_cli.main gateway run`，任何退出码 5 秒后重启。

### USB 组件升级流程（2026-06-28 实测）

```bash
USB=/mnt/usb

# 0. 先确认 U 盘真实挂载（避免操作本地 SSD 目录）
blkid | grep sdb1    # 有 UUID=46BE8B4FBE8B3709 → 真实 U 盘
mount | grep sdb1    # 有输出 → 已挂载

# 0b. 解决 git safe directory 问题
git config --global --add safe.directory "$USB/Hermes/hermes-agent"

# 1. hermes-agent 源码（git 仓库）— Linux 升级
cd $USB/Hermes/hermes-agent
git fetch origin --tags   # 拉取最新标签（可能需要 30s-2min）
git tag --sort=-v:refname | head -3  # 查看可用版本
git checkout -f <目标版本>   # 例如 v2026.8.27 或 origin/main
# ⚠️ 如果提示 "needs merge"（从旧 tag 跳新 tag 导致），先 git merge --abort

# 2. venv 同步（hermes-agent 升级后必须）
cd $USB/Hermes/hermes-agent
uv pip install --python venv/bin/python -r pyproject.toml
# 或用系统 uv（跨版本 Python 兼容）：
# uv pip install --python /path/to/venv/bin/python -r pyproject.toml

# 3. 验证升级结果
git log --oneline -1    # 应显示新版本 tag commit
venv/bin/python -c "import hermes_cli; print(hermes_cli.__file__)"  # 应无报错

# 4. openclaw-qqbot npm 包 — Linux 升级
cd $USB/openclaw
npm install @tencent-connect/openclaw-qqbot@latest
# 验证：npm ls @tencent-connect/openclaw-qqbot → 1.7.2 等最新版本
# dist/src/gateway.js 时间戳应更新

# 3. claude-code npm 包 — Linux 升级
cd $USB/node
npm install @anthropic-ai/claude-code@latest --prefer-offline
# 验证：cat $USB/node/node_modules/@anthropic-ai/claude-code/package.json | python3 -c "import json,sys; print(json.load(sys.stdin)['version'])"

# 4. opencode-ai npm 包（opencode 内部依赖）— Linux 升级
cd $USB/opencode-portable/opencode
npm install opencode-ai@latest --prefer-offline
# 注意：这只更新 npm 元数据，实际 Windows exe 仍需在 Windows 上跑 update.bat

# 5. hermes-agent pip 包 — Linux 升级（如需）
# pip install hermes-agent 最新版即为本地版本，通常无需处理

# 6. Windows 运行时（Node.js/Python/codex.exe）— 必须在 Windows 上操作
# Linux 无法执行 NTFS 上的 Windows PE 文件
# → 插到 Windows 机器，下载新版覆盖 codex/、Hermes/node/、portable/python/
# → 运行 opencode-portable/update.bat 更新 opencode.exe
```

> ⚠️ `git reset --hard origin/main` 而非 `git pull`：确保精确对应远程 HEAD，避免 merge commit 污染历史。
> ⚠️ `git remote show origin` 先确认默认分支名（可能是 `main` 而非 `master`）。
> ⚠️ weixin.py 有本地自定义修复时，需从本地 `~/.hermes/hermes-agent/` 复制覆盖 USB。

⚠️ **不要 remount USB**（mount -t ntfs-3g 会覆盖现有挂载关系）。
⚠️ **weixin.py 修改后需手动同步** 到 hermes-venv/lib/python3.14/site-packages/gateway/platforms/。

### GitHub CDN TLS 下载限制（codex.exe 无法在 Linux 下载）

某些 GitHub CDN IP（约 `f4937fc2*` 哈希）对 `github.com` 的 TLS 证书 SAN 不匹配，导致大文件下载失败：
```
curl: (56) OpenSSL SSL_read: ... error:0A000126:SSL routines::unexpected eof while reading
wget: (5) Server rejected
```
**影响**：OpenAI codex CLI (~299MB) 无法从 Linux 直接下载。
**解决**：到 Windows 机器下载 `codex-x86_64-pc-windows-msvc.exe` 替换 `/mnt/usb/codex/codex.exe`。
**检查最新版本**：`curl -s "https://api.github.com/repos/openai/codex/releases/latest" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tag_name'))"`
（小文件 `curl -L --retry 3 --ssl-no-revoke` 可能仍可下载，但 200MB+ 必失败）

### ⚠️ `du` 在 NTFS 上极慢（2026-06-28 实测）

`du -sh /mnt/usb/Hermes/` 等命令在 NTFS 上会超时（30s+），因为 NTFS 目录项多（~12288 项 Hermes 目录）且 NTFS-3G 驱动效率低。

**实测**：`du -sh /mnt/usb/Hermes/ /mnt/usb/Hermes/hermes-agent/ /mnt/usb/Hermes/hermes-agent/venv/ /mnt/usb/openclaw/` 全部超时。

**替代方案**：
```bash
# 用 ls 估算大小（快得多）
ls /mnt/usb/Hermes/hermes-agent/venv/bin/python3  # 验证 venv 存在
git -C /mnt/usb/Hermes/hermes-agent describe --tags  # 验证版本

# 用 rsync dry-run 估算总量（比 du 快）
rsync -avn /home/saber/.openclaw/ /mnt/usb/openclaw/ | tail -5
# 最后一行的 total size 即源目录大小
```



## 构建 hermes-venv（Linux）

推荐用系统 Python 3.14 创建 venv，然后 pip 安装 hermes-agent：

```bash
# 方法1：系统 Python（推荐，最简）
python3 -m venv /mnt/usb/hermes-venv
/mnt/usb/hermes-venv/bin/pip install hermes-agent --upgrade

# 方法2：uv（如果系统 Python 版本不够新）
uv python install 3.14 --install-dir /mnt/usb/hermes-venv/
uv venv /mnt/usb/hermes-venv/ --python 3.14
source /mnt/usb/hermes-venv/bin/activate
pip install hermes-agent==0.15.2
```

⚠️ **不要用 python-build-standalone embed zip**（20260510 起已不含 embed zip，改用 install_only tarball）。

验证：
```bash
/mnt/usb/hermes-venv/bin/hermes --version
/mnt/usb/hermes-venv/bin/python3 -c "import hermes_cli; print(hermes_cli.__version__)"
```

## weixin.py 本地修改同步

hermes-venv 的 `gateway/platforms/weixin.py` 是运行时实际加载的文件。
每次同步源码树后，必须手动复制到 venv：

```bash
sudo cp ~/.hermes/hermes-agent/gateway/platforms/weixin.py \
   /mnt/usb/hermes-venv/lib/python3.14/site-packages/gateway/platforms/weixin.py
```

验证：
```bash
grep -c "重新登录\|qr_login" /mnt/usb/hermes-venv/lib/python3.14/site-packages/gateway/platforms/weixin.py
# 应返回 ≥2
```

## OpenClaw 同步到 USB（推荐方法）

```bash
# 1. 全局安装到本地 npm 环境
npm install -g openclaw@latest

# 2. 复制到 U 盘（npm 把包安装到固定位置）
cp -r $(npm root -g)/openclaw /mnt/usb/openclaw

# 3. 修复嵌套目录结构（cp 会生成 openclaw/openclaw/，需要提一层）
# 仅当 openclaw/openclaw/openclaw.mjs 存在时才需要
if [ -f "/mnt/usb/openclaw/openclaw/openclaw.mjs" ]; then
  mv /mnt/usb/openclaw/openclaw/* /mnt/usb/openclaw/
  rmdir /mnt/usb/openclaw/openclaw
fi
```

⚠️ **USB 权限**：USB NTFS 根目录是 `root-owned 777`，用 `sudo` 写。

⚠️ **remount 陷阱**：用 `mount -t ntfs-3g /dev/sdb1 /mnt/usb` 重新挂载会覆盖现有挂载关系，导致看到不同的设备内容。**不要 remount**，除非确认设备 UUID。

## 启动脚本模式（bin/ 封装法）

每个 `bin/` 里的 wrapper 脚本都通过 `$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)` 自动找 USB 根目录，无需硬编码路径：

```bash
# USB/bin/hermes — Hermes 入口
#!/bin/bash
USB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export HERMES_HOME="$USB_DIR/hermes-home"
export PATH="$USB_DIR/hermes-venv/bin:$PATH"
exec "$USB_DIR/hermes-venv/bin/hermes" "$@"

# USB/bin/hermes-gateway — Gateway 看门狗
#!/bin/bash
USB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export HERMES_HOME="$USB_DIR/hermes-home"
export PATH="$USB_DIR/hermes-venv/bin:$PATH"
LOG="$HERMES_HOME/logs/gateway-watchdog.log"
mkdir -p "$(dirname "$LOG")"
while true; do
  echo "[$(date)] Starting hermes gateway..." >> "$LOG"
  "$USB_DIR/hermes-venv/bin/python3" -m hermes_cli.main gateway run >> "$LOG" 2>&1
  echo "[$(date)] Gateway exited (code $EXIT), restarting in 5s..." >> "$LOG"
  sleep 5
done

# USB/bin/openclaw — OpenClaw 入口
#!/bin/bash
USB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export HERMES_HOME="$USB_DIR/hermes-home"
exec node "$USB_DIR/openclaw/openclaw.mjs" "$@"
```

**关键**：hermes-gateway 用看门狗循环而非 systemd Restart，因为 Bot 正常断线(exit=0)不会触发 systemd 的 Restart 策略。

### lsblk 安全弹出验证

弹出 U 盘前用 lsblk 验证真实设备状态：

```bash
# 已弹出（安全拔除）
lsblk /dev/sdb
# 输出: NAME MAJ:MIN RM SIZE RO TYPE MOUNTPOINTS
#       sdb    8:16   1   0B  0 disk      ← SIZE=0B 说明设备已不在

# 仍在用（勿拔）
# 输出: sdb    8:16   1 116G  0 disk
#       └─sdb1 ...   1 116G  0 part /mnt/usb
```

### U盘安全弹出流程（Linux）

```bash
USB_DEV="/dev/sdb1"
USB_MNT="/mnt/usb"

# 1. sync + unmount
sync
sudo umount "$USB_MNT"

# 2. 用 udisksctl 断电（触发安全移除）
sudo udisksctl power-off -b "$USB_DEV"

# 3. 验证已弹出（等待几秒）
sleep 3
lsblk "$USB_DEV"
# 若 SIZE=0B → 可安全拔除
```

⚠️ **残留挂载点陷阱**：U盘拔出后，`/mnt/usb` 目录不会自动消失，会变成普通本地目录显示旧缓存内容（设备号变成 sda2 等系统盘 ID）。不要把残留目录误认为 U 盘内容。

## 验证命令

```bash
# 版本检查
/mnt/usb/hermes-venv/bin/python3 -m hermes_cli.main --version
# 应显示: Hermes Agent v0.15.2 (2026.5.29.2)

# hermes-cli 导入
/mnt/usb/hermes-venv/bin/python3 -c "import hermes_cli; print(hermes_cli.__version__)"

# OpenClaw 版本
node /mnt/usb/openclaw/openclaw.mjs --version
# 应显示: OpenClaw 2026.5.27

# bin/ 脚本完整性
ls /mnt/usb/bin/
# 应显示: hermes hermes-bin hermes-gateway openclaw

# hermes-home 内容完整性
ls /mnt/usb/hermes-home/
# 应显示: skills/ sessions/ cron/ config.yaml 等

# 状态
/mnt/usb/start.sh status

# Skills 数量
find /mnt/usb/hermes-home/skills -name "SKILL.md" | wc -l
# 应显示: ~1065
```

## OpenClaw 独立看门狗（systemd 版）

OpenClaw 需要自己的看门狗，与 Hermes Gateway 分离。原因：Bot 正常断线（exit=0）不会触发 systemd Restart 策略，且两者生命周期独立。

### Watchdog script (with environment variables)

```bash
# ~/.hermes/openclaw-watchdog.sh
#!/bin/bash
LOG="/home/saber/.hermes/openclaw-watchdog.log"
OPENCLAW_PID=""

set -a
source /home/saber/.hermes/.env  # loads MINIMAX_API_KEY etc.
set +a

export OPENCLAW_SKIP_STARTUP_MODEL_PREWARM=1  # mandatory: prevents runtime.channel crash

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG"; }

cleanup() {
    [ -n "$OPENCLAW_PID" ] && kill -0 "$OPENCLAW_PID" 2>/dev/null && kill "$OPENCLAW_PID"
    log "Watchdog stopping"
    exit 0
}
trap cleanup SIGTERM SIGINT EXIT

log "OpenClaw Watchdog starting"

while true; do
    cd /home/saber
    /usr/bin/node /home/saber/.npm-global/lib/node_modules/openclaw/dist/index.js \
        gateway --port 18888 --allow-unconfigured >> "$LOG" 2>&1 &
    OPENCLAW_PID=$!
    log "OpenClaw started, PID=$OPENCLAW_PID"
    wait $OPENCLAW_PID
    log "OpenClaw exited (code=$?), restarting in 5s..."
    sleep 5
done
```

> **Always include `OPENCLAW_SKIP_STARTUP_MODEL_PREWARM=1`** — this is the fix for `Cannot read properties of undefined (reading 'run')` crashes.

### systemd service 文件

```ini
# ~/.config/systemd/user/openclaw.service
[Unit]
Description=OpenClaw QQ Bot Watchdog
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/bin/bash /home/saber/.hermes/openclaw-watchdog.sh
Restart=no
TimeoutStopSec=10
Environment=HOME=/home/saber

[Install]
WantedBy=default.target
```

### Deployment (bash background, NOT systemd)

```bash
chmod +x /home/saber/.hermes/openclaw-watchdog.sh
# Run as background process directly — systemd is NOT used for OpenClaw
# (Hermes Gateway uses systemd; OpenClaw uses bash watchdog)
bash /home/saber/.hermes/openclaw-watchdog.sh > /tmp/oc-wd.log 2>&1 &
echo "Watchdog PID: $!"
```

### 验证

```bash
ss -tlnp | grep 18888        # 应显示 node-MainThread 监听
ps aux | grep openclaw # 应有两个进程: bash watchdog + node
journalctl --user -u openclaw.service -n 10 # 应显示 started
```

> 详细技术参数和端口分配见 `references/openclaw-watchdog-setup.md`。

⚠️ **端口分配**：

```bash
ps aux | grep -E "hermes|openclaw" | grep -v grep
ss -tlnp | grep -E "18799|18888|8642"
```

⚠️ **端口分配**：Hermes Gateway 用 8642，OpenClaw 用 18888。两者独立，不要混淆。

## start.sh 用法

```bash
/mnt/usb/start.sh hermes    # 对话
/mnt/usb/start.sh gateway   # 启动 Gateway（后台）
/nt/usb/start.sh status     # 状态
/mnt/usb/start.sh stop      # 停止
/mnt/usb/start.sh update    # 更新 hermes-agent
```

## 部署清单

| 组件 | 版本 | 来源 | 升级方式 |
|------|------|------|----------|
| hermes-agent 源码 | v2026.8.27 (v0.20.6) | git origin/main | Linux: `git fetch origin --tags && git checkout -f v2026.8.27` + `uv pip sync` |
| openclaw core | 2026.6.10 | npm | Linux: `npm install --prefer-offline`（见下方 npm 升级流程） |
| openclaw-qqbot | 1.7.2 | npm | Linux: `npm install @tencent-connect/openclaw-qqbot@latest` |
| @openclaw/fs-safe | 0.4.0 (npm最新) | npm | `npm install --prefer-offline` 会自动拉最新 |
| claude-code npm | 2.1.195 | npm | Linux: `cd $USB/node && npm install @anthropic-ai/claude-code@latest --prefer-offline` |
| opencode-ai npm | 1.17.11 | npm | Linux: `cd $USB/opencode-portable/opencode && npm install opencode-ai@latest --prefer-offline`（仅 npm 包标签，实际 exe 需 Windows 更新） |
| hermes-agent pip | 0.15.2 | PyPI | 通常已是最新，无需操作 |
| Node.js 便携版 | v26.4.0 (PE32+) | Windows 下载 | Linux 可下载 win-x64 zip 预放到 tmp/，Windows 解压替换 Hermes/node/ |
| Python 便携版 | 3.13+ (PE32+) | Windows 下载 | ⚠️ 必须在 Windows 上升级 |
| codex.exe | rust-v0.142.3 (PE32+) | GitHub 下载 | ⚠️ GitHub CDN TLS 限制，无法在 Linux 下载，需 Windows 上手动更新 |

### OpenClaw npm 升级流程（Linux 版，2026-06-28 实测）

pnpm 在 NTFS 上会报错 `ERR_PNPM_VIRTUAL_STORE_DIR_MAX_LENGTH_DIFF`，且 `pnpm install` 会清空 `node_modules/` 后卡住。用 npm 替代：

```bash
cd /mnt/usb/openclaw

# 1. 移除 stale patch 残留（导致 pnpm install 失败但 npm 警告）
rm -rf /mnt/usb/openclaw/patches/

# 2. 如 package.json 有 patchedDependencies 但包已不存在，也会报错
python3 -c "
import json
with open('package.json') as f:
    d = json.load(f)
if 'patchedDependencies' in d:
    del d['patchedDependencies']
    with open('package.json','w') as f:
        json.dump(d, f, indent=2)
    print('Removed stale patchedDependencies')
"

# 3. npm install（会重建整个 node_modules/，约 7 分钟）
npm install --prefer-offline

# 4. 验证
node -e "console.log(require('./node_modules/openclaw/package.json').version)"
node -e "console.log(require('./node_modules/@tencent-connect/openclaw-qqbot/package.json').version)"
```

⚠️ npm install 耗时约 7 分钟（1197 packages），远超 pnpm。耐心等待。

### Node.js 便携版升级（Linux 下载 + Windows 使用）

Linux 无法执行 PE32+ 文件，但可以下载 zip 并预放到 U 盘：

```bash
USB=/mnt/usb
USB_NODE=$USB/Hermes/node

# 1. Linux 下载 win-x64 zip
curl -L --progress-bar "https://nodejs.org/dist/v26.4.0/node-v26.4.0-win-x64.zip" \
  -o $USB/tmp/node-v26.4.0-win-x64.zip

# 2. 备份旧版
cp -r $USB_NODE $USB/node.old_backup

# 3. 解压 zip（会生成 node-v26.4.0-win-x64/node-v26.4.0-win-x64/ 子目录）
cd $USB/tmp && unzip -q node-v26.4.0-win-x64.zip

# 4. 替换（删除旧目录，移入新版）
mv $USB_NODE $USB/node.old
mv $USB/tmp/node-v26.4.0-win-x64/node-v26.4.0-win-x64 $USB_NODE

# 5. 清理（确认正常后可删备份节省 85MB）
rm -f $USB/tmp/node-v26.4.0-win-x64.zip
rm -rf $USB/node.old

# 验证文件大小：v26 ~99MB，v22 ~70MB
ls -lh $USB_NODE/node.exe
```

⚠️ `Hermes/node/` 和 `node/` 是两个独立目录，内容相同。升级时操作 `Hermes/node/`（hermes.bat 实际引用位置）。

### OpenClaw systemd service — `--allow-unconfigured` is mandatory

OpenClaw's `gateway run` in non-interactive environments (systemd, screen, cron) crashes with "Missing config" even when the config file is present.

**Fix**: add `--allow-unconfigured` to all startup commands:
```bash
# systemd service ExecStart (correct)
ExecStart=/usr/bin/node /home/saber/.npm-global/lib/node_modules/openclaw/dist/index.js gateway --port 18888 --allow-unconfigured

# bin/openclaw wrapper (correct)
exec node "$USB_DIR/openclaw/openclaw.mjs" gateway run --port 18888 --allow-unconfigured

# direct command line (correct)
openclaw gateway run --force --allow-unconfigured
```

**`OPENCLAW_SKIP_STARTUP_MODEL_PREWARM=1` is also mandatory** — without it, the 5-second warmup timeout leaves `runtime.channel` uninitialized, causing every incoming QQ message to crash with `Cannot read properties of undefined (reading 'run')`. Always export this in the watchdog script (see below).

⚠️ 漏掉此参数 → systemd failed 循环，journal 显示 "Missing config"。
⚠️ 插件版本不兼容时会静默跳过，不阻塞启动。

**验证启动成功**：
```bash
systemctl --user status openclaw-gateway.service
ss -tlnp | grep 18799
journalctl --user -u openclaw-gateway.service -n 20 | tail -15
# 关键行："[gateway] ready" + "[qqbot] ✅ Access token obtained successfully"
```

## 已知空间使用

~3.5GB / 116GB (hermes-venv 153MB + hermes-home 2.4GB + openclaw 863MB)

---

# Windows 端即插即用配置

## 限制说明

Linux 二进制（hermes-venv 里的 Python、openclaw 里的 node）不能直接在 Windows 运行。正确的跨平台方案是：
- **Portable Python/Node 写入 U 盘**（Windows 原生可执行文件）
- **hermes-agent 通过 pip 安装**（在 Portable Python 中）
- **hermes-home 指向 U 盘**（通过环境变量）

## USB Windows 目录结构

```
USB 根目录/
├── hermes-home/                  # 配置/记忆/sessions（2.4GB）
├── hermes-venv/                  # Linux Python环境（153M，仅 Linux 用）
├── openclaw/                     # OpenClaw npm 包（跨平台）
├── hermes-agent.whl              # Hermes 源码备份
├── portable/                     # Windows 即插即用环境
│   ├── python/                  # Python 3.13 embeddable + pip
│   │   ├── python.exe
│   │   ├── python313._pth       ← 必须启用 import site
│   │   ├── Scripts/             # pip.exe 等
│   │   └── Lib/site-packages/
│   └── node/                     # Node.js 22.16.0
│       ├── node.exe
│       ├── npm/
│       └── node_modules/
├── start-hermes-usb.bat          # Windows 主入口（双击运行）
└── start.sh                      # Linux 主入口
```

## Portable Python 初始化步骤（已在 U 盘完成）

```powershell
# 1. 下载 embeddable zip
Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.13.0/python-3.13.0-embed-amd64.zip' -OutFile 'python-embed.zip'
Expand-Archive -Path 'python-embed.zip' -DestinationPath 'portable/python' -Force

# 2. 必须修改 python313._pth 启用 site 模块（否则 pip 报错）
# 替换文件内容为：
#   python313.zip
#   .
#   import site

# 3. 安装 pip
python.exe get-pip.py

# 4. 安装 hermes-agent
python.exe -m pip install hermes-agent --upgrade
```

## start-hermes-usb.bat 自动下载逻辑
## start-hermes-usb.bat 自动下载逻辑

`start-hermes-usb.bat` 已写入 U 盘，实现了**首次自动下载 + 菜单式交互**。

### 核心逻辑

```batch
:: hermes 命令在 Windows Portable Python 上的正确调用
"%PYTHON%" -m hermes.cli.main chat              :: Hermes Chat
"%PYTHON%" -m hermes_cli.main gateway run       :: Gateway（含看门狗）

:: hermes.exe 实际位置是 Scripts/ 而非 bin/
:: 因此 chat 入口用 python -m hermes.cli.main，不要依赖 hermes 命令行
if not exist "%PORTABLE_PY%\Scripts\hermes.exe" (
    echo [错误] hermes 未安装，请先运行 [1] 安装
)
```

### Windows Gateway 看门狗（bat :gwloop 标签）

```batch
:GWLOOP
"%PYTHON%" -m hermes_cli.main gateway run >> "%GATEWAY_LOG%" 2>&1
set "EXIT_CODE=%ERRORLEVEL%"
echo [%date% %time%] Gateway exited ^(code %EXIT_CODE%^), restarting in 5s... >> "%GATEWAY_LOG%"
timeout /t 5 /nobreak >nul
goto GWLOOP
```

### 关键陷阱

- **hermes 不是命令**：hermes-agent pip 包安装后，`hermes` 命令在 Linux 的 `bin/hermes`，但 Windows Portable Python 里 pip 装到 `Scripts/hermes.exe`。bat 中用 `python -m hermes_cli.main` 或 `python -m hermes.cli.main` 来调用。
- **`where hermes` 会失败**：bat 脚本检测 hermes 时用 `python -m hermes --version >nul 2>&1`，不用 `where hermes`。
- **Node 子目录提亮**：下载后 `node-v22.16.0-win-x64/*` 必须 `move` 到 `portable/node/` 根目录，否则 `node.exe` 找不到。
- **python313._pth 必须有 `import site`**：否则 pip 报错 "not a supported wheel on this platform"。

### 菜单选项

```
[1] 安装 hermes-agent（首次必选，~150MB）
[2] Hermes Chat (python -m hermes.cli.main chat)
[3] Hermes Gateway（后台 + 看门狗）
[4] 启动 OpenClaw
[5] 查看状态
[6] 停止所有服务
```

### 首次运行时间线

1. 双击 `start-hermes-usb.bat`
2. 自动下载 Python embeddable (~12MB) + get-pip.py + 安装 pip
3. 自动下载 Node.js (~35MB) + 提亮子目录
4. 运行 [1] 安装 hermes-agent (~150MB pip 包)
5. 之后完全离线，插上即用

### 验证（Windows PowerShell）

```powershell
# 检查 Python/Node
cd D:\  # U盘盘符
.\portable\python\python.exe --version
.\portable\node\node.exe --version

# 检查 hermes-agent
.\portable\python\python.exe -m hermes --version

# 状态（通过 bat 菜单 [5]）
```

## 关键技巧

### python313._pth 必须启用 site
embeddable zip 默认 `import site` 被注释，导致 `pip install` 报错 "not a supported wheel on this platform"。必须取消注释这行：
```
python313.zip
.
import site
```

### Portable Node.js 解压后有子目录
`node-v22.16.0-win-x64.zip` 解压后得到 `node-v22.16.0-win-x64/` 子目录，内容才是真正的 node.exe/npm.cmd。需要用 `move` 把文件移到 `portable/node/` 根目录。

### 首次下载量
- Python embeddable: ~12MB
- Node.js win-x64: ~35MB
- hermes-agent (pip): ~50MB
- 合计首次需要网络约 100MB，之后完全离线可用

## hermes-home 跨平台注意事项

hermes-home 包含 sessions/ 目录（~701MB）和 skills/ 目录（~179MB），可以在 Linux 和 Windows 之间共享，但：
- Windows 的 node_modules 路径格式与 Linux 不同（如需 OpenClaw 插件）
- Gateway 日志路径 Windows 用 `\` 分隔，脚本已兼容处理

## 同步 weixin.py 到 Windows

如果 weixin.py 有本地修改，在 Windows 上也需要同步：
```powershell
# 在有 hermes-agent 的 Windows 机器上找到 site-packages
python.exe -c "import site; print(site.getsitepackages()[0])"
# 复制修改后的 weixin.py 到该路径的 gateway/platforms/
```