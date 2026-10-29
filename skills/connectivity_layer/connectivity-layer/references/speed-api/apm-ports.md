# APM 常见端口与波特率速查

收录各型 APM/ArduPilot（尤其是 APM 2.8 / ATmega2560、青苗 Pixhawk/飞行控制器）的常见串口与波特率，便于快速排错。

---

## 1) APM 2.8 (ATmega2560 Arduino Mega) 串口

| OS/发行版 | 热插拔设备名 | 权限组 | 排错快速键 |
|-----------|---------------|--------|----------|
| Arch Linux / Manjaro | `/dev/ttyACM0` 或 `/dev/ttyUSB0` | `uucp`（非 dialout） | `sudo usermod -aG uucp $USER` + newgrp uucp |
| Debian / Ubuntu / Mint | `/dev/ttyACM0` | `dialout` | `sudo usermod -aG dialout $USER` + logout |
| macOS | `/dev/cu.usbmodem<ID>` | 无需组 | — |
| Win10/11 | COM<x> | 需安装 CH340/CP210x 驱动 | 设备管理器检查端口号 |

**检测方法：**
```bash
dmesg | grep -E 'cdc_acm|ch34x|cp210x|ttyACM|ttyUSB'  # Linux
# macOS: ls /dev/cu.*
```

**典型信号**
- Teensy/APM: /dev/ttyACM*
- FTDI/CP210x USB 转 TTL: /dev/ttyUSB*
- 克隆 APM（CH340 转 TTL）：Linux: `ch34x` 模块若无则需手动加载（`modprobe ch34x`）


---

## 2）固定波特率约定

| 场景 | APM 内核 | 官方推荐波特率 | GCS/MAVLink 工具同时输出 | 备注 |
|------|---------|---------------|--------------------------|------|
| APM 2/APM-Copter | 固件 | 57600 | MavProxy、MissionPlanner | APM 自带 57.6Kbaud |
| APM 2 (F4/F7) | 旧固件 | 115200 | ArduPilot 3.4/3.5+ | 大多数 GCS 向下兼容 |
| Pixhawk 系列 | 标准 | 57600 | MissionPlanner MAVLink | Pixhawk 可切换 |
| ArduPilot ChibiOS | 标准 | 57600 | MAVLink2 (UART0) | 自动使能 `TELEM1`/`TELEM2` |


**注意：** APM 2.8 原生主 UART 即 USB-CDC，波特率固定为 115200（可在参数表中调整）。
- 若 GCS/地面站连接提示 `MAVLink v2 错误` → 检查飞控固件与 GCS 版本兼容。

---

## 3）通过地面站切换波特率（APM 2.8）


地面站参数表：

| 参数 | 值 | 含义 | 范围 |
|------|-----|------|------|
| `SERIAL0_BAUD` | 115 | `/dev/ttyACM` 主串口波特率（默认 57600） | 1/2/5/11/57/115 (单位 100 的倍数) |
| `SERIAL1_BAUD` | 57 | TELEM1/TELEM2 | 同上 |

**重启生效。** 常用枚举：

- 115 → 115200 baud
- 57 → 57600 baud
- 1 → 1200 baud（极慢）


**绝大多数 APM 2/ArduCop/Copter 默认 57600，切勿在不明状态下盲目升速。**


---

## 4）排错一览表

| 现象 | 可能原因 | 首选解 |
|------|----------|--------|
| `ls /dev/tty*` 无 APM 设备 | USB 线虚接，Windows 未装驱动，Linux udev 规则不识别 CH340 | `lsusb` 确认设备 → 安装驱动（Windows）/ `modprobe ch34x`（Linux） |
| `Permission denied /dev/ttyACM0` | 当前用户不在 `dialout`/`uucp` 组 | `sudo usermod -aG <group> $USER` + `newgrp <group>` |
| `No Heartbeat packets received` | 波特率不匹配 | `SERIAL0_BAUD` 改 57600（APM 默认）后重启 |
| APM 不响应 MAVLink 指令 | 无 RC 接收机或安全开关未解锁 | 连接 RC 遥控器或 bypass GCS 解锁 |

---

## 5）案例：无驱动 Linux 用 APM 2.8


**设备信息（ lsusb 一次定位 ）**
```bash
$ lsusb -d 10c4:ea60
Bus 003 Device 012: ID 10c4:ea60 Silicon Labs CP210x USB to UART Bridge Controller
```
**步骤**
1. 安装驱动 (Linux):
   ```bash
   sudo pacman -S python-pyserial python-pymavlink # 依赖
   # CP210X 驱动内核自带，ls /dev/ttyUSB*
   ```
2. 添加组（大多数嵌入式 USB 设备):
   ```bash
   sudo usermod -aG uucp,dialout $USER && newgrp uucp
   ```
3. 读取遥测：
   ```bash
   python scripts/inspect_apm.py /dev/ttyUSB0
   ```

---

## 6）快速引用片段

| 任务 | 命令 | 场景 |
|------|-------|------|
| 串口列表 | `ls /dev/ttyACM* /dev/ttyUSB*` | 确认设备就绪 |
| 添加组 | `sudo usermod -aG dialout $USER && newgrp dialout` | APM 设备权限 |
| 读遥测 | `python scripts/inspect_apm.py /dev/ttyACM0` | 一键监控 |

**打包做成 shell alias:**
```bash
# ~/.bashrc 或 zshrc
alias apm-dev='ls /dev/ttyACM* /dev/ttyUSB*'
alias apm-perm='sudo usermod -aG uucp,dialout $USER; newgrp uucp'
alias apm-telem='python3 ~/.hermes/skills/connectivity_layer/connectivity-layer/scripts/inspect_apm.py'
```

---

## 7）外接小板与端口冲突

当前 Linux USB 总线已被占用：

```bash
lsusb  | grep -E 'WCH|CP210|FTDI|CH340'
echo 200  | sudo tee /proc/sys/vm/block_dump  # 会垃圾满磁盘，勿开启
```
暂时挂起占用键鼠或 4G 转串口模块即可恢复：
```bash
sudo uhubctl -a off -p 2  # 仅树莓派需装包
```

---

## 8）备忘：波特率与速度单位换算
| 数值 | 波特率 | 场景 |
|------|---------|------|
| 1 | 1200 | 最慢工业 UART（已弃用） |
| 2 | 2400 | 早期 GPS （已弃用） |
| 5 | 57600 | ArduPilot APM 默认 (56 kbps) |
| 11 | 115200 | 高速遥测（默认 115 kbps) |
| 100 | 1.2 M | 转储数据流（少用） |
