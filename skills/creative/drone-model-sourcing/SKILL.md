---
name: drone-model-sourcing
description: 从 GitHub 开源项目搜索、下载 FPV 穿越机 3D 模型（STEP/DXF/STL），整理成本地可用的模型库。触发于用户要求了解/下载无人机图纸时。
---

# 开源穿越机模型获取技能

## 核心信息

GitHub 是最丰富的免费 FPV 穿越机机架 3D 模型来源：
- `thingiverse.com` — 有 Cloudflare 验证，浏览器无法自动过
- `printables.com` — 访问超时
- `cults3d.com` — 访问超时
- **GitHub** — 最稳定，直接 API 搜索+下载

## 优质来源仓库

| 仓库 | 类型 | 主要格式 | Stars |
|------|------|----------|-------|
| tbs-trappy/source_one | 经典开源机架 | DXF | 607 |
| WE-are-FPV/JeNo-5.1 | 主流5寸 | STEP/STL/DXF | 68 |
| WE-are-FPV/JeNo-7 | 7寸长航程 | STEP/STL/DXF | 32 |
| WE-are-FPV/JeNo-3-3.5 | 3寸微型 | STEP/STL/DXF | 25 |
| WE-are-FPV/JeNo-Pocket | 2.5寸超微 | STEP | 20 |
| ps915/source_x | 巨型穿越机 | DXF | 43 |
| ps915/source_micro | 微穿越机 | DXF | 38 |
| aeracoop/flone-frame | 激光切割四轴 | DXF/SVG | 23 |

## 下载命令模板

```bash
BASE=~/.hermes/drone-models
mkdir -p $BASE/STEP $BASE/DXF $BASE/STL

# STEP 下载
curl -s -L --max-time 30 -o "$BASE/STEP/<filename>.step" "<raw_url>"

# DXF 下载
curl -s -L --max-time 30 -o "$BASE/DXF/<filename>.dxf" "<raw_url>"

# STL 下载
curl -s -L --max-time 30 -o "$BASE/STL/<filename>.stl" "<raw_url>"
```

## GitHub API 搜索

```bash
# 搜索包含 STEP 文件的仓库
curl -s "https://api.github.com/search/repositories?q=fpv+frame+step+in:path&sort=stars&per_page=10"

# 搜索包含 DXF 文件的仓库
curl -s "https://api.github.com/search/repositories?q=fpv+drone+dxf+in:path&sort=stars&per_page=10"
```

## raw.githubusercontent.com 下载地址格式

```
https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}
```

## 文件格式选择

| 使用目的 | 推荐格式 | 工具链 |
|----------|----------|--------|
| CNC 机床加工 | **DXF**（矢量，ezdxf 可直接导入） | AutoCAD/FreeCAD/CAMC |
| 激光切割 | **SVG**（转换后更干净） | LightBurn/RDWorks/SheetCAM |
| 3D 打印 | **STL**（网格格式） | Cura/PrusaSlicer/ BambuLab |
| CAD 建模参考 | **STEP**（精确曲面） | SolidWorks/FreeCAD/Rhino |

### DXF vs SVG 选择建议

- **激光切割优先 SVG**：DXF 常含填充剖面线/标注文字，SVG 转换后只保留轮廓线，更干净
- **CNC 铣削优先 DXF**：DXF 保留层信息，可区分轮廓/钻孔/雕刻路径
- **转换工具链**：DXF → SVG → PNG 预览用 `ezdxf + svgwrite + rsvg-convert`

## DXF/DWG 格式检测与处理

**关键发现（2026-05 实测）：**
部分"DXF"文件实为 **AutoCAD DWG 格式**（文件扩展名误导）。JeNo 系列 DXF 实为 AC1027（AutoCAD 2013）格式，`ezdxf` 库可直接读取，无需转换。

### 快速检测方法

```bash
# 方法1：检查文件头（最快）
head -c 100 file.dxf | cat -v | grep -E 'SECTION|AC1027|AC1015'
# 有 AC1027/AC1015 → DWG 格式，用 ezdxf 读
# 有普通 DXF 文本组码 → 真 DXF

# 方法2：Python 检测
python3 -c "
with open('file.dxf','rb') as f:
    hdr = f.read(200).decode('utf-8', errors='ignore')
if 'AC1027' in hdr or 'AC1015' in hdr or 'AC1014' in hdr:
    print('DWG format - use ezdxf')
elif 'ENTITIES' in hdr:
    print('Real DXF - plain text format')
else:
    print('Unknown binary format')
"
```

