# DXF Extraction Reference

## Quick Extract Script

```python
import re

with open('/tmp/file.dxf') as f:
    content = f.read()

# Split into entities
entities_raw = re.split(r'(?=LWPOLYLINE|CIRCLE|ENDSEC)', content)
entities_raw.pop()  # remove trailing ENDSEC

all_entities = []
for ent in entities_raw:
    if 'LWPOLYLINE' in ent and 'AcDbPolyline' in ent:
        lines = ent.strip().split('\n')
        i = 0
        pts = []
        bulges = []
        while i < len(lines):
            l = lines[i].strip()
            if l == '10':
                x = float(lines[i+1].strip())
                if i+2 < len(lines) and lines[i+2].strip() == '20':
                    y = float(lines[i+3].strip())
                    pts.append((x, y))
                    i += 4
                    continue
            elif l == '42':
                bulges.append(float(lines[i+1].strip()))
            i += 1
        if pts:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            all_entities.append({
                'type': 'LWPOLYLINE', 'pts': pts, 'bulges': bulges,
                'x_min': min(xs), 'x_max': max(xs),
                'y_min': min(ys), 'y_max': max(ys),
                'w': max(xs)-min(xs), 'h': max(ys)-min(ys)
            })
    elif 'CIRCLE' in ent and 'AcDbCircle' in ent:
        lines = ent.strip().split('\n')
        i = 0
        cx = cy = cr = None
        while i < len(lines):
            l = lines[i].strip()
            if l == '10': cx = float(lines[i+1].strip())
            elif l == '20': cy = float(lines[i+1].strip())
            elif l == '40': cr = float(lines[i+1].strip())
            i += 1
        if cx is not None:
            all_entities.append({'type': 'CIRCLE', 'cx': cx, 'cy': cy, 'r': cr})

# Sort by size
def area(e):
    if e['type'] == 'LWPOLYLINE':
        return e['w'] * e['h']
    return 0

for e in sorted(all_entities, key=area, reverse=True):
    if e['type'] == 'LWPOLYLINE':
        print(f"Poly: {len(e['pts'])} pts | X: {e['x_min']:.1f}~{e['x_max']:.1f} ({e['w']:.1f}) | Y: {e['y_min']:.1f}~{e['y_max']:.1f} ({e['h']:.1f})")
    else:
        print(f"CIRCLE: ({e['cx']:.1f},{e['cy']:.1f}) r={e['r']:.1f}")
```

## Key DXF Group Codes

| Group | Meaning | Notes |
|-------|---------|-------|
| 0 | Entity type | LWPOLYLINE, CIRCLE, LINE, ARC |
| 5 | Handle | Unique entity ID |
| 8 | Layer name | |
| 10 | X coordinate | Also: center X for CIRCLE/ARC |
| 20 | Y coordinate | Also: center Y |
| 30 | Z coordinate | |
| 40 | Radius | Also: start angle for ARC |
| 41 | Second radius | For ellipse |
| 42 | Bulge factor | Arc segment in LWPOLYLINE; tan(θ/4) |
| 70 | Flags | Polyline: 1=closed, 4=spline, 8=3Dpoly |
| 90 | Vertex count | Number of vertices |

## Bulge Interpretation

Bulge = tan(θ/4) where θ is the included arc angle.

| Bulge | Arc Angle |
|-------|-----------|
| 0.4142 | 90° |
| 1.0 | 180° |
| -0.4142 | -90° |

To convert bulge to arc midpoint:
```python
import math
def bulge_to_angle(b):
    return math.degrees(4 * math.atan(b))
```

## Scale Factor

DXF files from CAD software are often in mm with no explicit scaling. Check `$INSUNITS`:
- 4 = Millimeters
- 6 = Inches
- 1 = Inches (older format)

If units don't match, scale coordinates by appropriate factor.
