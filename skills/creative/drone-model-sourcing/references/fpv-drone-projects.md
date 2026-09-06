# FPV Drone Frame Projects Reference

## Team BlackSheep (TBS) Source Series

### TBS Source One v6 (5" Freestyle)
- **Repo:** `tbs-trappy/source_one` — 607 stars
- **Specs (from official README + DXF):**
  - Wheelbase: 230mm (5")
  - Top plate: 2mm | Bottom plate: 4mm | Camera plate: 4mm | Arm: 2mm
  - Single arm: **370mm × 25mm × 25mm**, weight 60g
  - Frame total weight: ~700g (carbon fiber)
  - Motor mount pattern: standard 5" (16×19mm 4×M3)
  - Version: V6 (2025) — major redesign
- **Files in repo:**
  - `SO1-V6-skate.stl` — main frame body (~6MB)
  - `So1-V6-2025-AUG-19.dxf` — full frame drawing (~95MB)
  - `So1-V6-2025-AUG-19.dwg` — AutoCAD source (~42MB)
  - `SO1-V6-*-mount.stl` — camera/antenna mounts
- **Access:** `https://github.com/tbs-trappy/source_one`

### TBS Source Micro v0.1 (Whoop 120mm)
- **Repo:** `ps915/source_micro` — 38 stars
- **Specs (from official README + DXF):**
  - Wheelbase: 120mm
  - Top/bottom plate: **2.5mm**
  - Standoff height: **20mm**
  - Stack mount: **20×20mm & 16×16mm**
  - Frame weight: 19g
  - Hardware: 8× M2×8mm button head, 4× M2 20mm standoff
- **Files in repo:**
  - `SourceMicro_v0.1_top_plate_2.5mm.dxf` — top plate geometry
  - `SourceMicro_v0.1_bottom_plate_2.5mm.dxf` — bottom plate
  - `SourceMicro_v0.1_BOM.pdf` — bill of materials
  - `SourceMicro_v0.1_tiny_cam_combo.stl` — camera mount
- **DXF extracted geometry (verified from actual file):**
  - Main body (24-vertex polyline): 79.5mm wide × 26mm tall
  - Center opening: ~15mm × 12mm (for stack)
  - Motor holes: 4× M2 (r=1mm) at ±35mm, ±150mm offset (45° positions)
  - Center hole: r=2mm
  - Stack slots: 4× 2mm × 8mm rectangles at ±18mm, ±292mm
- **Access:** `https://github.com/ps915/source_micro`

### TBS Source X (X-Class Giant)
- **Repo:** `ps915/source_x` — 43 stars
- **Specs (from official README):**
  - MTM distance: 800mm
  - Frame weight: 700g
  - Bottom plate: 4mm | Top plate: 2mm | Motor plates: 2mm | Camera plate: 4mm
  - Single arm: **370mm × 25mm × 25mm**, weight 60g
- **Access:** `https://github.com/ps915/source_x`

## Standard Dimensions

### 5" Racing/Freestyle
| Parameter | Value |
|-----------|-------|
| Wheelbase | 220-235mm |
| Arm | 10-15mm wide, 3-5mm thick |
| Body | 120-150mm × 40-60mm |
| Motor PCD | 16mm (4×M3) |
| Motor OD | 22-28mm |
| Stack height | 28-36mm |
| Stack mount | 30.5×30.5mm |

### Tiny Whoop / 2"
| Parameter | Value |
|-----------|-------|
| Wheelbase | 65-75mm |
| Arm | 4-6mm wide, 2-3mm thick |
| Body | 28-35mm × 25-30mm |
| Motor PCD | 6-9mm |
| Motor OD | 14-20mm (0802/1102) |
| Prop | 50-55mm (2") |

### 3" Cinewhoop
| Parameter | Value |
|-----------|-------|
| Wheelbase | 100-115mm |
| Body | 70-90mm |
| Motor | 13-16mm OD |
| Prop | 75-80mm (3") |
| Stack mount | 20×20mm |

## Real DXF Data — TBS Source Micro v0.1

From `SourceMicro_v0.1_top_plate_2.5mm.dxf`:

**Main body** (24-vertex polyline):
- X: -37.5 ~ 42.0mm → width 79.5mm
- Y: -303.0 ~ -277.0mm → height 26mm
- Has arc bulges (rounded corners)

**Center opening** (14 vertices):
- X: -4 ~ 11mm → 15mm
- Y: -296 ~ -284mm → 12mm

**Motor holes**: 4× M2 (r=1mm) at ±35mm, ±150mm offset (45° positions)
**Center hole**: r=2mm
**Stack slots**: 4× 2×8mm rectangles

## Motor Specs

### 5" (2306/2207/2308)
| | |
|---|---|
| Stator | 22-23mm × 6-8mm |
| OD | 27-30mm |
| Shaft | 5mm |
| Mount | 16×19mm 4×M3 |

### Whoop (0802/1102/1103)
| | |
|---|---|
| Stator | 8-11mm × 2-3mm |
| OD | 14-20mm |
| Shaft | 1.5-2mm |
| Mount | 6-9mm PCD 4×M2 |

## Prop Specs

| Class | Diameter | Hub radius | Shaft |
|-------|----------|------------|-------|
| 5" | 127-130mm | 6-8mm | M5×5mm |
| 3" | 75-80mm | 4-5mm | M5 or press |
| 2" | 50-55mm | 3-4mm | T-mount |
