# gmsh OCC API 参考（2026-05 实测）

## gmsh 两个 API 层的本质区别

gmsh 有两个 OCC（OpenCASCADE）接口层，**不可混用点/线**：

| API 层 | 模块 | 能力 | 关键方法 |
|--------|------|------|----------|
| `gmsh.model.geo` | 2D 几何 + extrusion | 面/线/点，无立体 | `add_point`, `add_line`, `add_circle`, `add_curve_loop`, `add_plane_surface`, `extrude`, `revolve` |
| `gmsh.model.occ` | 完整 3D CAD | 体/面/线/点，布尔运算 | `add_point`, `add_line`, `add_box`, `add_cylinder`, `add_curve_loop`, `add_surface_filling`, `add_fuse`, `add_cut`, `synchronize` |

### geo 没有的方法（常见错误来源）
- ❌ `geo.add_box` — 不存在
- ❌ `geo.add_cylinder` — 不存在
- ❌ `geo.add_surface` — 不存在

### occ 没有的方法
- ❌ `occ.add_plane_surface` — 用 `add_surface_filling`
- ❌ `occ.add_extrude` — 用 `geo.extrude`

## 正确模式：occ 做几何 + geo.extrude 拉伸面

```python
import gmsh, math, sys

gmsh.initialize(sys.argv)
gmsh.model.add("ModelName")
gmsh.option.setNumber("Mesh.CharacteristicLengthMax", 0.5)

occ = gmsh.model.occ
geo = gmsh.model.geo
occ.synchronize()

# ── occ 创建 3D 体 ──
bp = occ.add_box(-75, -60, 0, 150, 120, 4)

# ── occ 创建孔（圆柱体）──
cyl = occ.add_cylinder(mx, my, -1, 0, 0, 6, MOTOR_HOLE_R)
occ.synchronize()

# ── 布尔减 ──
result = occ.cut([(3, bp)], [(3, cyl)], removeTool=True)
if result and result[0]:
    bp = result[0][0][1]  # 取返回的新 tag
occ.synchronize()

# ── occ 创建 2D 面：闭合线框 → surface_filling ──
pts = [occ.add_point(x, y, z) for x, y, z in corner_points]
ls  = [occ.add_line(pts[i], pts[(i+1)%4]) for i in range(4)]
loop = occ.add_curve_loop(ls)
surf = occ.add_surface_filling(loop)

# ── geo.extrude 拉伸 occ 创建的面 ──
# ⚠️ extrude 只能拉伸 occ 创建的面的 tag
ext = geo.extrude([(2, surf)], 0, 0, ARM_THICK)
arm_vols = [t for d, t in ext if d == 3]

occ.synchronize()

# ── occ.fuse 融合体 ──
# ⚠️ 必须用 [(dim, tag), ...] 格式
all_parts = [(3, bp)] + [(3, v) for v in arm_vols + standoff_vols]
fused = occ.fuse(all_parts[:1], all_parts[1:])
final_tag = fused[0][0][1] if fused and fused[0] else bp

occ.synchronize()
gmsh.write("/tmp/model.step")
gmsh.finalize()
```

## 常见错误速查

| 错误 | 原因 | 解决 |
|------|------|------|
| `AttributeError: 'geo' has no attribute 'add_box'` | 在 geo 层调用了 occ 专属方法 | 全部换 occ |
| `AttributeError: 'occ' has no attribute 'add_surface'` | occ 没有 `add_plane_surface/add_surface` | 用 `add_surface_filling` |
| `AttributeError: 'occ' has no attribute 'add_extrude'` | occ 没有 extrude 方法 | 用 `geo.extrude` |
| `Exception: Invalid data for input vector of pairs` | `occ.fuse([tag], [tag])` 格式错误 | 改为 `occ.fuse([(3,tag)], [(3,tag)])` |
| mesh generate(3) 超时 | 复杂融合几何体网格化太慢 | `Mesh.CharacteristicLengthMax` 调大，或分别导出零件 |

## API 签名

```
occ.add_point(x, y, z)                                      → tag
occ.add_line(startTag, endTag)                               → tag
occ.add_circle(x, y, z, r)                                  → tag
occ.add_curve_loop(curveTags: list[int])                     → tag
occ.add_surface_filling(wireTag)                             → tag  (occ 层唯一的面创建方法)
occ.add_box(x, y, z, dx, dy, dz)                            → tag
occ.add_cylinder(x, y, z, dx, dy, dz, r)                   → tag
occ.fuse(objects: list[dimTag], tools: list[dimTag])        → (modified_tags, dimTag_pairs)
occ.cut(objects, tools, ...)                                 → 同上
geo.extrude(dimTags, dx, dy, dz)                           → [(dim, tag), ...]
geo.revolve(dimTags, dx, dy, dz, ax, ay, az, angle)      → 同上
```

## 已知可用工具

| 工具 | 可用 | 备注 |
|------|------|------|
| gmsh OCC API | ✅ | occ + geo 混合用法 |
| ezdxf | ✅ | 读 DXF/DWG |
| svgwrite + rsvg-convert | ✅ | DXF→SVG→PNG |
| PIL (Pillow) | ✅ | 图像处理 |
| inkscape | ❌ | 无头环境 |
| cairosvg | ❌ | 不可用 |
| gmsh fltk/OpenGL | ❌ | 无头环境截图 |
