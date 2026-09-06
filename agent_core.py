#!/usr/bin/env python3
"""
自主进化核心引擎
Autonomous Improvement Core Engine
每分钟运行一次心跳，每天生成日报，每周生成架构审查
"""

import json
import os
import sys
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

SELF_DIR = Path.home() / ".hermes" / "self-improvement"
BASE_DIR = Path.home() / ".hermes"
LOGS_DIR = SELF_DIR / "logs"
REPORTS_DAILY = SELF_DIR / "reports" / "daily"
REPORTS_WEEKLY = SELF_DIR / "reports" / "weekly"
BENCHMARK_DIR = SELF_DIR / "benchmarks"
SKILLS_SUGGESTED = SELF_DIR / "skills" / "suggested"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DAILY.mkdir(parents=True, exist_ok=True)
REPORTS_WEEKLY.mkdir(parents=True, exist_ok=True)
BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)
SKILLS_SUGGESTED.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOGS_DIR / "heartbeat.log"

def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def read_json(path: Path, default):
    try:
        return json.loads(path.read_text())
    except:
        return default

def write_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

# ── 心跳：每分钟记录活跃状态 ──────────────────────────────────
def heartbeat():
    now = datetime.now()
    heartbeat_file = LOGS_DIR / "last_heartbeat.json"
    data = read_json(heartbeat_file, {})
    data["last_heartbeat"] = now.isoformat()
    data["count"] = data.get("count", 0) + 1
    write_json(heartbeat_file, data)

# ── 系统状态采样 ─────────────────────────────────────────────
def sample_system_state() -> dict:
    """采集当前系统关键指标"""
    state = {"timestamp": datetime.now().isoformat()}

    # CPU / 内存
    try:
        out = subprocess.check_output(
            "python3 -c \"import psutil; p=psutil.Process(); print(json.dumps({'cpu':p.cpu_percent(),'mem_mb':p.memory_info().rss//1024//1024}))\"" if False else "echo '{}'",
            shell=True, timeout=5
        )
    except:
        pass

    # 磁盘
    try:
        out = subprocess.check_output("df -h /home/saber --output=avail,size,pcent | tail -1", shell=True, timeout=5, text=True)
        parts = out.strip().split()
        if len(parts) == 3:
            state["disk_avail_gb"] = parts[0]
            state["disk_total_gb"] = parts[1]
            state["disk_used_pct"] = parts[2]
    except:
        pass

    # 进程健康
    for name, port, pidfile in [
        ("hermes-gateway", 8642, Path.home() / ".hermes" / "hermes-agent" / "gateway.pid"),
        ("xiaozhi-server", 8080, Path.home() / ".hermes" / "xiaozhi-server.pid"),
        ("openclaw", 18888, Path.home() / ".hermes" / "openclaw.pid"),
    ]:
        try:
            out = subprocess.check_output(f"ss -tlnp 2>/dev/null | grep -q ':{port}' && echo UP || echo DOWN",
                                          shell=True, timeout=5, text=True)
            state[f"{name}_status"] = "UP" if "UP" in out else "DOWN"
        except:
            state[f"{name}_status"] = "UNKNOWN"

    # ESP32 串口（静默跳过不存在的设备）
    for dev in ["/dev/ttyACM0", "/dev/ttyUSB0"]:
        if not os.path.exists(dev):
            continue
        try:
            out = subprocess.check_output(f"python3 -c \"import serial; s=serial.Serial('{dev}',9600,timeout=1); print('OK')\"",
                                           shell=True, timeout=2, text=True)
            state["esp32_uart"] = dev
            break
        except:
            pass

    return state

# ── 今日成就记录 ─────────────────────────────────────────────
def record_success(action: str, detail: str = ""):
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_DIR / f"success_{today}.json"
    data = read_json(log_file, [])
    data.append({"time": datetime.now().isoformat(), "action": action, "detail": detail})
    write_json(log_file, data)

def record_failure(action: str, error: str, detail: str = ""):
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_DIR / f"failure_{today}.json"
    data = read_json(log_file, [])
    data.append({"time": datetime.now().isoformat(), "action": action, "error": str(error)[:200], "detail": detail})
    write_json(log_file, data)

