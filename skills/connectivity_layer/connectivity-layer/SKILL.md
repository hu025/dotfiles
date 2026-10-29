---
name: connectivity-layer
title: connectivity-layer
description: |
  中心化的「联外」技能 umbrella，囊括与外部系统/设备/模型 API 的交互场景：
  - APM/ArduPilot 飞控总线（MAVLink）
  - MCP 客户端与 MiniMax 平台 API
  - 硬件状态抽取、传感器监控与硬件级故障恢复

triggers:
  - '"MAVLink"'
  - '"APM 2"'
  - '"ardupilot"'
  - '"mavlink"'
  - '"model-context-protocol"'
  - '"MCP native"'
  - '"MiniMax Platform API"'
  - '"connect hardware"'
  - '"check sensor"'
  - '"reset servos"'
  - '"re-arm flight controller"'
  - '"模型连接"'
  - '"ESP32"'
  - '"ESP-IDF"'
  - '"esptool"'
  - '"ESP32-S3"'
  - '"固件烧录"'
categories:
  - connectivity_layer
author:
  - Hermes Curator
created: "2025-07-15"
---

# connectivity-layer —— 统一「联外系统」的技能库

连接本身应当被抽象、可复用与安全管理；本 umbrella 为以下场景提供 **class-level 指令、速查、一键脚本**：
- APM 飞控总线连接与 MAVLink 诊断
- MCP 原生客户端（MiniMax 等各式 MCP 服务）
- 小型外部 API 封装（MiniMax 平台）

--------

## 核心能力分区（抬头即可 copy-paste）
- [MAVLink/APM 飞控连接](#mavlinkapm-飞控连接)
- [MCP 客户端 + MiniMax API](#mcp-客户端--minimax-api)
- [硬件状态监控与安全重置](#硬件状态监控与安全重置)
- [原子脚本与模板](#原子脚本与模板)
- [速查 API 卡片](#速查-api-卡片)
- [故障场景与现成解决方案](#故障场景与现成解决方案)

--------

## 快速上手

### MAVLink / APM 飞控
1) 首次使用请先确认端口与权限：
   ```bash
   ls /dev/ttyACM* /dev/ttyUSB*     # 常见端口
   sudo usermod -aG dialout $USER     # 解决权限问题
   newgrp dialout
   ```
2) 状态检查：
   ```bash
   apm_status      # 飞控完整状态
   apm_sensors     # 传感器实时 dump
   ```
3) 紧急安全归中：
   ```bash
   apm_disarm                            # 落锁 + 舵机中位
   apm_set_all "[1500,1500,1500,1500,1500,1500,1500,1500]"  # 强制归中
   ```

**脚本加持** — 无需再写一次性代码：
   ```bash
   python scripts/inspect_apm.py /dev/ttyACM0  # 一键监控脚本
   ```

### MCP 客户端 + MiniMax API
   1) 准备配置文件：
   ```bash
   cp templates/minimax.env ~/.config/minimax/.env
   # 填入 MINIMAX_API_KEY
   ```
   2) 一键对话：
   ```bash
   python scripts/call_minimax.py --model abab6-chat --prompt "你好，世界"
   ```
   3) MCP 资源列表（若要挂载 MiniMax 以外的 MCP 服务）：
   ```bash
   mcp list_resources --verbose
   mcp call "{uri}"                   # 调用任意服务
   ```

--------

## MAVLink/APM 飞控连接

| 需求 | 指令 | 脚本/模板 | 注意事项 |
|---|---|---|---|
| 完整状态读取 | `apm_status` | 指令内置 | — |
| 传感器实时采样 | `apm_sensors` | 指令内置 | 包含：6 轴 IMU、GPS、气压、电池 |
| 单通道舵机测试 | `apm_servo --channel 5 --pwm 1600` | 指令内置 | 地面静止方可使用 |
| 全舵机安全复位 | `apm_set_all "[1500]*8"` | 指令内置 | 紧急时用 |
| 落锁并中位输出 | `apm_disarm` | 指令内置 | 解除任意锁定 |
| 批量通道扫描 | `apm_test` | 指令内置 | 验证端口与舵机连线 |

**快速故障排除**
- 提示 `permission denied` → 加入 dialout 组并重新登录 shell；或 `sudo` 临时执行。
- 串口未出现 → 检查是否是 `/dev/ttyACM1`；刷机后可能需要 `sudo udevadm control --reload`。
- mavlink 无任何回应 → 目标设备需上电且波特率匹配（默认 57600）。

**速查**
- [端口与波特率速查](references/speed-api/apm-ports.md)
- [飞控操作速查](references/speed-api/apm-flight.md)

--------

## MCP 客户端 + MiniMax API