### 已知 DWG→DXF 误标文件

| 文件 | 实际版本 | 读取方式 |
|------|----------|----------|
| JeNo5_1.6.0_ALL_VERSIONS.dxf | AC1027 (AutoCAD 2013) | `ezdxf.readfile()` ✅ |
| JeNo7_ALL_VERSIONS.dxf | AC1027 | `ezdxf.readfile()` ✅ |
| JeNo3_ALL_VERSIONS.dxf | 待确认 | `ezdxf.readfile()` ✅ |

### SVG 转换工具链

```bash
# 1. DXF/DWG → SVG（Python ezdxf + svgwrite）
python3 << 'PYEOF'
import ezdxf, svgwrite, math, os
# 见 references/dxf_to_svg_pipeline.md

# 2. SVG → PNG 预览（rsvg-convert 可用，inkscape/cairosvg 不可用）
rsvg-convert -w 1600 -h 1600 input.svg -o output.png

# 3. 多图拼接 INDEX（Python PIL）
python3 << 'PYEOF'
from PIL import Image, ImageDraw
# 见 references/png_index_generation.md
PYEOF
```

### 已知可用的 SVG/图像转换工具

| 工具 | 路径 | 可用 |
|------|------|------|
| rsvg-convert | `/usr/bin/rsvg-convert` | ✅ |
| ImageMagick convert | `/usr/bin/convert` | ✅ |
| inkscape | 不存在 | ❌ |
| cairosvg | Python import 不可用 | ❌ |

## 本地存储路径

```
~/.hermes/drone-models/
├── STEP/     # CAD 模型
├── DXF/      # 工程图纸
├── STL/      # 3D 打印
└── README.md # 清单文档
```

## DXF 精确解析工作流（ezdxf）

使用 `ezdxf` 库读取 DXF 而非纯文本正则，ezdxf 已预装在 venv 中。

```python
import ezdxf

doc = ezdxf.readfile('/path/to/file.dxf')
msp = doc.modelspace()
print("DXF units:", doc.header.get('$INSUNITS', '?'))  # 4=Millimeters, 1=Inches, 0=Unitless
print("Version:", doc.dxfversion)

for entity in msp:
    etype = entity.dxftype()
    if etype == 'LWPOLYLINE':
        # ⚠️ points() 是 context manager，必须用 `with`
        with entity.points() as pts:
            pts = list(pts)
        xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
        print(f"LWPOLYLINE {len(pts)}pts: W={max(xs)-min(xs):.2f} H={max(ys)-min(ys):.2f}")
        for j,p in enumerate(pts[:8]):
            print(f"  {j}: ({p[0]:.2f},{p[1]:.2f})")
    elif etype == 'CIRCLE':
        c=entity.dxf.center; r=entity.dxf.radius
        print(f"CIRCLE: ({c[0]:.2f},{c[1]:.2f}) r={r:.2f}")
    elif etype == 'ARC':
        c=entity.dxf.center; r=entity.dxf.radius
        print(f"ARC: ({c[0]:.2f},{c[1]:.2f}) r={r:.2f} "
              f"{entity.dxf.start_angle:.1f}~{entity.dxf.end_angle:.1f}")
```

**常见坑：**
- `entity.points` 是 method，不是 property，直接迭代会报 `TypeError: 'method' object is not iterable`
- 必须调用 `entity.points()` 返回 context manager，再用 `with` + `list()`
- ezdxf 1.4+ 的标准用法，之前的版本行为不同

### DXF→CAD 坐标变换

DXF 原点通常在图纸左下角，CAD 软件以中心为原点，需做变换：

```python
X_MIN, X_MAX = -37.5, 42.0   # 从 DXF 实测
Y_MIN, Y_MAX = -303.0, -277.0

cx = (X_MIN + X_MAX) / 2  # 中心化
cy = (Y_MIN + Y_MAX) / 2

def dxf_to_cad(x, y):
    # DXF 坐标转 CAD 中心原点
    return x - cx, y - cy

# DXF 中 24 点外轮廓旋转 90° 用于 CAD：
# new_x = old_y, new_y = -old_x（绕原点旋转90°后再中心化）
def rotate90(x, y):
    return y, -x
```

