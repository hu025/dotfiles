#!/usr/bin/env python3
"""
5-inch FPV Racing Drone Frame — TBS Source One v6 Spec
WHEELBASE=230mm | ARM=4mm碳板 | 25mm宽臂 | 5寸桨

用法: python3 build_source_one.py
输出: STEP → ~/.hermes/drone-models/STEP/SourceOne_5inch_v1.step
      STL  → ~/.hermes/drone-models/STL/SourceOne_5inch_v1.stl
"""
import math, os, gmsh, sys

# ── 规格（基于 TBS Source One v6 实测）─────────────────────────
WB      = 230.0   # 轴距 mm
ARM_W   = 25.0    # 臂宽 mm
ARM_T   = 4.0     # 臂厚 mm（底板碳纤维）
PL_W    = 150.0   # 板宽 mm
PL_D    = 120.0   # 板深 mm
PL_T    = 4.0     # 底板厚 mm
TP_T    = 2.0     # 顶板厚 mm
MHOLE_R = 16.0    # 电机安装孔半径 mm
FC_SP   = 30.5    # 飞控孔距 mm
SCR_R   = 1.6     # 螺丝孔半径 mm
CAM_R   = 12.0    # 摄像头孔半径 mm
ST_R    = 2.0     # 支撑柱半径 mm
ST_H    = 20.0    # 支撑柱高度 mm
MB_H    = 8.0     # 电机外转子高度 mm
MB_R    = 18.0    # 电机外转子半径 mm
ARM_IN  = 10.0    # 臂内侧半径 mm

def build():
    gmsh.initialize(sys.argv)
    gmsh.model.add("SourceOne_5inch_v1")
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", 1.5)

    occ = gmsh.model.occ
    geo = gmsh.model.geo
    occ.synchronize()

    # ── 1. BOTTOM PLATE (150x120x4mm) ────────────────────────────
    bp = occ.add_box(-PL_W/2, -PL_D/2, 0.0, PL_W, PL_D, PL_T)

    # 4个电机安装孔（穿透整个板）
    motor_cuts = []
    for i in range(4):
        a = math.pi/4 + i*math.pi/2
        mx, my = WB/2*math.cos(a), WB/2*math.sin(a)
        motor_cuts.append(occ.add_cylinder(mx, my, -1, 0, 0, PL_T+2, MHOLE_R))

    # 4个飞控螺丝孔
    fc_cuts = []
    for sx in [-1.0, 1.0]:
        for sy in [-1.0, 1.0]:
            fc_cuts.append(occ.add_cylinder(sx*FC_SP/2, sy*FC_SP/2, -1, 0, 0, PL_T+2, SCR_R))

    occ.synchronize()

    all_cuts = [(3, c) for c in motor_cuts + fc_cuts]
    res = occ.cut([(3, bp)], all_cuts, removeTool=True)
    if res and res[0]:
        bp = res[0][0][1]

    occ.synchronize()

    # ── 2. ARMS — 4条矩形斜臂（面 → 拉伸为体）────────────────────
    arm_vols = []

    for i in range(4):
        a = math.pi/4 + i*math.pi/2
        dx, dy = math.cos(a), math.sin(a)
        pvx, pvy = -dy, dx

        hw = ARM_W / 2.0
        ro = WB/2 - MHOLE_R - 2.0   # 外端
        ri = ARM_IN                    # 内侧半径

        p1x = ro*dx + hw*pvx;  p1y = ro*dy + hw*pvy
        p2x = ro*dx - hw*pvx;  p2y = ro*dy - hw*pvy
        p3x = ri*dx  - hw*pvx;  p3y = ri*dy  - hw*pvy
        p4x = ri*dx  + hw*pvx;  p4y = ri*dy  + hw*pvy

        pts = [occ.add_point(p1x, p1y, 0),
               occ.add_point(p2x, p2y, 0),
               occ.add_point(p3x, p3y, 0),
               occ.add_point(p4x, p4y, 0)]
        ls  = [occ.add_line(pts[j], pts[(j+1)%4]) for j in range(4)]
        loop = occ.add_curve_loop(ls)
        surf = occ.add_surface_filling(loop)

        ext = geo.extrude([(2, surf)], 0, 0, ARM_T)
        for d, t in ext:
            if d == 3:
                arm_vols.append(t)

    occ.synchronize()

    # ── 3. TOP PLATE (150x120x2mm) ───────────────────────────────
    tp_z = ARM_T + TP_T
    tp_pts = [occ.add_point(-PL_W/2, -PL_D/2, tp_z),
              occ.add_point( PL_W/2, -PL_D/2, tp_z),
              occ.add_point( PL_W/2,  PL_D/2, tp_z),
              occ.add_point(-PL_W/2,  PL_D/2, tp_z)]
    tp_ls = [occ.add_line(tp_pts[j], tp_pts[(j+1)%4]) for j in range(4)]
    tp_loop = occ.add_curve_loop(tp_ls)
    tp_surf = occ.add_surface_filling(tp_loop)
    occ.synchronize()

    # ── 4. STANDOFFF (4x M2x20mm) ───────────────────────────────
    standoff_vols = []
    for sx, sy in [(-FC_SP/2,-FC_SP/2),(FC_SP/2,-FC_SP/2),
                    (-FC_SP/2,FC_SP/2),(FC_SP/2,FC_SP/2)]:
        c = occ.add_cylinder(sx, sy, ARM_T, 0, 0, ST_H, ST_R)
        standoff_vols.append(c)
    occ.synchronize()

    # ── 5. MOTOR BELLS (4x 简化圆柱) ────────────────────────────
    motor_vols = []
    for i in range(4):
        a = math.pi/4 + i*math.pi/2
        mx, my = WB/2*math.cos(a), WB/2*math.sin(a)
        c = occ.add_cylinder(mx, my, 0.0, 0.0, 0.0, MB_H, MB_R)
        motor_vols.append(c)
    occ.synchronize()

    # ── 6. ASSEMBLE (occ.fuse) ───────────────────────────────────
    all_parts = [(3, bp)] + [(3, v) for v in arm_vols + standoff_vols + motor_vols]
    fused = occ.fuse(all_parts[:1], all_parts[1:])
    final_tag = fused[0][0][1] if fused and fused[0] else bp
    occ.synchronize()

    # ── 7. MESH + EXPORT ─────────────────────────────────────────
    print("Meshing...")
    gmsh.model.mesh.generate(3)

    base = os.path.expanduser("~/.hermes/drone-models")
    os.makedirs(f"{base}/STEP", exist_ok=True)
    os.makedirs(f"{base}/STL", exist_ok=True)

    step_path = f"{base}/STEP/SourceOne_5inch_v1.step"
    stl_path  = f"{base}/STL/SourceOne_5inch_v1.stl"

    gmsh.write(step_path)
    sz1 = os.path.getsize(step_path)
    print(f"STEP → {step_path}  ({sz1//1024}KB)")

    gmsh.model.mesh.generate(2)
    gmsh.write(stl_path)
    sz2 = os.path.getsize(stl_path)
    print(f"STL  → {stl_path}  ({sz2//1024}KB)")

    gmsh.finalize()
    print("Done!")

if __name__ == "__main__":
    build()
