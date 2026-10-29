# MAVLink 飞控速查 API

收录 APM 2/ArduPlane v3.4.0 所需的常用速查信息，方便命令行 `less` / `bat` 直接跳转学习。

---

## 1) MAVLink v1.0 控制器（手动构建）

| 函数 | 说明 | 代码片段 |
|------|-------|----------|
| `mpkt(msgid, payload, sysid=255, compid=1)` | 构建标准 MAVLink v1.0 包 | [snippet_mpkt](snippet_reusable/mpkt) |
| `crc_x25(data)` | Calc Crc16 (x25) with lookup table | [snippet_crc](snippet_reusable/crc_x25) |
| `parse(data)` | 遍历 0xFE 包头，返回解析包 | — |
| `poll(s, timeout)` | 持续读串口并在 timeout 内返回解析包 | `py scripts/inspect_apm.py` |

[snippet_mpkt]
```python
import struct

def mpkt(msgid, payload, sysid=255, compid=1):
 h = bytes([0xFE, len(payload), 0, sysid, compid, msgid])
 c = crc_x25(h[1:] + payload)
 return h + payload + bytes([c & 0xFF, c >> 8])
```

[snippet_crc]
```python
def crc_x25(data):
 crc = 0xFFFF
 for b in data:
 crc ^= b
 for _ in range(8):
 crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
 return crc
```

---

## 2) 关键 MAVLink 消息 速查

### HEARTBEAT (msgid=0)
| 字段 | 偏移 | 解析 | 说明 |
|-------|------|------|------|
| custom_mode | 0-3 | `<I` | 飞控模式号（APM 内数字模式） |
| base_mode | 4 | `B` | bit7=ARMED（是否锁定） |
| autopilot | 6 | `B` | 17 = APM（识别是否 APM） |
| system_status | 7 | `B` | 2 = STANDBY（运行态） |

```python
import struct
msgid=0; sysid_auth=1
pkts = parse(data)
hb = next((p for p in pkts if p[0]==msgid and len(p[2])>=8), None)
if hb:
 cm = struct.unpack('<I', hb[2][0:4])[0]
 bm = hb[2][4]
 ap = hb[2][6]
 ss = hb[2][7]
 mode = cm & 0xFF
 armed = bool(bm & 0x80)
```

### SYS_STATUS (msgid=1) – 电源档
| 字段 | 偏移 | 解析 | APM2.8 实测 | 说明 |
|------|------|------|-------------|------|
| voltage (raw_adc) | 8-9 | `<H` | 64523 (示例) | ADC 原始值 → 真实电压 ≈ raw / 5150 |
| current (raw) | 10-11 | `<h` | -3.21 A | 电流 = abs(raw * 0.01) |
| battery_remaining | 12 | `B` | 95% | 电量百分比 |

```python
raw_v = struct.unpack('<H', payload[8:10])[0]
voltage = raw_v / 5150.0   # 实测 64523 → 12.52V ✔️
txt = f"Battery: {voltage:.2f}V / {current:.2f}A / {battery_pct}%"
```

### GPS_RAW_INT (msgid=2)
| 字段 | 偏移 | 解析 | 说明 |
|------|------|-------|------|
| FIX | 0 | `B` | 3=3D Fix |
| latitude | 4-7 | `<i` | ‰7 (/1e7) |
| longitude | 8-11 | `<i` | ‰7 |
| altitude | 12-15 | `<i` | cm → m (/100) |
| satellites_visible | 29 | `B` | 卫星数 |

```python
lat_deg = lat_i / 1e7
lon_deg = lon_i / 1e7
alt_m = alt_i / 100.0
```

### SERVO_OUTPUT_RAW (msgid=36) – APM 2.8 横移了！
| 问题 | 原因 | 解决 |
|------|------|------|
| 第一通道与 Demo 冲突 | 固件激活 Demo Servos 动画 | 避开 CH1，用 CH2-CH8 |
| CH5-CH8 固定偏移 +521 | 固件实现 | 通过地面站重新校准或软件减去 |

**正确解析**
```python
# raw bytes of a SERVO_OUTPUT_RAW
port = data[0]
vals = [
 struct.unpack('<H', data[1+2*i:3+2*i])[0]
 for i in range(min(8, (len(data)-1)//2))
]
# PWM 单位：1000=最小 1500=中位 2000=最大
```

---

## 3) COMMAND_LONG 参数坑（高发）

| 消息 | 命令号 | params 类型 | 报文长度 | 错误示例 | 正确写法 |
|------|--------|-------------|----------|-----------|----------|
| COMMAND_LONG | 76 | float[7] | 34 B | 传 int → 解析时端会不匹配 | 全部 float，末尾 2 B confirmation |

```python
# ARM 指令 (命令:400)
# 错误（太短）
wrong=struct.pack('<IHHHHH', 400, 1, 0,0,0,0) # payload 14 B

# 正确 (34 B)
correct=struct.pack('<I7fH',
 400, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0,
 0 # confirmation
)
```

---

## 4) MAVLink v1.0 消息 ID 快速索引

简版速查：需要时 `grep msgid= <文件>` 搜索替换更方便。

| 消息名 | ID | 用途 | Python unpack（< 前缀） |
|-------|----|------|-----------------------------|
| HEARTBEAT | 0 | 飞控模式、ARM 状态 | `<IHBxxB` (共 8B) |
| SYS_STATUS | 1 | 电压/电流/剩余电量 | `<HBHHhB` |
| GPS_RAW_INT | 2 | GPS 原始坐标 | `<BxxxiiiiH` |
| RAW_IMU | 27 | 3轴加速度+角速度 | `<hhh hh hh h` |
| SERVO_OUTPUT_RAW | 36 | APM 8路 PWM（原始） | `<B HHHHHHHH` (B=port) |
| STATUSTEXT | 253 | 飞控日志字符串 | `<B xxxs` (字符串) |
| PARAM_VALUE | 22 | 参数读取 | `<16s f h` (前16字节名) |

---

## 5) 技能梳理索引

| Topic | key | 在连接层内对应小节 |
|-------|-----|-------------------|
| 手动解析 MAVLink | 把包解成字典 | **3) COMMAND_LONG 参数坑** 与 **本页其余小节** |
| 舵机控制 API | MAV_CMD_DO_SET_SERVO | connectivity-layer SKILL.md："舵机控制核心" |
| 传感器公式 | voltage raw → V | **2) SYS_STATUS** |
| 固件升级 Hack | avrdude 升级流程 | [references/apm-firmware-upgrade.md](references/apm-firmware-upgrade.md) （待补）