## GitHub API 下载大文件 / 二进制文件

raw.githubusercontent.com 对大文件（>50MB）直接下载会失败，改用 GitHub API：

```bash
# 通过 API 获取 base64 编码内容
curl -s "https://api.github.com/repos/{owner}/{repo}/contents/{path}" | \
  python3 -c "
import json,sys,base64
d=json.load(sys.stdin)
content=d.get('content','')
if content:
    # base64 要补齐 padding
    padding = 4 - len(content) % 4
    if padding < 4: content += '=' * padding
    data = base64.b64decode(content)
    with open('/tmp/output', 'wb') as f: f.write(data)
    print('size:', len(data))
else:
    # 备选：download_url
    import urllib.request
    urllib.request.urlretrieve(d.get('download_url',''), '/tmp/output')
    import os; print('file size:', os.path.getsize('/tmp/output'))
"
```

适用场景：`.stl` 二进制文件、`.dxf` 大文件（94MB Source One DXF 必须用此法）

## Cloudflare 拦截站点（2026-05 实测）

以下站点**无法访问**（被 Cloudflare 403）：
- `grabcad.com` — 需要 JS 渲染，curl/wget 返回 Cloudflare 挑战页
- `mechstream.com` — Cloudflare 验证
- `3dmodels.org` — 301 重定向失败
- `thingiverse.com` — Cloudflare 验证
- `cults3d.com` — 超时
- `yeggi.com` / `sketchfab.com` — 反爬

**替代方案：GitHub 搜索 + GrabCAD 手动下载**（用户自己在浏览器登录 GrabCAD 下载，文件传给 Agent 处理）

## gmsh 从零构建 CAD 模型

gmsh 有两个 API 层，**不可混用**：
- `gmsh.model.geo` — 2D 面/线/点，只有 `extrude`/`revolve` 可做 3D
- `gmsh.model.occ` — 完整 3D 体/面/线/点，布尔运算

**正确模式**：`occ` 做所有几何，`geo.extrude` 拉伸 occ 创建的面。

> ⚠️ 完整踩坑记录、API 签名、错误速查见 `references/gmsh_occ_api.md`
> ⚠️ 可运行的 5 寸穿越机完整脚本见 `templates/source_one_build.py`

### 核心要点

```python
# occ 创建体
bp = occ.add_box(x, y, z, dx, dy, dz)
cyl = occ.add_cylinder(x, y, z, dx, dy, dz, r)

# occ 创建面（只用 add_surface_filling）
pts = [occ.add_point(x,y,z) for ...]
ls = [occ.add_line(pts[i], pts[(i+1)%4]) for i in range(4)]
surf = occ.add_surface_filling(occ.add_curve_loop(ls))

# geo.extrude 拉伸 occ 的面（只能用 geo.extrude）
ext = geo.extrude([(2, surf)], 0, 0, ARM_THICK)
arm_vols = [t for d, t in ext if d == 3]  # 取返回的体 tag

# occ.fuse — 必须用 [(dim, tag), ...] 格式
fused = occ.fuse([(3, bp)], [(3, v) for v in other_parts])
```

### 已知限制

- gmsh OCC 融合 10+ 体时 mesh generate(3) 可能超时 → 调大 `Mesh.CharacteristicLengthMax` 到 1.5+ 或分别导出零件
- `gmsh.fltk`（图形界面截图）在无头环境不可用 → 用 `image_generate` AI 绘图生成预览替代
- 沙箱 `execute_code` 中 gmsh Info 输出被截断 → 用 `terminal` 工具执行脚本
- 多次 `occ.synchronize()` 是必要的，每步布尔运算后都要同步
- 沙箱环境 `execute_code` 中 gmsh 输出会被截断（Info 日志丢失），用 `terminal` 工具执行较长脚本更可靠

## Source Micro / Source One 精确几何数据（2026-05 实测）

| `references/source_micro_dxf_geometry.md` | TBS Source Micro DXF 实测坐标、建模参数 |
| `references/image_analysis_pil.md` | PIL 图像统计分析法（暗色图/ vision_analyze 失效时的备选） |

## U 盘权限注意