def record_learning(what: str, source: str, outcome: str):
    """记录学习到的新知识"""
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_DIR / f"learning_{today}.json"
    data = read_json(log_file, [])
    data.append({"time": datetime.now().isoformat(), "what": what, "source": source, "outcome": outcome})
    write_json(log_file, data)

def record_improvement(area: str, what: str, result: str):
    """记录自我改进"""
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_DIR / f"improvements_{today}.json"
    data = read_json(log_file, [])
    data.append({"time": datetime.now().isoformat(), "area": area, "what": what, "result": result})
    write_json(log_file, data)

# ── 每日报告 ─────────────────────────────────────────────────
def generate_daily_report() -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    report_path = REPORTS_DAILY / f"daily_{today}.md"

    success_data = read_json(LOGS_DIR / f"success_{today}.json", [])
    failure_data = read_json(LOGS_DIR / f"failure_{today}.json", [])
    learning_data = read_json(LOGS_DIR / f"learning_{today}.json", [])
    improvement_data = read_json(LOGS_DIR / f"improvements_{today}.json", [])
    system_state = sample_system_state()

    # 计算明日改进项
    tomorrow_items = []
    if failure_data:
        top_failures = [f["action"] for f in failure_data[-3:]]
        tomorrow_items.append(f"复盘今日失败：{', '.join(top_failures)}")
    tomorrow_items.append("验证核心服务健康状态")
    tomorrow_items.append("检查记忆库是否有待更新的信息")

    report = f"""# 每日自我改进报告 · {today}

## 📊 系统状态

| 指标 | 值 |
|------|-----|
| 时间 | {datetime.now().strftime('%H:%M:%S')} |
| 磁盘剩余 | {system_state.get('disk_avail_gb','N/A')} / {system_state.get('disk_total_gb','N/A')} ({system_state.get('disk_used_pct','N/A')}已用) |
| Hermes Gateway | {system_state.get('hermes-gateway_status','UNKNOWN')} |
| xiaozhi-server | {system_state.get('xiaozhi-server_status','UNKNOWN')} |
| OpenClaw | {system_state.get('openclaw_status','UNKNOWN')} |
| ESP32 串口 | {system_state.get('esp32_uart','未连接')} |

---

## ✅ 今日成就（{len(success_data)}项）

"""
    if success_data:
        for s in success_data[-10:]:
            ts = datetime.fromisoformat(s["time"]).strftime("%H:%M")
            report += f"- **{ts}** {s['action']}"
            if s.get("detail"): report += f" — {s['detail']}"
            report += "\n"
    else:
        report += "- 暂无记录（可能是首次运行或自动心跳采集）\n"

    report += f"\n---\n\n## ❌ 今日失败（{len(failure_data)}项）\n\n"
    if failure_data:
        for f in failure_data[-5:]:
            ts = datetime.fromisoformat(f["time"]).strftime("%H:%M")
            report += f"- **{ts}** {f['action']}: {f.get('error','?')[:80]}\n"
    else:
        report += "- 无失败记录 ✓\n"

    report += f"\n---\n\n## 📚 今日学习\n\n"
    if learning_data:
        for l in learning_data[-5:]:
            report += f"- [{l['source']}] {l['what']} → {l['outcome']}\n"
    else:
        report += "- 暂无记录\n"

    report += f"\n---\n\n## 🔧 今日改进\n\n"
    if improvement_data:
        for i in improvement_data[-5:]:
            report += f"- **[{i['area']}]** {i['what']} → {i['result']}\n"
    else:
        report += "- 暂无记录\n"

    report += f"\n---\n\n## 🎯 明日改进计划\n\n"
    for idx, item in enumerate(tomorrow_items, 1):
        report += f"{idx}. {item}\n"

    report += f"\n---\n\n*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

    report_path.write_text(report, encoding="utf-8")
    log(f"日报已生成：{report_path}")
    return report_path

