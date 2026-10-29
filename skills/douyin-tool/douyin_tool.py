#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音图文发布 + 评论读取（轻量版）

不用 SnowLuma / DSH，直接用 CloakBrowser 的 stealth Chromium（已装 146.0.7680.177）
+ Playwright 驱动，走浏览器上下文里的 fetch —— 抖音的 x-bogus / a-bogus 签名由页面
自己生成，我们不自己实现签名算法。

关键事实（实测）：
- 普通 chromium 访问 douyin.com 会落到「验证码中间页」（argus-csp-token）
- CloakBrowser stealth 版 navigator.webdriver=False，可正常拿到推荐流和视频详情
- 评论接口：GET https://www-hj.douyin.com/aweme/v1/web/comment/list/
    ?device_platform=webapp&aid=6383&channel=channel_pc_web
    &aweme_id=<id>&cursor=0&count=20&item_type=0
- 视频详情接口：GET .../aweme/v1/web/aweme/detail/?...&aweme_id=<id>
  响应里的 statistics.comment_count 是评论总数
- 发布/评论回复/登录 都需要登录态（sessionid cookie），未登录时页面只显示「登录」按钮

用法：
    python3 douyin_tool.py comments <aweme_id> [--count 20]
    python3 douyin_tool.py info <aweme_id>
    python3 douyin_tool.py feed [--limit 10]
    python3 douyin_tool.py login-status
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

# CloakBrowser 的 venv 是 python3.13，自带编译好的 greenlet。
# 必须用它自己的 python 跑，且清掉 PYTHONPATH —— 否则会串到 Hermes 的 py3.14
# playwright，greenlet 扩展对不上，报 ModuleNotFoundError: greenlet._greenlet。
CLOAK_PY = Path.home() / ".agent-reach/tools/cloakbrowser/bin/python"
CLOAK_SITE = Path.home() / ".agent-reach/tools/cloakbrowser/lib/python3.13/site-packages"

PROFILE = Path.home() / ".hermes/douyin-profile"
UA_DESKTOP = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
               "(KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36")

COMMENT_API = ("https://www-hj.douyin.com/aweme/v1/web/comment/list/"
               "?device_platform=webapp&aid=6383&channel=channel_pc_web"
               "&aweme_id={aid}&cursor={cursor}&count={count}&item_type=0")
DETAIL_API = ("https://www-hj.douyin.com/aweme/v1/web/aweme/detail/"
              "?device_platform=webapp&aid=6383&channel=channel_pc_web"
              "&aweme_id={aid}")


def _ensure_importable() -> None:
    os.environ.pop("PYTHONPATH", None)
    if str(CLOAK_SITE) not in sys.path:
        sys.path.insert(0, str(CLOAK_SITE))


def _launch(profile: Path | None = None):
    _ensure_importable()
    from cloakbrowser import launch_persistent_context
    prof = str(profile or PROFILE)
    prof = os.path.expanduser(prof)
    Path(prof).mkdir(parents=True, exist_ok=True)
    # 清掉上次异常退出留下的 singleton 锁
    for n in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
        try:
            (Path(prof) / n).unlink()
        except FileNotFoundError:
            pass
    return launch_persistent_context(
        prof, headless=True,
        args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
    )


def _page(ctx):
    return ctx.pages[0] if ctx.pages else ctx.new_page()


def _block(page):
    """把评论接口的响应缓存下来，后面直接读。"""
    store = {}
    def on_resp(resp):
        if "comment/list" in resp.url:
            try:
                store["body"] = resp.text()
            except Exception:
                pass
    page.on("response", on_resp)
    return store