- `/mnt/usb` — USB 挂载点，文件可读但**新建文件报 Permission denied**
- U 盘目录 `/mnt/usb/hermes-agent/` 内文件可读，新建文件被拒
- 如需备份到 U 盘：下载到 `~/.hermes/drone-models/` 后手动复制

## Vision 分析本地图片注意

`vision_analyze()` 对本地图片路径支持不稳定，即使在 `/home/saber/` 下也可能报 `Access denied`。**图片分析备选方案**：

```python
# 用 PIL 分析图片统计特征（不依赖 vision_analyze）
from PIL import Image
import numpy as np

img = Image.open('/path/to/image.jpg')
arr = np.array(img)

# 基础统计
print('RGB均值:', np.mean(arr, axis=(0,1)))  # 判断色调
print('亮度均值:', np.mean(arr))
gray = np.mean(arr, axis=2)
print('亮度范围:', np.min(gray), '~', np.max(gray))  # 暗色图<50, 亮色图>150

# 高亮区域（主体位置）
bright = gray > 180
ys, xs = np.where(bright)
if len(ys) > 0:
    print(f'主体位置: Y={ys.min()}-{ys.max()}, X={xs.min()}-{xs.max()}')

# 列/行均值（检测背景布）
col_means = [np.mean(gray[:, x]) for x in range(0, gray.shape[1], 20)]
print('列均值std:', np.std(col_means))  # std>5 说明有纹理/物体，std<3 说明是大面积纯色背景
```

## 抖音 (Douyin) 图文作品提取（2026-05 实测）

适用：用户分享抖音链接，要求分析/学习图文内容。

### 短链接解析

```bash
# 抖音短链接格式：https://v.douyin.com/p_XXXXXXXXXX/
# curl -sI -L 可获取重定向后的真实 URL
curl -sI -L --max-time 10 "https://v.douyin.com/p_FXmVoNNIc/" | grep -i location
```

### 图文页面 URL

```
https://www.douyin.com/note/{note_id}
https://www.iesdouyin.com/share/note/{note_id}/
```

注意：`browser_navigate()` 访问抖音PC版可能超时（JS 渲染慢），用 `browser_console()` 执行 JS 提取数据更可靠。

### 提取图文内容（browser_console JS）

```javascript
// 获取页面所有图片URL（只要 douyinpic 域名）
const allImages = Array.from(document.querySelectorAll('img[src]'))
  .map(img => img.src)
  .filter(s => s.includes('douyinpic'))
  .slice(0, 10);
JSON.stringify(allImages);

// 获取页面标题/描述
JSON.stringify({
  title: document.title,
  desc: document.querySelector('[class*="note-desc"]')?.innerText?.slice(0,500) || ''
});
```

### 下载图文图片

抖音图片 URL 带有签名参数（`x-signature=...`, `x-expires=...`, `lk3s=...`），**必须带完整参数下载**，否则403。

```bash
# 从 browser_console 获取的 URL 直接用 curl 下载
curl -sL --max-time 15 \
  -o /tmp/douyin_main.jpg \
  "https://p3-pc-sign.douyinpic.com/obj/xxx?lk3s=xxx&x-signature=xxx&x-expires=xxx"

# 下载后复制到 /home/saber/ 才可用于 vision_analyze
cp /tmp/douyin_main.jpg /home/saber/douyin_main.jpg
```

### 抖音页面元数据（直接可用的字段）

页面 `<title>` 标签包含：标题 + 标签关键词  
页面 snapshot 中包含：`StaticText` 元素含发布时间、点赞/评论数、作者信息  
作者信息：搜索 `YJ Eadric` 可找到粉丝数（4353）、获赞数（5.4万）

### 已验证的抖音域名

```
douyin.com          # 主站
iesdouyin.com       # 旧版移动端
douyinpic.com       # 图片 CDN
p3-pc-sign.douyinpic.com  # 签名图片
```

### 已知限制

- 抖音页面需要 JS 渲染，`curl` 直接请求只能拿到部分内容
- 图片签名 URL 有时效（`x-expires`），过期需重新从页面提取
- 视频内容无法通过此法提取（图文的视频封面可提取）
- Vision 工具对 `/home/saber/` 下的图片也可能无法分析，备选 PIL 图像统计分析法

## 验证下载完整性

```bash
ls -lh ~/.hermes/drone-models/STEP/ ~/.hermes/drone-models/DXF/ ~/.hermes/drone-models/STL/
```

