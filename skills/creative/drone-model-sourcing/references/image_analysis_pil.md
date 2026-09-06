# PIL 图像统计分析法（备选视觉分析）

当 `vision_analyze()` 无法使用时，用 PIL + numpy 分析图片的统计特征来推断内容。

## 适用场景

- vision_analyze 报 Access denied 或"看不到图片"
- 图片平均亮度 < 50（极暗图像，视觉模型难以识别）
- 需要快速判断图片色调/主体位置

## 基础分析脚本

```python
from PIL import Image
import numpy as np

img = Image.open('/path/to/image.jpg')
arr = np.array(img)
gray = np.mean(arr, axis=2)
h, w = arr.shape[:2]

# ── 基础统计 ──────────────────────────────────────────
print(f'尺寸: {w}×{h}')
print(f'RGB均值: R={np.mean(arr[:,:,0]):.1f} G={np.mean(arr[:,:,1]):.1f} B={np.mean(arr[:,:,2]):.1f}')
print(f'亮度均值: {np.mean(gray):.1f}  (暗<50, 中间70~140, 亮>180)')
print(f'亮度std: {np.std(gray):.2f}  (std>20说明有纹理/物体)')

# ── 主体位置检测 ──────────────────────────────────────
bright = gray > 180
ys, xs = np.where(bright)
if len(ys) > 0:
    print(f'高亮主体: Y={ys.min()}-{ys.max()}(H={ys.max()-ys.min()}), X={xs.min()}-{xs.max()}(W={xs.max()-xs.min()})')
    bright_region = arr[ys.min():ys.max()+1, xs.min():xs.max()+1]
    print(f'高亮区RGB: R={np.mean(bright_region[:,:,0]):.0f} G={np.mean(bright_region[:,:,1]):.0f} B={np.mean(bright_region[:,:,2]):.0f}')

# ── 灰度直方图（快速判断整体明暗）────────────────────
vals = np.histogram(gray.flatten(), bins=10)[0]
for i, c in enumerate(vals):
    lo = i * 255 // 10
    hi = (i+1) * 255 // 10
    bar = '#' * int(c / max(vals) * 40)
    print(f'  {lo:3d}-{hi:3d}: {c:8d} {bar}')

# ── 区域亮度分布 ──────────────────────────────────────
regions = {
    'top-left':     arr[:h//3, :w//3],
    'top-right':    arr[:h//3, 2*w//3:],
    'bottom-left':  arr[2*h//3:, :w//3],
    'bottom-right': arr[2*h//3:, 2*w//3:],
    'center':       arr[h//3:2*h//3, w//3:2*w//3],
}
for name, region in regions.items():
    print(f'{name}: brightness={np.mean(region):.1f}')

# ── 列/行均值标准差（判断背景纯度）────────────────────
col_std = np.std([np.mean(gray[:, x]) for x in range(0, w, 10)])
row_std = np.std([np.mean(gray[y, :]) for y in range(0, h, 10)])
print(f'列均值std: {col_std:.2f} (std>5=有纹理, std<3=纯色背景)')
print(f'行均值std: {row_std:.2f}')

# ── 色彩通道分析 ──────────────────────────────────────
r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
if np.mean(b) > np.mean(r) * 1.2:
    print('主色调: 蓝色/冷色调 (蓝布背景?)')
elif np.mean(r) > np.mean(b) * 1.5:
    print('主色调: 红色/暖色调')
else:
    print('主色调: 中性/混合色')
```

## 灰度直方图解读

| 灰度范围 | 含义 | 典型场景 |
|---------|------|---------|
| 0-30 占比 > 80% | 极暗图 | 深色背景布+打光拍摄 |
| 30-60 占比 > 80% | 暗调图 | 暗色背景+主体 |
| 100-180 占比高 | 正常曝光 | 标准拍摄 |
| 200-255 占比 > 20% | 高亮图 | 白背景/反光表面 |

## 提亮+对比度增强（辅助分析）

```python
from PIL import ImageEnhance

img = Image.open('/path/to/image.jpg')
enhanced = ImageEnhance.Contrast(img).enhance(5.0)
enhanced = ImageEnhance.Sharpness(enhanced).enhance(2.0)
enhanced.save('/path/to/enhanced.jpg', quality=95)
```

适用于暗色图提亮后用 vision_analyze 重新分析。

## 抖音图片实测数据（2026-05）

| 图片 | 尺寸 | 亮度均值 | 主色调 |
|------|------|---------|--------|
| 封面缩略图 | 401×301 | 141 | 中性偏亮 |
| 作品主图 | 1499×1237 | 44 | 蓝色/冷色调(极暗) |

主图平均亮度仅44.9，说明是**暗色背景布+打光拍摄**，需要强力提亮才能看出主体轮廓。
