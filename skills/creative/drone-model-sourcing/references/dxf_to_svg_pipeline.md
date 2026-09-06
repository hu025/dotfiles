# DXF/DWG → SVG → PNG 完整工具链

> 适用场景：从 GitHub 下载的 DXF/DWG 工程图，转换为激光切割 SVG 和 CNC 预览 PNG

## 环境要求

```bash
pip install ezdxf svgwrite   # Python 库
which rsvg-convert           # SVG→PNG（/usr/bin/rsvg-convert ✅）
```

## 完整脚本

```python
#!/usr/bin/env python3
"""
dxf_to_svg.py — DXF/DWG → SVG 转换器
用法: python3 dxf_to_svg.py <输入.dxf> <输出.svg> [名称标签]
"""
import ezdxf, svgwrite, math, os, sys

def dxf_to_svg(dxf_path, svg_path, name=""):
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()

    all_pts, circles, arcs = [], [], []
    for e in msp:
        if e.dxftype() == 'LINE':
            all_pts += [(s.x,s.y) for s in [e.dxf.start, e.dxf.end]]
        elif e.dxftype() == 'CIRCLE':
            circles.append((e.dxf.center.x, e.dxf.center.y, e.dxf.radius))
        elif e.dxftype() == 'ARC':
            arcs.append((e.dxf.center.x, e.dxf.center.y, e.dxf.radius,
                        e.dxf.start_angle, e.dxf.end_angle))
        elif e.dxftype() == 'LWPOLYLINE':
            for pt in e.get_points():
                all_pts.append((pt[0], pt[1]))
        elif e.dxftype() == 'POLYLINE':
            for v in e.vertices:
                all_pts.append((v.dxf.location.x, v.dxf.location.y))

    # 计算边界
    if all_pts:
        xs=[p[0] for p in all_pts]; ys=[p[1] for p in all_pts]
        x_min,x_max = min(xs),max(xs); y_min,y_max = min(ys),max(ys)
    else:
        x_min=min(c[0]-c[2] for c in circles); x_max=max(c[0]+c[2] for c in circles)
        y_min=min(c[1]-c[2] for c in circles); y_max=max(c[1]+c[2] for c in circles)

    for c in circles:
        x_min=min(x_min,c[0]-c[2]); x_max=max(x_max,c[0]+c[2])
        y_min=min(y_min,c[1]-c[2]); y_max=max(y_max,c[1]+c[2])

    W = x_max - x_min + 30; H = y_max - y_min + 30; pad = 15
    dwg = svgwrite.Drawing(svg_path, size=(f'{W}mm', f'{H}mm'))
    dwg.viewbox(0, 0, W, H)
    dwg.add(dwg.rect(insert=(0,0), size=('100%','100%'), fill='white'))

    def tx(x): return x - x_min + pad
    def ty(y): return (y_max + y_min) - y + pad  # Y轴翻转

    g = dwg.g(stroke='black', stroke_width=0.3, fill='none', stroke_linecap='round')
    for e in msp:
        if e.dxftype() == 'LINE':
            s,t = e.dxf.start, e.dxf.end
            g.add(dwg.line((tx(s.x),ty(s.y)),(tx(t.x),ty(t.y))))
        elif e.dxftype() == 'CIRCLE':
            c,r = e.dxf.center, e.dxf.radius
            g.add(dwg.circle(center=(tx(c.x),ty(c.y)), r=r))
        elif e.dxftype() == 'ARC':
            c,r = e.dxf.center, e.dxf.radius
            sa,ea = math.radians(e.dxf.start_angle), math.radians(e.dxf.end_angle)
            path = svgwrite.path.Path(
                d=f"M {tx(c.x+r*math.cos(sa)):.2f},{ty(c.y+r*math.sin(sa)):.2f} "
                  f"A {r:.2f} {r:.2f} 0 0 1 {tx(c.x+r*math.cos(ea)):.2f},{ty(c.y+r*math.sin(ea)):.2f}")
            g.add(path)
        elif e.dxftype() == 'LWPOLYLINE':
            pts = list(e.get_points())
            if len(pts) >= 2:
                closed = bool(e.dxf.flags & 1)
                d = f"M {tx(pts[0][0]):.2f},{ty(pts[0][1]):.2f}"
                for pt in pts[1:]:
                    d += f" L {tx(pt[0]):.2f},{ty(pt[1]):.2f}"
                if closed: d += " Z"
                g.add(svgwrite.path.Path(d))

    dwg.add(g)
    dim_w=x_max-x_min; dim_h=y_max-y_min
    dwg.add(dwg.text(f"{name}  {dim_w:.0f}×{dim_h:.0f}mm",
                     insert=(pad, H-pad+4), font_size='3', fill='#CC0000'))
    dwg.save()

    print(f"  ✅ {name}: {dim_w:.0f}×{dim_h:.0f}mm → {svg_path}")
    return f"{dim_w:.0f}×{dim_h:.0f}mm"

if __name__ == '__main__':
    base = '/home/saber/.hermes/drone-models'
    os.makedirs(f'{base}/SVG', exist_ok=True)

    files = [
        ('DXF/SourceMicro_v0.1_bottom_plate.dxf', 'SourceMicro_Bottom'),
        ('DXF/SourceMicro_v0.1_top_plate.dxf',    'SourceMicro_Top'),
        ('DXF/SourceX_v1.0_bottom_plate.dxf',      'SourceX_Bottom'),
        ('DXF/SourceX_v1.0_top_plate.dxf',         'SourceX_Top'),
        ('DXF/SourceX_v1.0_arm_tubes.dxf',         'SourceX_Arms'),
        ('DXF/JeNo5_1.6.0_ALL_VERSIONS.dxf',       'JeNo5'),
        ('DXF/JeNo7_ALL_VERSIONS.dxf',               'JeNo7'),
        ('DXF/JeNo3_ALL_VERSIONS.dxf',               'JeNo3'),
    ]

    for fpath, name in files:
        dxf_to_svg(f'{base}/{fpath}', f'{base}/SVG/{name}.svg', name)

    # SVG → PNG
    import subprocess
    for svgf in os.listdir(f'{base}/SVG'):
        if not svgf.endswith('.svg'): continue
        name = svgf.replace('.svg','')
        subprocess.run(['rsvg-convert','-w','1600','-h','1600',
                       f'{base}/SVG/{svgf}', '-o', f'{base}/PNG/{name}.png'],
                      capture_output=True)
        print(f"  PNG: {name}.png")
```