---

## OpenSCAD → gmsh STEP 转换（实战总结）

## 飞控读取（串口连接）

**适用场景**：通过 USB 连接飞控，读参数、日志、MAVLink 数据。

### 串口检测

```bash
# 查看所有串口设备
ls -la /dev/serial/by-id/          # 首选（稳定标识）
ls -la /dev/ttyACM* /dev/ttyUSB*  # 备用

# 通过 sysfs 枚举 USB 设备（含厂商信息）
python3 -c "
import os
for d in os.listdir('/sys/bus/usb/devices/'):
    try:
        vendor = open(f'/sys/bus/usb/devices/{d}/idVendor').read().strip()
        product = open(f'/sys/bus/usb/devices/{d}/idProduct').read().strip()
        mfg = open(f'/sys/bus/usb/devices/{d}/manufacturer').read().strip() if os.path.exists(f'/sys/bus/usb/devices/{d}/manufacturer') else ''
        prod = open(f'/sys/bus/usb/devices/{d}/product').read().strip() if os.path.exists(f'/sys/bus/usb/devices/{d}/product') else ''
        if vendor:
            print(f'{d}: {vendor}:{product} | {mfg} | {prod}')
    except: pass
"
```

### 常用飞控串口参数

| 固件 | 波特率 | 协议 | 典型设备 ID |
|------|--------|------|-------------|
| Betaflight | 115200 | CLI/MSP | STM32 CDC |
| ArduPilot | 115200 | MAVLink | /dev/ttyACM* |
| Cleanflight | 115200 | MSP | STM32 |
| Arduino (自定义) | 9600/57600/115200 | 文本/二进制 | Arduino Mega 2560 |

### 串口读取工具链

**pyserial 需安装到 hermes venv**（系统 Python 无此模块）：
```bash
/home/saber/.hermes/hermes-agent/venv/bin/pip3 install pyserial -q
```

**MAVLink 连接**（推荐）：
```bash
/home/saber/.hermes/hermes-agent/venv/bin/pip3 install pymavlink -q
python3 -c "
from pymavlink import mavutil
m = mavutil.mavlink_connection('/dev/ttyACM0', baud=115200)
msg = m.recv_match(type=['HEARTBEAT','SYS_STATUS','ATTITUDE'], timeout=5)
if msg: print(msg)
"
```

**二进制/文本串口扫描**：
```python
import serial, time

port = '/dev/ttyACM0'
for br in [115200, 57600, 38400, 19200, 9600]:
    try:
        s = serial.Serial(port, br, timeout=0.5)
        s.flushInput()
        s.write(b'\n')  # 触发飞控 CLI 响应
        time.sleep(0.5)
        data = s.read(128)
        s.close()
        if data.strip(b'\xff\x00')[:4] != b'\x00\x00\x00\x00':
            hexd = data[:32].hex()
            ascii_data = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[:32])
            print(f'BR={br}: {hexd} | {ascii_data}')
    except: pass
```

### 已知设备 ID

- `2341:0010` = Arduino Mega 2560（CDC ACM 驱动）
- Pixhawk/Cube 通常显示为 `26ac:*` 或 `0483:*`
- Betaflight F4/F7 刷固件后显示为 `0483:5740` (STM32)

### 注意事项

- **pymavlink 不在 hermes venv 中**：需先安装
- **pyserial 不在系统 Python 中**：用 hermes venv 的 python
- **Arduino Mega 2560** 不是飞控，而是 USB-TTL 适配器或自定义控制器（如 LED 屏、OSD 生成器）
- **飞控未识别时**：检查是否上电（部分飞控需Battery供电才枚举USB）、驱动是否加载（`lsmod | grep cdc_acm`）

**用户提供了原始 OpenSCAD 代码，要求直接转换为 STEP 文件。完整工作流如下：

### Step 1：环境检测

```bash
which gmsh && gmsh --version  # gmsh CLI 存在性
python3 -c "import gmsh; print(gmsh.__version__)"  # gmsh Python 模块
# OpenSCAD (openscad CLI) 不需要——gmsh OCC 可以直接建模
```

### Step 2：gmsh 建模（推荐在 `terminal` 工具执行）