# ── 评论读取 ────────────────────────────────────────────
def fetch_comments(aweme_id: str, count: int = 20, cursor: int = 0,
                   profile: str | None = None) -> dict:
    """在浏览器上下文里 fetch 评论接口（签名参数由页面生成）。"""
    ctx = _launch(profile)
    try:
        page = _page(ctx)
        page.goto(f"https://www.douyin.com/video/{aweme_id}",
                  wait_until="domcontentloaded", timeout=60000)
        time.sleep(6)
        res = page.evaluate(
            """async (u) => {
                try {
                    const r = await fetch(u, {credentials: 'include',
                        headers: {'referer': 'https://www.douyin.com/'}});
                    return {status: r.status, body: (await r.text()).slice(0, 400000)};
                } catch (e) { return {err: String(e)}; }
            }""",
            COMMENT_API.format(aid=aweme_id, cursor=cursor, count=count),
        )
        if res.get("err"):
            return {"ok": False, "error": res["err"], "comments": []}
        try:
            data = json.loads(res.get("body") or "{}")
        except Exception as exc:
            return {"ok": False, "error": f"parse: {exc}", "comments": []}
        if not data.get("comments"):
            return {"ok": False, "error": data.get("status_msg") or "no comments (可能需要登录)",
                    "comments": []}
        out = []
        for c in data["comments"]:
            user = c.get("user") or {}
            out.append({
                "id": c.get("cid"),
                "user": user.get("nickname"),
                "sec_uid": user.get("sec_uid"),
                "text": (c.get("text") or "").strip(),
                "digg": c.get("digg_count"),
                "reply": c.get("reply_comment_total"),
                "create_time": c.get("create_time"),
                "ip": c.get("ip_label"),
            })
        return {
            "ok": True,
            "aweme_id": aweme_id,
            "total": data.get("total") or len(out),
            "has_more": data.get("has_more"),
            "cursor": data.get("cursor"),
            "comments": out,
        }
    finally:
        ctx.close()


# ── 视频信息 ────────────────────────────────────────────
def fetch_info(aweme_id: str, profile: str | None = None) -> dict:
    ctx = _launch(profile)
    try:
        page = _page(ctx)
        page.goto(f"https://www.douyin.com/video/{aweme_id}",
                  wait_until="domcontentloaded", timeout=60000)
        time.sleep(6)
        res = page.evaluate(
            """async (u) => {
                try {
                    const r = await fetch(u, {credentials: 'include',
                        headers: {'referer': 'https://www.douyin.com/'}});
                    return {status: r.status, body: (await r.text()).slice(0, 400000)};
                } catch (e) { return {err: String(e)}; }
            }""",
            DETAIL_API.format(aid=aweme_id),
        )
        if res.get("err"):
            return {"ok": False, "error": res["err"]}
        data = json.loads(res.get("body") or "{}")
        a = data.get("aweme_detail") or {}
        st = a.get("statistics") or {}
        au = a.get("author") or {}
        return {
            "ok": True,
            "aweme_id": aweme_id,
            "desc": (a.get("desc") or "").strip(),
            "author": au.get("nickname"),
            "sec_uid": au.get("sec_uid"),
            "create_time": a.get("create_time"),
            "duration_ms": a.get("duration"),
            "images": len(a.get("images") or []),
            "video": bool(a.get("video")),
            "stats": {
                "comment": st.get("comment_count"),
                "digg": st.get("digg_count"),
                "share": st.get("share_count"),
                "collect": st.get("collect_count"),
            },
        }
    finally:
        ctx.close()


# ── 推荐流 ──────────────────────────────────────────────
def fetch_feed(limit: int = 10, profile: str | None = None) -> dict:
    """从推荐流取视频 id + 标题 + 作者。"""
    ctx = _launch(profile)
    try:
        page = _page(ctx)
        page.goto("https://www.douyin.com/",
                  wait_until="domcontentloaded", timeout=60000)
        time.sleep(6)
        for _ in range(3):
            page.mouse.wheel(0, 600)
            time.sleep(1.0)
        items = page.evaluate(
            """() => {
              const out = [];
              const seen = new Set();
              document.querySelectorAll('*').forEach(e => {
                for (const a of ['href','data-item-id','data-id','data-aweme-id']) {
                  const v = e.getAttribute && e.getAttribute(a);
                  if (!v) continue;
                  const m = String(v).match(/(\\d{19})/);
                  if (m && !seen.has(m[1])) {
                    seen.add(m[1]);
                    // 从最近的带文案的祖先拿标题/作者
                    let p = e, txt = '', author = '';
                    for (let i=0;i<8 && p;i++,p=p.parentElement) {
                      const t = (p.innerText||'');
                      if (t.length > txt.length && t.length < 700) txt = t;
                    }
                    const am = txt.match(/@([^@\\s]{1,24})/);
                    if (am) author = am[1];
                    out.push({id: m[1], text: txt.slice(0,220), author});
                  }
                }
              });
              return out;
            }""")
        return {"ok": True, "count": len(items[:limit]), "items": items[:limit]}
    finally:
        ctx.close()