## PNG 预览图拼接（总览图）

```python
from PIL import Image, ImageDraw

SVG_DIR = '/home/saber/drone-models/SVG'
OUT_DIR = '/home/saber/drone-models/PNG'
os.makedirs(OUT_DIR, exist_ok=True)

files = sorted([f for f in os.listdir(SVG_DIR) if f.endswith('.svg')])
cols, rows = 3, 3
cell_w, cell_h = 500, 500
pad = 10; header = 60

canvas = Image.new('RGB',
    (cols*cell_w+(cols+1)*pad, rows*cell_h+(rows+1)*pad+header), 'white')
draw = ImageDraw.Draw(canvas)

labels = [
    ('SourceMicro_Bottom','94×94mm\n微型底板'),
    ('SourceMicro_Top',  '80×26mm\n微型顶板'),
    ('SourceX_Bottom',   '249×293mm\nX-Class底板'),
    # ... 继续添加
]

for i,(fname,label) in enumerate(labels):
    col=i%cols; row=i//cols
    x=col*cell_w+(col+1)*pad; y=row*cell_h+(row+1)*pad+header
    img_file=f'{OUT_DIR}/{fname}.png'
    if os.path.exists(img_file):
        img=Image.open(img_file).convert('RGB')
        # 居中裁剪为正方形
        iw,ih=img.size; tr=cell_w/cell_h; ir=iw/ih
        if ir>tr:
            nw=int(ih*tr); o=(iw-nw)//2; img=img.crop((o,0,o+nw,ih))
        else:
            nh=int(iw/tr); o=(ih-nh)//2; img=img.crop((0,o,iw,o+nh))
        img=img.resize((cell_w,cell_h), Image.LANCZOS)
        canvas.paste(img,(x,y))
    draw.rectangle([x,y,x+cell_w,y+cell_h], outline='#CCCCCC', width=2)
    draw.text((x+pad,y+pad), label.split('\n')[0], fill='#CC0000')
    if '\n' in label:
        draw.text((x+pad,y+pad+16), label.split('\n')[1], fill='#666666')

draw.text((pad,pad//2),'FPV穿越机图纸集', fill='#333333')
canvas.save(f'{OUT_DIR}/INDEX.png', quality=95)
```

## 实测结果（2026-05-15）

| 文件 | 尺寸 | 格式 |
|------|------|------|
| SourceMicro_Bottom.svg | 94×94mm | ✅ 完整 |
| SourceMicro_Top.svg | 80×26mm | ✅ 完整 |
| SourceX_Bottom.svg | 249×293mm | ✅ 完整 |
| SourceX_Top.svg | 279×293mm | ✅ 完整 |
| SourceX_Arms.svg | 231×371mm | ✅ 完整 |
| JeNo5.svg | 1254×2856mm | ✅ 完整（含标注） |
| JeNo7.svg | 1509×1963mm | ✅ 完整 |
| JeNo3.svg | 1515×1983mm | ✅ 完整 |