# ── 每周架构审查报告 ─────────────────────────────────────────
def generate_weekly_report() -> str:
    today = datetime.now()
    week_start = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
    week_end = today.strftime("%Y-%m-%d")
    report_path = REPORTS_WEEKLY / f"weekly_{week_end}.md"

    # 汇总本周每日数据
    total_success = 0
    total_failure = 0
    all_success = []
    all_failures = []
    all_learning = []
    all_improvements = []

    for i in range(7):
        day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        s = read_json(LOGS_DIR / f"success_{day}.json", [])
        f = read_json(LOGS_DIR / f"failure_{day}.json", [])
        l = read_json(LOGS_DIR / f"learning_{day}.json", [])
        imp = read_json(LOGS_DIR / f"improvements_{day}.json", [])
        total_success += len(s)
        total_failure += len(f)
        all_success.extend(s)
        all_failures.extend(f)
        all_learning.extend(l)
        all_improvements.extend(imp)

    # 统计高频失败
    from collections import Counter
    failure_counter = Counter([f["action"] for f in all_failures])
    top_failures = failure_counter.most_common(5)

    # 统计高频成功
    success_counter = Counter([s["action"] for s in all_success])
    top_successes = success_counter.most_common(5)

    # 下周计划（基于本周发现的问题生成）
    next_week_plan = []
    if top_failures:
        next_week_plan.append(f"解决最高频失败 Top3：{', '.join([a for a,_ in top_failures[:3]])}")
    next_week_plan.append("验证技能库是否有更新需求")
    next_week_plan.append("检查工具链依赖是否有安全更新")
    next_week_plan.append("审视记忆库，去除过时信息")

    report = f"""# 每周架构审查报告 · {week_start} ~ {week_end}

## 📈 本周统计

| 指标 | 数值 |
|------|------|
| 总成功 | {total_success} |
| 总失败 | {total_failure} |
| 成功率 | {"{:.0%}".format(total_success/(total_success+total_failure+1))} |
| 新学习 | {len(all_learning)} |
| 自我改进 | {len(all_improvements)} |

---

## 🏆 Top 成功类型

"""
    for action, count in top_successes[:5]:
        report += f"- {action} × {count}\n"

    report += "\n## 🔴 Top 失败类型\n\n"
    if top_failures:
        for action, count in top_failures:
            report += f"- {action} × {count}\n"
    else:
        report += "- 无失败 ✓\n"

    report += "\n## 📚 本周学习汇总\n\n"
    if all_learning:
        seen = set()
        for l in all_learning:
            key = l["what"]
            if key not in seen:
                report += f"- [{l['source']}] {l['what']} → {l['outcome']}\n"
                seen.add(key)
    else:
        report += "- 无记录\n"

    report += "\n## 🔧 本周改进汇总\n\n"
    if all_improvements:
        areas = Counter([i["area"] for i in all_improvements])
        for area, count in areas.most_common():
            items = [i for i in all_improvements if i["area"] == area]
            report += f"\n### {area} ({count}项)\n"
            for i in items[-3:]:
                report += f"- {i['what']}\n"
    else:
        report += "- 无记录\n"

    report += "\n## 🏗️ 下周优化计划\n\n"
    for idx, item in enumerate(next_week_plan, 1):
        report += f"{idx}. {item}\n"

    report += f"\n---\n\n*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

    report_path.write_text(report, encoding="utf-8")
    log(f"周报已生成：{report_path}")
    return report_path

# ── 主入口 ───────────────────────────────────────────────────
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "heartbeat"

    if mode == "heartbeat":
        heartbeat()
    elif mode == "daily":
        generate_daily_report()
    elif mode == "weekly":
        generate_weekly_report()
    elif mode == "success":
        record_success(sys.argv[2] if len(sys.argv)>2 else "unknown", sys.argv[3] if len(sys.argv)>3 else "")
    elif mode == "failure":
        record_failure(sys.argv[2] if len(sys.argv)>2 else "unknown", sys.argv[3] if len(sys.argv)>3 else "")
    elif mode == "learning":
        record_learning(sys.argv[2] if len(sys.argv)>2 else "", sys.argv[3] if len(sys.argv)>3 else "", sys.argv[4] if len(sys.argv)>4 else "")
    elif mode == "improve":
        record_improvement(sys.argv[2] if len(sys.argv)>2 else "", sys.argv[3] if len(sys.argv)>3 else "", sys.argv[4] if len(sys.argv)>4 else "")
    elif mode == "status":
        print(json.dumps(sample_system_state(), ensure_ascii=False, indent=2))
    else:
        print(f"用法: {sys.argv[0]} [heartbeat|daily|weekly|success|failure|learning|improve|status]")