使用场景：通过统一的 mcp CLI（`@modelcontextprotocol/cli`）连接 MiniMax 与其它 MCP 服务，无需再写 SDK 层叠加。


| 任务 | 使用方式 | 必需环境变量 | 速查 |
|---|---|---|---|
| 查看所有资源 | `mcp list_resources --verbose` | — | [mcp-cli.md](references/speed-api/mcp-cli.md) |
| 直接调用资源 | `mcp call "{uri}"` | `MCP_API_KEY` | 同上 |
| 调用 MiniMax 模型 | `python scripts/call_minimax.py --model abab6-chat --prompt "hi"` | `MINIMAX_API_KEY` | [minimax.md](references/speed-api/minimax.md) |
| 长流式对话（REPL） | `python scripts/call_minimax.py --stream` | 同上 | 脚本内置 back-pressure |

--------

## 硬件状态监控与安全重置

### 实时监控遥测
指令：
```bash
apm_sensors
```
输出字段：
- 电池：Voltage、Current、mAh 消耗量
- IMU：3 轴加速度、3 轴角速度
- GPS：定位状态、卫星数、海拔
- 气压：气压值、温度
- 飞控：运行模式、固件版本、电池 SOH（25 mV 精度）

### 安全重置与保险动作
- **apm_disarm** – 落锁（启用安全锁定）并强制将所有舵机输出归零中位，舵机自动进入中立。
- **apm_set_all [1500]*8** – 所有通道强制 1500 μs（中位），批量将多轴归位至安全位置。适用于 `apm_disarm` 后的确认动作。

**强烈提醒**：舵机操作 **必须保证飞控静止于地面、螺旋桨静止、处于安全环境**；否则可能误伤人员或损坏设备。

--------

## 原子脚本与模板

| 文件 | 用途 | 一句话运行 |
|---|---|---|
| [templates/apm_preflight_check.sh](templates/apm_preflight_check.sh) | 飞控 10 项预检查 | `chmod +x templates/apm_preflight_check.sh && ./templates/apm_preflight_check.sh /dev/ttyACM0` |
| [scripts/inspect_apm.py](scripts/inspect_apm.py) | 一键遥测监控与日志存储 | `python scripts/inspect_apm.py /dev/ttyACM0 --log apm.log` |
| [scripts/call_minimax.py](scripts/call_minimax.py) | MiniMax 一键对话/流式 | `python scripts/call_minimax.py --model abab6 --prompt "help"` |
| [templates/minimax.env](templates/minimax.env) | 示例 .env 文件 | 复制到 ~/.config/minimax/.env 并填 key |

--------

## 速查 API 卡片（可直接 cat/less）
速查卡片可直接命令行浏览，无需打开浏览器：

- [apm-ports.md](references/speed-api/apm-ports.md) —— 常见 APM/ArduPilot 端口与波特率
- [apm-flight.md](references/speed-api/apm-flight.md) —— MAVLink 协议梳理与常用指令
- [minimax.md](references/speed-api/minimax.md) —— MiniMax 平台 API 指南（模型、token、错误码）
- [mcp-cli.md](references/speed-api/mcp-cli.md) —— 自制 mcp 客户端与 MiniMax 对接小技巧

--------

## 故障场景与现成解决方案

| 场景 | 典型报错 | 快速解 |
|---|---|---|
| 端口权限 | `Permission denied (open /dev/ttyACM0)` | `sudo usermod -aG dialout $USER && newgrp dialout` 再试一次 |
| 设备无 mavlink 响应 | mcp 连接挂起 | 检查是否已上电；target 波特率是否为 57600（默认） |
| mcp 服务端 stdout 缓冲 | cli 卡住无输出 | 启动时加前缀：`stdbuf -oL mcp ...` 或使用 `--no-buffer` |
| MiniMax 触顶 60 RPM | 返回 429 throttle | 脚本内置等待与重试（见 [scripts/call_minimax.py](scripts/call_minimax.py)） |

收录更多坑位 → [references/known-quirks.md](references/known-quirks.md)

--------

## 配置与安装需要的最简依赖
- Python 3.11+
- pymavlink (`pip install pymavlink`) – MAVLink 栈
- @modelcontextprotocol/cli (`npm i -g @modelcontextprotocol/cli`) – mcp 标准客户端
- MiniMax API key + 必要的 MiniMax SDK 或手动拼 HTTP（scripts 内部自动适配）

---

## 小贴士
- 喜欢 alias？将常用指令做成你的 shell alias、DNA 或 Platypus profile，一键呼出即可。
- 希望将本集合沉淀成下一次会话必备技能？ `hermes curator pin connectivity-layer` 即可 pin 住，防止未来被误删。
- 若新增场景或遇到未收录的错误，请直接 PR 本 umbrella：补上速查卡片或修复脚本，保证下一次会话不踩坑。