# gmsh OCC API Reference

## Environment Setup

gmsh SDK is installed in the Hermes venv:
```python
import gmsh
gmsh.initialize()
gmsh.model.add("name")
# ... build geometry ...
gmsh.write("/tmp/out.step")
gmsh.finalize()
```

## Common Primitives

### Box (rectangular solid)
```python
gmsh.model.occ.addBox(cx, cy, cz, dx, dy, dz, tag=t)
# cx,cy,cz = corner coordinate (minimum)
# dx,dy,dz = dimensions in x,y,z
```

### Cylinder
```python
gmsh.model.occ.addCylinder(cx, cy, cz, dx, dy, dz, r, tag=t)
# cx,cy,cz = center of base circle
# dx,dy,dz = axis direction and length
# r = radius
```

### Sphere
```python
gmsh.model.occ.addSphere(cx, cy, cz, r, tag=t)
```

### Torus
```python
gmsh.model.occ.addTorus(cx, cy, cz, r1, r2, tag=t)
# r1 = major radius (center of tube)
# r2 = minor radius (tube radius)
```

### Cone
```python
gmsh.model.occ.addCone(cx, cy, cz, dx, dy, dz, r1, r2, tag=t)
# r1 = bottom radius, r2 = top radius (0 = point)
```

### Boolean Operations
```python
# Fragment (merge with tagging)
gmsh.model.occ.fragment([(3, tag1)], [(3, tag2)], ...)

# Cut (subtract)
gmsh.model.occ.cut([(3, tag_target)], [(3, tag_tool)], removeTool=True)

# Fuse (union)
gmsh.model.occ.fuse([(3, tag_a)], [(3, tag_b)], ...)

# Common (intersection)
gmsh.model.occ.common([(3, tag_a)], [(3, tag_b)])
```

## STEP Export

```python
gmsh.model.occ.synchronize()
gmsh.model.occ.removeAllDuplicates()
gmsh.write("/tmp/out.step")
```

## Tag Convention

Use a running counter starting at `t=1`:
```python
t = 1
gmsh.model.occ.addBox(..., tag=t); t += 1
gmsh.model.occ.addCylinder(..., tag=t); t += 1
```

Dimension tags `(dim, tag)` where dim=3 for solids.

## Importing STEP

```python
gmsh.open("/tmp/in.step")
print(gmsh.model.getEntities())
```

## Useful gmsh Options

```python
gmsh.option.setNumber("General.Terminal", 0)  # Suppress verbose output
gmsh.option.setNumber("Mesh.Algorithm", 6)       # 2D mesh algorithm
```

## Drone Geometry Template

```python
import gmsh, math
gmsh.initialize()
gmsh.model.add("drone")

WHEELBASE = 230.0; ARM_W = 12.0; ARM_T = 4.0
BODY_L = 140.0; BODY_W = 55.0
PLATE_T = 3.0; STACK_H = 28.0
MOTOR_R = 13.0; MOTOR_H = 22.0
PROP_R = 63.5; PROP_H = 2.5

t = 1

# Motor positions (X-config, 45° offset)
motor_pos = []
for q in range(4):
    ang = math.radians(q * 90 + 45)
    mx = (WHEELBASE / 2) * math.cos(ang)
    my = (WHEELBASE / 2) * math.sin(ang)
    motor_pos.append((mx, my))

# Top plate
gmsh.model.occ.addBox(-BODY_W/2, -BODY_L/2, 0, BODY_W, BODY_L, PLATE_T, tag=t); t+=1

# Bottom plate
gmsh.model.occ.addBox(-BODY_W/2, -BODY_L/2, -(PLATE_T+STACK_H), BODY_W, BODY_L, PLATE_T, tag=t); t+=1

# Arms
for q in range(4):
    ang = math.radians(q * 90 + 45)
    arm_len = WHEELBASE / 2 - 35
    mid_r = WHEELBASE / 2 - arm_len / 2
    cx = mid_r * math.cos(ang)
    cy = mid_r * math.sin(ang)
    px = -math.sin(ang); py = math.cos(ang)
    gmsh.model.occ.addBox(
        cx - arm_len/2*math.cos(ang) - ARM_W/2*px,
        cy - arm_len/2*math.sin(ang) - ARM_W/2*py,
        -ARM_T/2, arm_len, ARM_W, ARM_T, tag=t
    ); t+=1

# Motors
for mx, my in motor_pos:
    gmsh.model.occ.addCylinder(mx, my, PLATE_T, 0, 0, MOTOR_H, MOTOR_R, tag=t); t+=1
    # Shaft
    gmsh.model.occ.addCylinder(mx, my, PLATE_T+MOTOR_H, 0, 0, 10, 2, tag=t); t+=1

# Props
for mx, my in motor_pos:
    z_base = PLATE_T + MOTOR_H + 12
    for blade in range(3):  # 3-blade for 5"
        ba = math.radians(blade * 120)
        bx = mx + PROP_R/2*0.68*math.cos(ba)
        by = my + PROP_R/2*0.68*math.sin(ba)
        gmsh.model.occ.addBox(bx-PROP_R*0.38, by-5, z_base-1.5, PROP_R*0.76, 10, PROP_H, tag=t); t+=1
    # Hub
    gmsh.model.occ.addCylinder(mx, my, z_base-3, 0, 0, 8, 6, tag=t); t+=1

gmsh.model.occ.synchronize()
gmsh.model.occ.removeAllDuplicates()
gmsh.write("/tmp/drone.step")
gmsh.finalize()
```

## Limitations

- `addBox` creates axis-aligned boxes; for rotated arms use coordinate transform
- Complex surfaces (propeller airfoil, ergonomic curves) require subdivision into primitives
- OCC boolean operations can fail on coincident surfaces — use `removeAllDuplicates()` after sync
- Very large models (>50K entities) can cause gmsh to hang on fragment — break into sub-assemblies
