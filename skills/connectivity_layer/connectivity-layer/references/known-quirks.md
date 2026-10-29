# APM 飞控 & MCP 使用场景 实测坑位速查

大部分内容来自多次会话验证与实测；快速按关键字 `grep` 定位问题即可。随时追加、PR 进本文件即可成为幕后高频手册。


---

## 🔧 APM 飞控（MAVLink）常见崩溃点


### 1) `stdbuf -oL` or `--no-buffer` 在 mcp / MAVLink 日志失效（Linux 断行）
- 现象：cmd 一直静默不输出，像 hang 住
- 起因：Git 仓库的 `substdbuf -oL` 在某些 Python 打包版本下不行，或 mcp CLI 日志在 stdout 启用行缓冲
- 解决：
  ```bash
  # export 给所有子进程
  export PYTHONUNBUFFERED=1
  # 或剥离日志层
  stdbuf -oL mcp ...
  ```
  在 `scripts/call_minimax.py` 与 `scripts/inspect_apm.py` 的 handler 入口处加上：
  ```python
  import os
  if 'PYTHONUNBUFFERED' not in os.environ:
 os.environ['PYTHONUNBUFFERED'] = '1'
  ```

### 2) miniMax torrent/quota 达到 60 RPM 后自动冷却
- 表现：Python client 直接返回 429 或 "Rate throttled"
- 解决：
  - 脚本自动 `time.sleep(0.99)` 加缓冲；或
  - 串行模式，改并行 `asyncio.gather` 但需控制并发度 < 5

### 3) APM 2.8 CH5-CH8 固定 521 偏移（实测 2026-06-29）
- 现象：地面站遥测显示 PWM 为 1000/1500/2000，APM 口实际输出为 1521/2021/1521
- 原因：ArduPlane **读写通道值** 时，为了避免早期 Demo Servos 的冲突，在固件写死了偏移。
- Fix:
  - 方案 A：在 APM 地面站里把通道 Calibration 改掉（Advanced → Servo Calibration）
  - 方案 B：软件侧减掉 -521：
  ```python
  def undo_offset(v): return max(500, v - 521)
  ```

### 4) pymavlink 3.x `flushInput()` 报错
- 起因：pyserial 3.x 弃用 `flushInput()` → 改 `reset_input_buffer()`
- 影响：`apm-flight-controller` 内置工具挂死
- 解：
  ```diff
  - s.flushInput()
  + s.reset_input_buffer()
  ```
  在 `scripts/inspect_apm.py` 的 `poll()` 处替换。



---

## 🔧 MCP / MiniMax 客户端相关\[src: minimax-platform-api\]


### 1) MCP 服务端 stdout 缓冲导致长时间无任何输出（Stdio block）
- 现象：mcp list_resources 时终端直接卡死，无预览
- 原因：mcp CLI 自身在处理 log 的时候用了行缓冲，导致 stdout 不行扫描新行
- 处理：
  ```bash
  stdbuf -oL mcp list-resources      # 显式禁用行缓冲
  # 或改您的启动脚本为 require_once 'stdbuf -oL $cmd' 之类
  ```

### 2) MiniMax `abab6-chat` 的空白 Token 问题（2026-07-08）
- 现象：发 `请输出一首五言绝句` 返回空白（非降级，server返回空 response）
- 起因：server 端用了默认空白 Emptiness guard，`Content-Type: application/json` 的 `"stream":false` 返回就略过了 tokenizer 而直接输出
- 解：用 `stream=true`，即 `scripts/call_minimax.py --stream`。服务器端选择：
  ```bash
  curl -X POST "https://api.minimax.chat/v1/text/chatcompletion" \
    -H "Authorization: Bearer $KEY" \
    -H "Content-Type: application/json" \
    -d '{"model":"abab6-chat","messages":[{"role":"user","content":"hi"}],"stream":true}'
  ```

### 3) 新 key 需配置 ENV，但脚本内 PATH 会找同名文件污染
- 起因：程序读取 ~/.bashrc 外的同名 config 文件（不该读，导致 key 消失）
- 解决：
  - $MINIMAX_API_KEY 绝对优先级：自举阶段即明确 `os.getenv('MINIMAX_API_KEY')`，不行再读 `.env`，不行再 `raise`。确保 `~/.config/minimax/.env` 不被误读。


---

## 🧪 USB 权限与驱动问题

### 1) /dev/ttyACM0 Permission denied（Arch Linux）
- 现象：`apm_status` 提示 Permission denied，用 root `sudo` 临时可行
- 解决：群组 `uucp`（Arch）与 `dialout`（Debian）：
  ```bash
  sudo usermod -aG uucp $USER && newgrp uucp
  ```
- 确认：
  ```bash
  groups
  ls -l /dev/ttyACM0
  ```

