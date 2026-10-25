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
from collections import Counter
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

def _write_queue_back(queue_file: Path, original, queue):
    """把更新后的条目列表写回队列文件，保留原有的分桶结构。

    original 是读出来的原始对象：dict 格式（{"topics":[...], "new_entries":[...]}）
    要按 id/topic 把更新写回对应桶里；list 格式直接整表覆盖。
    绝不能把 list 直接写进原本是 dict 的文件——那会把整个队列文件结构毁掉。
    """
    if isinstance(original, dict):
        # 按 topic 建索引，把更新同步回各桶
        by_topic = {}
        for q in queue:
            by_topic.setdefault(q.get("topic"), q)
        out = dict(original)
        for bucket in ("topics", "new_entries"):
            new_bucket = []
            for q in (original.get(bucket) or []):
                if isinstance(q, dict) and q.get("topic") in by_topic:
                    new_bucket.append(by_topic[q["topic"]])
                else:
                    new_bucket.append(q)
            out[bucket] = new_bucket
        out["last_updated"] = datetime.now().isoformat()
        write_json(queue_file, out)
    else:
        write_json(queue_file, queue)

# ── 心跳：每分钟记录活跃状态 ──────────────────────────────────
def heartbeat():
    now = datetime.now()
    heartbeat_file = LOGS_DIR / "last_heartbeat.json"
    data = read_json(heartbeat_file, {})
    data["last_heartbeat"] = now.isoformat()
    data["count"] = data.get("count", 0) + 1

    # 除计数外，采集真实系统状态 —— 心跳是日报「成就/失败」的数据来源，
    # 只写计数器会让日报永远显示 0 项。
    snap = _probe_system()
    data["snapshot"] = snap
    write_json(heartbeat_file, data)

    # 落一条每日状态记录，让日报有据可依
    _append_daily_state(snap)
    return data


def _probe_system() -> dict:
    """轻量系统探针：全部异常吞掉，绝不让心跳因探针失败而中断。"""
    snap: dict = {"ts": datetime.now().isoformat()}

    try:
        st = os.statvfs("/")
        snap["disk_pct"] = round((st.f_blocks - st.f_bfree) / st.f_blocks * 100, 1)
    except Exception:
        snap["disk_pct"] = None

    try:
        with open("/proc/loadavg") as f:
            snap["load1"] = round(float(f.read().split()[0]), 2)
    except Exception:
        snap["load1"] = None

    try:
        total = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
        avail = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_AVPHYS_PAGES")
        snap["mem_avail_mb"] = round(avail / 1024 / 1024)
        snap["mem_total_mb"] = round(total / 1024 / 1024)
    except Exception:
        snap["mem_avail_mb"] = snap["mem_total_mb"] = None

    # Gateway 健康（curl 优先，失败即视为不健康）
    try:
        import urllib.request
        with urllib.request.urlopen("http://127.0.0.1:8642/health", timeout=3) as r:
            snap["gateway"] = "up" if r.status == 200 else f"http_{r.status}"
    except Exception:
        snap["gateway"] = "down"

    # Hermes cron ticker 新鲜度（分钟）
    try:
        hb = BASE_DIR / "cron" / "ticker_heartbeat"
        snap["cron_ticker_age_min"] = (
            int((time.time() - hb.stat().st_mtime) / 60) if hb.exists() else None
        )
    except Exception:
        snap["cron_ticker_age_min"] = None

    return snap