# ── 登录态 ──────────────────────────────────────────────
def login_status(profile: str | None = None) -> dict:
    ctx = _launch(profile)
    try:
        page = _page(ctx)
        page.goto("https://www.douyin.com/",
                  wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)
        st = page.evaluate(
            """() => {
              const btn = Array.from(document.querySelectorAll('a,button,div,span'))
                .find(e => (e.innerText||'').trim()==='登录' && e.offsetHeight>0);
              const c = document.cookie;
              return {
                hasLoginButton: !!btn,
                hasSessionid: c.includes('sessionid'),
                hasSessionidSS: c.includes('sessionid_ss'),
                hasUidTT: c.includes('uid_tt'),
                cookieLen: c.length,
                webdriver: navigator.webdriver,
                title: document.title,
              };
            }""")
        st["ok"] = True
        st["logged_in"] = st.get("hasSessionid") or st.get("hasSessionidSS")
        return st
    finally:
        ctx.close()


# ── 发布（需要登录态）──────────────────────────────────
def publish_text(text: str, images: list[str] | None = None,
                 profile: str | None = None) -> dict:
    """发布图文。未登录会直接失败并说明原因。

    抖音的发布走 creator.douyin.com 的图文投稿页，发布按钮会触发风控二次校验，
    所以这里只负责把内容填进去并报告状态，最终发布需要人在场确认。
    """
    ctx = _launch(profile)
    try:
        page = _page(ctx)
        page.goto("https://creator.douyin.com/creator-micro/content/post",
                  wait_until="domcontentloaded", timeout=60000)
        time.sleep(6)
        st = login_status.__wrapped__ if False else None
        info = page.evaluate(
            """() => {
              const t = document.body.innerText || '';
              return {
                url: location.href,
                needLogin: t.includes('扫码登录') || t.includes('验证码登录') || t.includes('密码登录'),
                hasUpload: !!document.querySelector('input[type=file]'),
                title: document.title,
              };
            }""")
        if info.get("needLogin"):
            return {"ok": False, "error": "creator 平台未登录（需要 sessionid cookie）",
                    "stage": "auth", "detail": info}
        return {"ok": False, "error": "图文发布需要在 creator 平台走完整投稿流程，"
                                      "当前只实现了页面定位，未提交",
                "stage": "partial", "detail": info}
    finally:
        ctx.close()


# ── CLI ─────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(description="抖音图文发布 + 评论读取")
    ap.add_argument("--profile", default=None, help="浏览器 profile 目录")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("comments", help="读取视频评论")
    p.add_argument("aweme_id")
    p.add_argument("--count", type=int, default=20)
    p.add_argument("--cursor", type=int, default=0)

    p = sub.add_parser("info", help="视频信息")
    p.add_argument("aweme_id")

    p = sub.add_parser("feed", help="推荐流")
    p.add_argument("--limit", type=int, default=10)

    sub.add_parser("login-status", help="登录态检测")

    p = sub.add_parser("publish", help="发布图文（需登录）")
    p.add_argument("text")
    p.add_argument("--images", nargs="*", default=[])

    args = ap.parse_args()

    if args.cmd == "comments":
        out = fetch_comments(args.aweme_id, args.count, args.cursor, args.profile)
    elif args.cmd == "info":
        out = fetch_info(args.aweme_id, args.profile)
    elif args.cmd == "feed":
        out = fetch_feed(args.limit, args.profile)
    elif args.cmd == "login-status":
        out = login_status(args.profile)
    elif args.cmd == "publish":
        out = publish_text(args.text, args.images, args.profile)
    else:
        out = {"ok": False, "error": "unknown command"}

    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