### 2) APM 2 克隆板 CH340 在 Linux 的驱动问题（2025-11）
- 现象：设备写入 `/dev/ttyACM0` 不出现，`dmesg` 显示 `ch34x` 未加载
- 解决：
  ```bash
  sudo pacman -S linux-headers
  yay -S ch34x-dkms  # AUR；或内核自带 6.1+
  sudo modprobe ch34x  # 动态加载
  ls /dev/ttyACM*
  udev rule 固化（按需）:
  cat <<EOF | sudo tee /etc/udev/rules.d/99-ch34x.rules
  ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", GROUP="uucp", MODE="0660"
  EOF
  sudo udevadm control --reload
  ```

---

## 🚀 脚本级已知坑点

### inspect_apm.py 的 pyserial 3.x 兼容性
- 报错：`AttributeError: 'Serial' object has no attribute 'flushInput'`
- 原因：Python 3.x pyserial 弃用了 `flushInput()`，mavlink 库调用了它
- 修复：
  ```diff
  - s.flushInput()
  + s.reset_input_buffer()
  ```
  在脚本底层用 `with serial.Serial(..., timeout=2)`，保证 buffer 清理。


### tools/registry.py 的 schema 坑
- 原因：旧文档示例把参数写成直接 `parameters={...}`，实测需 `schema={"parameters": {...}}` ，且必须加 `toolset="hardware"` 才会 work。
  ```python
  registry.register(
   name="apm_servo",
   toolset="hardware",  # ← 关键
   description="控制单个 APM 舵机通道",
   schema={
     "name": "apm_servo",
     "description": "...详细...",
     "parameters": {
       "type": "object",
       "properties": {"channel":{"type":"integer",...},
     }
   },
   handler=_apm_servo,
  )
  ```
- 影响：旧 `apm-flight-controller` 工具挂死或没注册。新集成 umbrella 已更新。


---

## 🧩 通用工具集约定

### `stdbuf -oL` 环境变量一致性
- 建议在启动器 shell（`~/.bashrc`/`~/.zshrc`）统一加：
  ```bash
  export PYTHONUNBUFFERED=1
  export LC_ALL=en_US.UTF-8      # 避免中文 log 顺序错乱
  ```
- 所有裸脚本：
  ```python
  import os, locale
  if 'PYTHONUNBUFFERED' not in os.environ:
 os.environ['PYTHONUNBUFFERED'] = '1'
  locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
  ```

---

## 🔧 ESP32 / ESP-IDF 开发坑点

### 1) Gitee 镜像克隆 ESP-IDF 后 submodule URL 全部失效
- **现象**：`fatal: could not read Username for 'https://gitee.com': 没有那个设备或地址`（或"未注册"），`git submodule update --init --recursive` 全部失败
- **根因**：Gitee 镜像保留了原始 ESP-IDF 仓库的 `.gitmodules`，其中 submodule URL 是**相对路径**（`../../espressif/esp32-bt-lib.git`）。克隆后这些相对路径无法解析
- **修**：用 Python 重写为绝对 GitHub URL（shell sed 无法正确处理 `../../` 路径）：

```python
import subprocess, os
os.chdir('/path/to/esp-idf')
result = subprocess.run(
    ['git', 'config', '--file=.gitmodules', '--get-regexp', r'submodule\..*\.url'],
    capture_output=True, text=True
)
for line in result.stdout.strip().split('\n'):
    if not line.strip(): continue
    parts = line.split(None, 1)
    if len(parts) != 2: continue
    key, url = parts
    if url.startswith('../../'):
        new_url = 'https://github.com/' + url.lstrip('../../')
        subprocess.run(['git', 'config', '--file=.gitmodules', key, new_url])
        subprocess.run(['git', 'config', key, new_url])
        print(f'  {key} -> {new_url}')
```

- **收尾**：修复后需 `git submodule deinit --force --all` 清理旧状态，再 `git submodule update --init --recursive`

### 2) ESP-IDF 子模块下载耗时长
- **现象**：23 个 submodule，多为预编译二进制库（bt-lib、wifi-lib 等），GitHub 直连速度约 5-10MB/分钟，总量约 1.5-2GB
- **监控**：`watch -n 30 'du -sh /path/to/esp-idf && find /path/to/esp-idf/components -maxdepth 2 -name "*.a" | wc -l'`

---

## 📝 如何为本页做补充
本文件为 **会话级细节沉淀**，PR 直接编辑 `references/known-quirks.md`。每条记录请保持三段式：
1) 现象（可复现错误字符串）
2) 根因（简短一行）
3) 解方法（代码或 shell 一行）

模板：
```markdown
### <Subject> [(src)](<src-skill>)
- **现象**：`output <error or blank>`
- **起因**：MCP CLI stdout 行缓冲 + Python 信任锁
- **修**：`stdbuf -oL mcp ...`
```
---

## 🔗 外部索引链接
| 子主题 | 在 umbrella 内页 |
|--------|-----------------|
| 端口速查 | [../speed-api/apm-ports.md](references/speed-api/apm-ports.md) |
| 飞控消息解析 | [../speed-api/apm-flight.md](references/speed-api/apm-flight.md) |
| Scad STL 生成 | [../apm-stl-generation.md](apm-stl-generation.md)（待补） |