用 `terminal` 而非 `execute_code` 沙箱执行 gmsh 脚本，因为：
- 沙箱会截断 gmsh Info 输出（`Info: Writing '/tmp/...step'`）
- 沙箱 timeout 更短

```python
# 用 terminal 工具执行脚本
# 脚本保存到 /tmp/build_model.py，然后:
# terminal(command="python3 /tmp/build_model.py", timeout=60)
```

### Step 3：核心建模模式（gmsh OCC API）

**`gmsh.model.occ.rotate()` 返回 `None`**，不像其他 OCC 方法返回新实体 tag。

```python
# ✅ 正确用法：先创建，再旋转（in-place，不需要捕获返回值）
knurl = gmsh.model.occ.addBox(...)
gmsh.model.occ.rotate([(3, knurl)], 0, 0, 0, 0, 0, 1, angle)  # 返回 None，正常

# ❌ 错误：rib_rot = occ.rotate(...) → rib_rot is None
rib_rot = gmsh.model.occ.rotate([(3, rib)], ...)
ribs.append(rib_rot[0][1])  # TypeError: 'NoneType' object is not subscriptable
```

**布尔运算 `cut()` 返回值解包**：

```python
# result 结构：[(modified_tool_object_tags, kept_tool_tags), ...]
# result[0] = (modified_tool_tags, kept_tool_tags)
# result[0][0] = modified_tool_tags (list of dimTag)
# result[0][0][1] = 第一个 dimTag 的 tag（数值）

result = occ.cut([(3, box)], [(3, cylin)], removeTool=True)
main_vol = result[0][0][1]  # 取第一个保留体的 tag
# ⚠️ 不要写：_, (main_vol,) = result — result[0] 长度是2但结构不对

# 更安全的方式（检查空值）：
if result and result[0] and result[0][0]:
    main_vol = result[0][0][1]
```

**布尔融合 `fuse()`**：

```python
fused = occ.fuse([(3, main_vol)], [(3, r) for r in ribs] + [(3, k) for k in knurls], removeTool=True)
final_vol = fused[0][0][1]
```

### Step 4：OpenSCAD → gmsh 语法对照

| OpenSCAD | gmsh OCC |
|----------|----------|
| `cube([w,h,d], center=true)` | `occ.addBox(-w/2, -h/2, -d/2, w, h, d)` |
| `cylinder(h, d, center=true, $fn=32)` | `occ.addCylinder(cx, cy, cz-d/2, 0, 0, d, r)` |
| `difference() { box; cyl }` | `cut([(3,box)],[(3,cyl)])` |
| `translate([x,y,z]) rotate(a) cube(...)` | 先 `addBox` 再 `occ.rotate([(3,tag)], ax,ay,az, 0,0,1, a)` |
| `for(i=[0:N-1])` + `rotate(angle) translate(...)` | `for i in range(N): angle=i*360/N; obj=addBox(...); occ.rotate(...)` |

### Step 5：OpenSCAD 特有操作的替代方案

**`$fn=32`（圆周分段）**：gmsh 的 `$fn` 对应 `Mesh.CharacteristicLengthMax` 调小，或直接用足够多的分段（cylinder 默认已够）。

**顶部倒角（chamfer）**：OpenSCAD 的 `rotate([0,45,0]) cube` 是近似简化处理，在 gmsh 中直接融合 box 到主体即可，不需要真正倒角特征。

**多面体/拉伸体**：OpenSCAD 的 `linear_extrude` → gmsh 用 `geo.extrude([(2, surfaceTag)], dx, dy, dz)`。

### Step 6：验证 STEP 文件

```python
with open(out_path) as f:
    lines = f.readlines()
has_header = any("ISO-10303" in l for l in lines[:10])
has_data = any("PRODUCT" in l for l in lines[:50])
print("✅ STEP 头部" if has_header else "❌ 格式错误")
```

### 输出路径

默认：`/tmp/` + `*.step`，复制到 `~/.hermes/hermes_workspace/` 永久保存。

### 已知限制

- gmsh 不支持 OpenSCAD 的 `hull()`（凸包）和 `minkowski()`（ Minkowski 和）
- 复杂布尔组合（10+ 体）导出前可调大 `Mesh.CharacteristicLengthMax` 加快速度
- `gmsh.write()` 不需要先 `gmsh.model.occ.synchronize()`，内部会自动同步