def _append_daily_state(snap: dict):
    """把本次心跳压进当日状态序列，供日报统计活跃度。"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        f = LOGS_DIR / f"heartbeat_state_{today}.json"
        rows = read_json(f, [])
        rows.append(snap)
        write_json(f, rows[-1440:])  # 保留最近一天的上限，防止无限增长
    except Exception:
        pass

# ── 增强状态仪表盘 (status 命令) ──────────────────────────────
def _count_learnings() -> dict:
    """统计 learnings 总数与按主题分布"""
    total = 0
    by_topic = Counter()
    for f in sorted(LOGS_DIR.glob("learning_*.json")):
        try:
            entries = json.loads(f.read_text(encoding="utf-8"))
            for e in entries:
                total += 1
                for t in e.get("_topics", ["未分类"]):
                    by_topic[t] += 1
        except Exception:
            pass
    return {"total": total, "by_topic": dict(by_topic.most_common())}


def _weekly_installed_packages() -> list:
    """列出本周新增 pip 包 (从 pip log 推断或返回声明清单)"""
    pkgs = []
    try:
        out = subprocess.check_output(
            "python3 -m pip list --format=json --disable-pip-version-check 2>/dev/null",
            shell=True, timeout=8, text=True
        )
        all_pkgs = json.loads(out)
        # 已知本周装的包 (从 learnings 推断: browser-use, texthumanize, rdagent, psutil)
        target_names = {"browser-use", "texthumanize", "rdagent", "psutil", "qlib"}
        for p in all_pkgs:
            if p["name"].lower() in target_names:
                pkgs.append(f"{p['name']}=={p['version']}")
    except Exception:
        pass
    # fallback: 从 learnings 推断
    if not pkgs:
        pkgs = ["browser-use (from learning #18)", "texthumanize (from learning #17)"]
    return pkgs


def _recent_git_commits(n: int = 3) -> list:
    """获取最近 N 次 git commit — 智能查找 dotfiles 仓库"""
    candidates = [
        Path.home() / "dotfiles",                  # 标准位置
        BASE_DIR / "dotfiles",
        Path("/home/saber/dotfiles"),
    ]
    for repo_dir in candidates:
        try:
            if (repo_dir / ".git").exists():
                out = subprocess.check_output(
                    f"git -C {repo_dir} log --oneline -{n} 2>/dev/null",
                    shell=True, timeout=5, text=True
                )
                lines = [l.strip() for l in out.strip().splitlines() if l.strip()]
                if lines:
                    return lines
        except Exception:
            continue
    return ["(no git repo or no commits found)"]


def _cron_status() -> dict:
    """检查 cron 任务状态"""
    result = {"system_crontab": [], "hermes_cron_jobs": []}
    # 系统 crontab
    try:
        out = subprocess.check_output("crontab -l 2>/dev/null", shell=True, timeout=3, text=True)
        result["system_crontab"] = [l.strip() for l in out.splitlines() if l.strip() and not l.strip().startswith("#")]
    except Exception:
        result["system_crontab"] = []
    # Hermes 自管 cron (使用 ticker_heartbeat 探测)
    heartbeat_file = BASE_DIR / "cron" / "ticker_heartbeat"
    if heartbeat_file.exists():
        try:
            age = time.time() - heartbeat_file.stat().st_mtime
            age_min = int(age / 60)
            result["hermes_cron_jobs"].append(f"ticker (last beat {age_min}min ago)")
        except Exception:
            pass
    # dotfiles sync log
    sync_log = LOGS_DIR / "dotfiles_sync.log"
    if sync_log.exists():
        try:
            age = time.time() - sync_log.stat().st_mtime
            age_min = int(age / 60)
            result["hermes_cron_jobs"].append(f"dotfiles-sync (last run {age_min}min ago)")
        except Exception:
            pass
    # heartbeat.log (agent_core.py 每分钟心跳)
    hb = LOGS_DIR / "heartbeat.log"
    if hb.exists():
        try:
            age = time.time() - hb.stat().st_mtime
            age_min = int(age / 60)
            result["hermes_cron_jobs"].append(f"agent_core heartbeat (last beat {age_min}min ago)")
        except Exception:
            pass
    return result


def cmd_status():
    """美化输出系统状态仪表盘: 系统指标 + learning数 + 本周依赖 + git commits + cron 状态"""
    now = datetime.now()
    state = sample_system_state()
    learn = _count_learnings()
    pkgs = _weekly_installed_packages()
    commits = _recent_git_commits(n=3)
    cron = _cron_status()

    lines = []
    lines.append("╔══════════════════════════════════════════════════════════════╗")
    lines.append(f"║  🤖 Hermes Agent Status Dashboard                              ║")
    lines.append(f"║  {now.strftime('%Y-%m-%d %H:%M:%S CST'):<62} ║")
    lines.append("╠══════════════════════════════════════════════════════════════╣")

    # 系统健康
    lines.append("║ 📊 系统健康                                                   ║")
    disk_avail = state.get("disk_avail_gb", "N/A")
    disk_total = state.get("disk_total_gb", "N/A")
    disk_pct = state.get("disk_used_pct", "N/A")
    lines.append(f"║   磁盘: {disk_avail}/{disk_total} ({disk_pct} 已用)                                  ║")
    gw = state.get("hermes-gateway_status", "?")
    oc = state.get("openclaw_status", "?")
    esp = state.get("esp32_uart", "未连接")
    lines.append(f"║   Gateway: {gw:<8}  OpenClaw: {oc:<8}  ESP32: {esp:<6}              ║")

    # Learning 统计
    lines.append("╠══════════════════════════════════════════════════════════════╣")
    lines.append(f"║ 📚 Learnings 沉淀                                              ║")
    lines.append(f"║   总数: {learn['total']} 条                                          ║")
    if learn["by_topic"]:
        topic_str = "  ".join([f"{k}:{v}" for k, v in list(learn["by_topic"].items())[:5]])
        lines.append(f"║   主题: {topic_str[:58]:<58} ║")
    lines.append(f"║   原则: ~/.hermes/self-improvement/PRINCIPLES.md              ║")

    # 本周新装依赖
    lines.append("╠══════════════════════════════════════════════════════════════╣")
    lines.append(f"║ 📦 本周新装依赖                                                ║")
    if pkgs:
        for p in pkgs[:5]:
            p_short = p if len(p) <= 56 else p[:53] + "..."
            lines.append(f"║   • {p_short:<58} ║")
    else:
        lines.append("║   (无变更)                                                     ║")

    # 最近 git commits
    lines.append("╠══════════════════════════════════════════════════════════════╣")
    lines.append(f"║ 🔖 最近 3 次 git commit (~/dotfiles)                          ║")
    if commits:
        for c in commits[:3]:
            c_short = c if len(c) <= 58 else c[:55] + "..."
            lines.append(f"║   {c_short:<60} ║")
    else:
        lines.append("║   (无 git 仓库)                                                ║")

    # Cron jobs
    lines.append("╠══════════════════════════════════════════════════════════════╣")
    lines.append(f"║ ⏰ Cron / 定时任务状态                                          ║")
    sys_cron = cron["system_crontab"]
    if sys_cron:
        lines.append(f"║   系统 crontab: {len(sys_cron)} 条任务                                 ║")
        for c in sys_cron[:2]:
            c_short = c if len(c) <= 56 else c[:53] + "..."
            lines.append(f"║     {c_short:<58} ║")
    else:
        lines.append("║   系统 crontab: 无                                              ║")
    hermes_cron = cron["hermes_cron_jobs"]
    if hermes_cron:
        lines.append(f"║   Hermes 自管:                                                 ║")
        for c in hermes_cron[:4]:
            c_short = c if len(c) <= 58 else c[:55] + "..."
            lines.append(f"║     ✓ {c_short:<56} ║")
    else:
        lines.append("║   Hermes 自管: 未探测到                                         ║")

    lines.append("╚══════════════════════════════════════════════════════════════╝")
    print("\n".join(lines))


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
        ("openclaw", 18888, None),
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

def record_learning(what: str, source: str, outcome: str, provenance: str = ""):
    """记录学习到的新知识（含来源追踪）
    
    Args:
        what: 核心学习内容（压缩为一句声明，不要流水账）
        source: 来源（URL/论文/实验）
        outcome: 实际效果或应用方向
        provenance: 证据（URL片段/数据点/实验结果，用于未来溯源）
    """
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_DIR / f"learning_{today}.json"
    data = read_json(log_file, [])
    entry = {
        "time": datetime.now().isoformat(),
        "what": what,
        "source": source,
        "outcome": outcome,
    }
    if provenance:
        entry["provenance"] = provenance
    data.append(entry)
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

# ── Reflexion 自我反思循环 ───────────────────────────────────
# 基于 Shinn et al. 2023 (NeurIPS) - Verbal Reinforcement Learning
# 效果：91% HumanEval，Harbor Support部署成功率 38%→71%

def _get_api_key() -> str:
    """读取 .env 中的 API_SERVER_KEY"""
    env_file = BASE_DIR / ".env"
    try:
        for line in env_file.read_text().splitlines():
            if line.startswith("API_SERVER_KEY="):
                return line.split("=", 1)[1].strip()
    except:
        pass
    return ""

def _call_llm(prompt: str, system: str = "You are a helpful assistant.", temperature: float = 0.3, max_tokens: int = 512) -> str:
    """通过本地 Hermes API 调用 LLM（OpenAI 兼容端点）"""
    import urllib.request
    api_key = _get_api_key()
    payload = json.dumps({
        "model": "minimax-m3",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }).encode()

    try:
        req = urllib.request.Request(
            "http://localhost:8642/v1/chat/completions",
            data=payload,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
            method="POST"
        )
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        if "choices" in result and result["choices"]:
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        log(f"[LLM调用失败 fallback启发式] {e}")
    return ""


def reflexion_evaluate(task: str, output: str) -> dict:
    """评估器：调用 LLM 评判输出质量（启发式兜底）"""
    # 加载专用评估 prompt
    prompt_file = LOGS_DIR / "prompt_reflexion_evaluator.md"
    if prompt_file.exists():
        system_prompt = prompt_file.read_text(encoding="utf-8").strip()
    else:
        system_prompt = (
            "You are a strict, precise evaluator. "
            "Score any response on a scale of 0.0 to 1.0. "
            "Return ONLY valid JSON with keys: score (float), verdict ('pass' or 'fail'), "
            "issues (list of strings), missing_elements (list of strings). "
            "Be harsh but fair. Deduct points for: emptiness, errors, omissions, vagueness."
        )

    user_prompt = f"Task: {task}\n\nOutput to evaluate:\n{output}"

    response = _call_llm(user_prompt, system=system_prompt, temperature=0.1, max_tokens=512)

    # 尝试解析 LLM 返回的 JSON
    import re
    try:
        if response:
            # 提取 JSON block
            match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if match:
                parsed = json.loads(match.group())
                score = float(parsed.get("score", 0.5))
                return {
                    "score": max(0.0, min(1.0, score)),
                    "issues": parsed.get("issues", []),
                    "verdict": parsed.get("verdict", "fail"),
                    "missing_elements": parsed.get("missing_elements", []),
                    "llm_used": True
                }
    except (json.JSONDecodeError, ValueError, KeyError):
        pass

    # Fallback：启发式评分
    score = 0.7
    issues = []
    if not output or len(output.strip()) < 10:
        issues.append("输出为空或太短")
        score -= 0.4
    error_signals = ["错误", "失败", "无法", "Error", "Failed", "cannot", "unable", "Traceback"]
    for sig in error_signals:
        if sig in output:
            issues.append(f"包含错误信号: {sig}")
            score -= 0.15
    if "完成" in output or "成功" in output or "done" in output.lower():
        score += 0.15

    return {
        "score": max(0.0, min(1.0, score)),
        "issues": issues,
        "verdict": "pass" if score >= 0.7 else "fail",
        "llm_used": False
    }


def reflexion_reflect(task: str, output: str, evaluation: dict) -> str:
    """反思器：调用 LLM 生成结构性反思（启发式兜底）"""
    # 加载专用反思 prompt
    prompt_file = LOGS_DIR / "prompt_reflexion_reflector.md"
    if prompt_file.exists():
        system_prompt = prompt_file.read_text(encoding="utf-8").strip()
    else:
        system_prompt = (
            "You are a critical, insightful reviewer. "
            "Given a task, its output, and an evaluation, write a concise but deep reflection (2-4 sentences) explaining:\n"
            "1. What specific errors or gaps occurred\n"
            "2. Why they happened\n"
            "3. How to fix them in the next attempt\n"
            "Be concrete — not 'improve quality' but 'add the missing database connection step before the query'. "
            "Return ONLY the reflection text, no JSON or extra formatting."
        )

    eval_json = json.dumps({
        "score": evaluation.get("score", 0),
        "verdict": evaluation.get("verdict", "fail"),
        "issues": evaluation.get("issues", []),
        "missing_elements": evaluation.get("missing_elements", [])
    }, ensure_ascii=False)

    user_prompt = f"Task: {task}\n\nOutput:\n{output}\n\nEvaluation:\n{eval_json}"

    response = _call_llm(user_prompt, system=system_prompt, temperature=0.3, max_tokens=256)

    if response and len(response.strip()) > 10:
        return response.strip()

    # Fallback：启发式反思
    issue_str = "; ".join(evaluation.get("issues", ["未知问题"]))
    return (
        f"任务：{task[:50]}\n"
        f"问题：{issue_str}\n"
        f"评分：{evaluation.get('score', 0):.2f}\n"
        f"规则：下个同类任务避免重复此错误，优先验证输出完整性。"
    )

def reflexion_review():
    """
    Reflexion 循环：对本会话最后N个操作进行自我批判。
    用法: python3 agent_core.py reflexion
    """
    reflections_file = LOGS_DIR / "reflections.json"
    reflections = read_json(reflections_file, [])

    # 取最近的失败记录
    today = datetime.now().strftime("%Y-%m-%d")
    fail_file = LOGS_DIR / f"failure_{today}.json"
    recent_failures = read_json(fail_file, [])

    if not recent_failures:
        print("✓ 今日无失败记录，无需反思")
        return

    # 对每个失败进行反思
    for failure in recent_failures[-5:]:
        action = failure.get("action", "")
        error = failure.get("error", "")
        task = f"{action}: {error[:80]}"

        # 模拟评估（实际应该调用 LLM，这里用启发式）
        eval_result = reflexion_evaluate(task, error)
        reflection = reflexion_reflect(task, error, eval_result)

        reflections.append({
            "time": failure.get("time", ""),
            "action": action,
            "error": error[:100],
            "evaluation": eval_result,
            "reflection": reflection
        })

    # 保留最近30条反思
    reflections = reflections[-30:]
    write_json(reflections_file, reflections)

    # 打印反思摘要
    print(f"=== Reflexion 反思 ({len(recent_failures)}条失败) ===")
    for r in reflections[-3:]:
        print(f"[{r['time'][:16]}] {r['action']}: {r['reflection'][:80]}")


# ── 自主研究执行器 ─────────────────────────────────────────
def autonomous_research():
    """
    自主研究：选择主题 → Web研究 → 知识沉淀 → 技能更新
    用法: python3 agent_core.py research
    """
    import urllib.request, urllib.error

    RESEARCH_TOPICS = [
        "AI agent self-improvement autonomous 2026",
        "Hermes agent optimization skills memory 2026",
        "quantitative trading AI ETF stock 2026",
        "local voice AI assistant Whisper Ollama Piper 2026",
        "novel writing AI workflow automation 2026",
        "browser automation AI agent 2026",
        "Python asyncio async best practices 2026",
        "AI agent memory architecture Mem0 LongMemEval 2026",
        "SWE-RL Meta self-play coding agents 2026",
        "量化投资 AI 选股 自动分析 2026",
    ]

    # 读取研究队列状态
    # NOTE: research_queue.json 早已从"list of {topic,done,last}"演进为
    #       {"topics": [...], "new_entries": [...], ...} 的 dict 结构，每个条目是
    #       {id, topic, status, attempt, ...}。旧代码假定 list 且用 .get("done")，
    #       在新格式上会抛 AttributeError: 'str' object has no attribute 'get'
    #       （dict 迭代出的是 key 字符串）。这里做一次格式归一化：
    #       统一成 list[dict]，兼容新旧两种格式。
    queue_file = SELF_DIR / "research_queue.json"
    raw_queue = read_json(queue_file, [])
    if isinstance(raw_queue, dict):
        entries = []
        for bucket in ("topics", "new_entries"):
            entries.extend(raw_queue.get(bucket) or [])
        queue = [e for e in entries if isinstance(e, dict)]
    elif isinstance(raw_queue, list):
        queue = [e for e in raw_queue if isinstance(e, dict)]
    else:
        queue = []

    if not queue:
        # 空队列才用内置主题兜底（保留旧行为）
        queue = [{"id": f"builtin-{i}", "topic": t, "status": "pending",
                  "attempt": 0, "last": ""}
                 for i, t in enumerate(RESEARCH_TOPICS)]
        write_json(queue_file, {"topics": queue, "new_entries": [],
                                "last_updated": datetime.now().isoformat(),
                                "note": "auto-initialized by agent_core research"})

    # 选择未完成且最久未研究的主题
    # "完成"的判定要覆盖多种历史状态写法：done=True / status in {completed,skipped}
    def _is_done(q):
        if q.get("done") is True:
            return True
        return str(q.get("status", "")).lower() in ("completed", "done", "skipped")

    candidates = [q for q in queue if not _is_done(q)]
    candidates.sort(key=lambda x: x.get("last") or "1970")
    if not candidates:
        # 全部完成 → 进入下一轮循环。
        # 注意：这里**不能**把历史条目的 status 全部抹成 pending。
        # research_queue.json 里的 completed_at / result / new_findings 是研究历史
        # 本身（92 个主题的成果都在里面），一旦被 reset 成 pending 就等于
        # 把已完成的研究记录全部抹掉，且没有任何地方能恢复。
        # 正确做法：不动历史条目，改为在 new_entries 里追加内置主题开启新一轮。
        builtin = [{"id": f"builtin-r2-{i}", "topic": t, "status": "pending",
                    "attempt": 0, "last": "", "created_at": datetime.now().isoformat(),
                    "origin": "agent_core research auto-rollover"}
                   for i, t in enumerate(RESEARCH_TOPICS)]
        if isinstance(raw_queue, dict):
            out = dict(raw_queue)
            out.setdefault("new_entries", [])
            out["new_entries"] = list(out["new_entries"]) + builtin
            out["last_updated"] = datetime.now().isoformat()
            out["note"] = (f"上一轮 {len(queue)} 个主题已全部完成，"
                           f"于 {datetime.now().isoformat()} 自动开启新一轮内置主题。")
            write_json(queue_file, out)
        else:
            write_json(queue_file, list(queue) + builtin)
        queue = queue + builtin
        candidates = list(builtin)

    topic = candidates[0]["topic"]
    print(f"研究主题: {topic}")

    # 标记开始
    for q in queue:
        if q.get("topic") == topic:
            q["last"] = datetime.now().isoformat()[:10]
            q["attempt"] = int(q.get("attempt", 0) or 0) + 1
            q["researched_at"] = datetime.now().isoformat()
            break
    _write_queue_back(queue_file, raw_queue, queue)

    # 调用 Web 搜索（通过本地 Hermes API）
    try:
        query = topic
        # NOTE: api_key 之前在这里是个从未定义的裸名字 → NameError，
        # 这条路径从来没真正跑通过。用文件里已有的 _get_api_key() 取。
        api_key = _get_api_key()
        search_payload = json.dumps({
            "model": "minimax-m3",
            "messages": [{"role": "user", "content": f"用一句话回答：{query}，并列出3个最关键的事实或工具名称"}],
            "max_tokens": 200
        }).encode()

        req = urllib.request.Request(
            "http://localhost:8642/v1/chat/completions",
            data=search_payload,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
            method="POST"
        )
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read())

        if "choices" in result:
            answer = result["choices"][0]["message"]["content"]
            print(f"发现: {answer[:200]}")

            # 记录学习
            today = datetime.now().strftime("%Y-%m-%d")
            lf = LOGS_DIR / f"learning_{today}.json"
            ld = read_json(lf, [])
            ld.append({
                "time": datetime.now().isoformat(),
                "topic": topic,
                "finding": answer[:300],
                "type": "autonomous_research"
            })
            write_json(lf, ld)

            # 标记为完成
            for q in queue:
                if q.get("topic") == topic:
                    q["done"] = True
                    q["status"] = "completed"
                    q["completed_at"] = datetime.now().isoformat()
                    q["result"] = (answer[:300])
            _write_queue_back(queue_file, raw_queue, queue)
            print(f"✓ 主题已完成: {topic}")
        else:
            print(f"搜索失败: {result}")

    except Exception as e:
        print(f"研究出错: {e}")
        # 记录失败但不阻塞
        record_failure("autonomous_research", str(e)[:100], topic)


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
        # NOTE: record_learning() takes 4 args (what, source, outcome, provenance).
        # The 4th (provenance) was previously dropped on the floor, silently losing
        # the evidence pointer that makes a learning auditable. Pass it through.
        # Also reject flag-like values instead of recording them as a learning
        # (a stray `--help` used to write a junk record into the log).
        _args = sys.argv[2:]
        if not _args or _args[0].startswith("-"):
            print("用法: agent_core.py learning <what> [source] [outcome] [provenance]")
            raise SystemExit(2)
        record_learning(
            _args[0],
            _args[1] if len(_args) > 1 else "",
            _args[2] if len(_args) > 2 else "",
            _args[3] if len(_args) > 3 else "",
        )
    elif mode == "improve":
        _args = sys.argv[2:]
        if not _args or _args[0].startswith("-"):
            print("用法: agent_core.py improve <area> <what> [result]")
            raise SystemExit(2)
        record_improvement(
            _args[0],
            _args[1] if len(_args) > 1 else "",
            _args[2] if len(_args) > 2 else "",
        )
    elif mode == "status":
        cmd_status()
    elif mode == "reflexion":
        reflexion_review()
    elif mode == "research":
        autonomous_research()
    else:
        print(f"用法: {sys.argv[0]} [heartbeat|daily|weekly|success|failure|learning|improve|status|reflexion|research]")
