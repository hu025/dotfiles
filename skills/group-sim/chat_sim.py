#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
群聊仿真引擎（轻量版）

从 Derpyu520/qq-bridge 的「一代仿真 / 二代仿真」机制提炼的自实现，
不依赖 SnowLuma / DeepSeek Harness，可直接嵌入 Hermes。

设计要点（借鉴上游）：
1. 状态机：观望 → 活跃 → 试探 → 退场，每个状态决定"该不该说话、说多长"
2. 选择性参与：不是每条消息都接话；用「相关度 + 状态 + 冷却」决定
3. 主动收尾：聊到一定轮次后自己收尾，不缠着不放
4. 分句发送：一句话拆成多条短消息发，符合群聊节奏
5. [SILENT]：明确表达"这轮不说话"，而不是空字符串
6. 硬边界：出站消息全过白名单 / 额度 / 脱敏（上游的 safety guard 思路）

与上游不同：本模块只做「决策」，不做 IO，不调用 LLM。
调用方拿 decision 决定要不要发、发什么。
"""
from __future__ import annotations

import json
import re
import time
import unicodedata
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

# ── 状态机 ─────────────────────────────────────────────
STATES = ("watching", "active", "probing", "withdrawing")
STATE_LABEL_ZH = {
    "watching": "观望",
    "active": "活跃",
    "probing": "试探",
    "withdrawing": "退场",
}

# 每个状态下：最大回复字数、是否允许主动发起话题、最小间隔秒数
STATE_POLICY: dict[str, dict[str, Any]] = {
    "watching":    {"max_chars": 60,  "can_start": False, "min_gap": 1800, "reply_rate": 0.15},
    "active":      {"max_chars": 180, "can_start": True,  "min_gap": 120,  "reply_rate": 0.75},
    "probing":     {"max_chars": 90,  "can_start": True,  "min_gap": 600,  "reply_rate": 0.45},
    "withdrawing": {"max_chars": 0,   "can_start": False, "min_gap": 3600, "reply_rate": 0.0},
}

# ── 话题相关性 ─────────────────────────────────────────
# 命中关键词 → 相关度加分；命中转人工/敏感 → 强制沉默
SILENT = "[SILENT]"

_BLOCK_PATTERNS = [
    re.compile(r"(转人工|人工客服|找客服|真人|投诉|退款|赔偿)"),
    re.compile(r"(密码|验证码|身份证|银行卡|密钥|私钥|token\s*[:=]|secret)", re.I),
]
_QUESTION_RE = re.compile(r"[?？]\s*$|吗\s*$|呢\s*$|怎么|如何|什么|为什么|能不能|可以吗")
_URL_RE = re.compile(r"https?://\S+")
_MENTION_RE = re.compile(r"@[^\s@:：]{1,24}")


def _norm(text: str) -> str:
    """归一化：全角转半角、去零宽字符、压缩空白。"""
    text = unicodedata.normalize("NFKC", text or "")
    text = re.sub(r"[\u200b-\u200f\ufeff]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def relevance(msg: str, topics: list[str], bot_name: str = "") -> float:
    """相关度 0~1：被 @、提到话题、问句、包含自己的名字都加分。"""
    m = _norm(msg)
    if not m:
        return 0.0
    score = 0.0
    if bot_name and bot_name in m:
        score += 0.45
    if _MENTION_RE.search(m):
        score += 0.35
    hits = sum(1 for t in topics if t and t in m)
    score += min(0.35, hits * 0.18)
    if _QUESTION_RE.search(m):
        score += 0.12
    if _URL_RE.search(m):
        score -= 0.05
    return max(0.0, min(1.0, score))


def should_silence(msg: str) -> bool:
    """硬边界：涉及密码/验证码/人工客服时一律不接话。"""
    m = _norm(msg)
    return any(p.search(m) for p in _BLOCK_PATTERNS)


# ── 分句（群聊节奏）────────────────────────────────────
def split_sentences(text: str, max_chars: int = 90) -> list[str]:
    """把长回复拆成多条短消息。优先按句末标点，再按逗号，最后硬切。"""
    text = (text or "").strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]
    parts = re.split(r"(?<=[。！？!?；;…])\s*", text)
    out: list[str] = []
    buf = ""
    for p in (x for x in parts if x):
        if len(buf) + len(p) <= max_chars:
            buf += p
            continue
        if buf:
            out.append(buf.strip())
        while len(p) > max_chars:
            out.append(p[:max_chars].rstrip())
            p = p[max_chars:]
        buf = p
    if buf.strip():
        out.append(buf.strip())
    return [x for x in out if x]


# ── 决策 ───────────────────────────────────────────────
@dataclass
class GroupConfig:
    topics: list[str] = field(default_factory=list)
    bot_name: str = ""
    max_chars: int = 180
    max_rounds_per_topic: int = 6          # 同一话题最多接几轮，之后自己收尾
    withdraw_after_idle: int = 1800         # 空闲多久进入退场
    cooldown: int = 60                      # 两次发言最小间隔秒数
    daily_quota: int = 40                   # 每日发言上限（额度护栏）
    allowed_groups: list[str] = field(default_factory=list)   # 空=全放行；建议填
    deny_groups: list[str] = field(default_factory=list)


@dataclass
class Decision:
    speak: bool
    reason: str
    text: str = ""
    messages: list[str] = field(default_factory=list)
    state: str = "watching"
    reply_to: str | None = None


class GroupSimulator:
    """群聊仿真决策器。每个群一个实例，状态持久化到 state.json。"""

    def __init__(self, cfg: GroupConfig, state_path: str | Path | None = None):
        self.cfg = cfg
        self.state_path = Path(state_path) if state_path else None
        self.state = self._load()

    # -- 持久化 --
    def _load(self) -> dict:
        default = {
            "state": "watching",
            "last_spoke_at": 0.0,
            "last_message_at": 0.0,
            "rounds_in_topic": 0,
            "topic_key": "",
            "quota_date": "",
            "quota_used": 0,
            "closing_done": False,
            "history": [],
        }
        if self.state_path and self.state_path.exists():
            try:
                data = json.loads(self.state_path.read_text(encoding="utf-8"))
                default.update(data)
                return default
            except Exception:
                pass
        return default

    def save(self) -> None:
        if not self.state_path:
            return
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(self.state, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # -- 内部 --
    def _quota_left(self, now: float | None = None) -> int:
        # 用传入的 now 算日期，测试/回放时不能被真实时间干扰
        now = now if now is not None else time.time()
        today = time.strftime("%Y-%m-%d", time.localtime(now))
        if self.state.get("quota_date") != today:
            self.state["quota_date"] = today
            self.state["quota_used"] = 0
        return max(0, self.cfg.daily_quota - int(self.state.get("quota_used", 0)))

    def _allowed(self, group_id: str) -> bool:
        if group_id in self.cfg.deny_groups:
            return False
        if self.cfg.allowed_groups and group_id not in self.cfg.allowed_groups:
            return False
        return True

    def _maybe_transition(self, now: float) -> str:
        st = self.state.get("state", "watching")
        idle = now - float(self.state.get("last_message_at") or 0)
        if st != "withdrawing" and idle > self.cfg.withdraw_after_idle:
            st = "withdrawing"
        elif st == "withdrawing" and not self.state.get("closing_done") and idle < 120:
            # 只是长时间没人说话而自然退场（不是主动收尾结束）→ 可以慢慢回来
            st = "watching"
        self.state["state"] = st
        return st

    # -- 对外 --
    def observe(self, message: str, group_id: str = "", now: float | None = None) -> None:
        """记录一条群消息（不发言，仅更新状态）。"""
        now = now or time.time()
        self.state["last_message_at"] = now
        self.save()

    def decide(
        self,
        message: str,
        reply_text: str = "",
        group_id: str = "",
        now: float | None = None,
        state: str | None = None,
    ) -> Decision:
        """
        决定这轮要不要说话、说什么。

        reply_text: LLM 生成的候选回复（可为空 → 只做"该不该说"的判断）
        state:      可选，强制指定状态（测试用）
        """
        now = now or time.time()
        if not self._allowed(group_id):
            return Decision(speak=False, reason="group_not_allowed", state=self.state.get("state", "watching"))
        if should_silence(message):
            return Decision(speak=False, reason="blocked_by_safety", state=self.state.get("state", "watching"))

        st = state or self._maybe_transition(now)
        policy = STATE_POLICY[st]

        # 退场态：已主动收尾就彻底沉默
        if st == "withdrawing":
            if policy["reply_rate"] <= 0 or self.state.get("closing_done"):
                return Decision(speak=False, reason="withdrawn", state=st)

        # 冷却
        gap = now - float(self.state.get("last_spoke_at") or 0)
        if gap < policy["min_gap"] and st != "active":
            return Decision(speak=False, reason="cooldown", state=st)

        # 额度
        if self._quota_left(now) <= 0:
            return Decision(speak=False, reason="daily_quota_exhausted", state=st)

        # 话题轮次
        rel = relevance(message, self.cfg.topics, self.cfg.bot_name)
        # 相关度过低：直接沉默（省一次 LLM 调用）
        if rel < 0.15 and st != "active":
            return Decision(speak=False, reason="low_relevance", state=st)
        topic_key = ",".join(sorted(t for t in self.cfg.topics if t and t in _norm(message)))
        if topic_key and topic_key != self.state.get("topic_key"):
            self.state["topic_key"] = topic_key
            self.state["rounds_in_topic"] = 0
            self.state["closing_done"] = False
        rounds = int(self.state.get("rounds_in_topic", 0))

        # 主动收尾：同一话题聊够轮数后，自己退
        if rounds >= self.cfg.max_rounds_per_topic:
            # 已经收尾过了 → 彻底沉默，不再重复发收尾语
            if self.state.get("closing_done"):
                return Decision(speak=False, reason="max_rounds_reached", state="withdrawing")
            if reply_text and len(reply_text.strip()) <= 60:
                # 只允许一句收尾，然后转入退场态
                self.state["rounds_in_topic"] = rounds + 1
                self.state["closing_done"] = True
                self.state["state"] = "withdrawing"
                self.state["last_spoke_at"] = now
                self.state["quota_used"] = int(self.state.get("quota_used", 0)) + 1
                self.state["history"].append({"t": now, "msg": reply_text[:80], "closing": True})
                self.save()
                return Decision(
                    speak=True,
                    reason="closing",
                    text=reply_text.strip(),
                    messages=[reply_text.strip()],
                    state=st,
                )
            return Decision(speak=False, reason="max_rounds_reached", state=st)

        # 概率门槛：相关度越高越可能接话；active 态且高相关度时直接接
        import random
        threshold = policy["reply_rate"]
        if rel >= 0.8 and st == "active":
            threshold = 1.0          # 明确相关 + 活跃 → 必回
        elif rel < 0.2:
            threshold = 0.0          # 基本无关 → 不接
        else:
            threshold = min(1.0, threshold + rel * 0.5)
        if random.random() > threshold:
            return Decision(speak=False, reason="below_threshold", state=st)

        if not reply_text or not reply_text.strip():
            return Decision(speak=False, reason="empty_reply", state=st)

        text = reply_text.strip()
        limit = min(self.cfg.max_chars, policy["max_chars"])
        if len(text) > limit:
            text = text[:limit].rstrip() + "…"

        msgs = split_sentences(text, max_chars=limit)
        self.state["last_spoke_at"] = now
        self.state["rounds_in_topic"] = rounds + 1
        self.state["quota_used"] = int(self.state.get("quota_used", 0)) + 1
        self.state["history"].append({"t": now, "msg": text[:80]})
        self.state["history"] = self.state["history"][-50:]
        self.save()

        return Decision(
            speak=True,
            reason="speak",
            text=text,
            messages=msgs,
            state=st,
        )

    def snapshot(self, now: float | None = None) -> dict:
        return {
            "state": self.state.get("state"),
            "state_label": STATE_LABEL_ZH.get(self.state.get("state", ""), ""),
            "rounds_in_topic": self.state.get("rounds_in_topic"),
            "quota_used": self.state.get("quota_used"),
            "quota_left": self._quota_left(now),
            "last_spoke_at": self.state.get("last_spoke_at"),
        }


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="群聊仿真决策器")
    ap.add_argument("--message", required=True, help="收到的群消息")
    ap.add_argument("--reply", default="", help="候选回复")
    ap.add_argument("--group", default="", help="群号")
    ap.add_argument("--topics", default="", help="话题关键词，逗号分隔")
    ap.add_argument("--state", default="", help="状态文件路径")
    ap.add_argument("--force-state", default="", help="强制状态 watching/active/probing/withdrawing")
    args = ap.parse_args()

    cfg = GroupConfig(
        topics=[t for t in args.topics.split(",") if t],
        allowed_groups=[],
    )
    sim = GroupSimulator(cfg, args.state or None)
    d = sim.decide(
        args.message,
        args.reply,
        group_id=args.group,
        state=args.force_state or None,
    )
    print(json.dumps({
        "speak": d.speak,
        "reason": d.reason,
        "state": d.state,
        "state_label": STATE_LABEL_ZH.get(d.state, ""),
        "messages": d.messages,
        "snapshot": sim.snapshot(),
    }, ensure_ascii=False, indent=2))
