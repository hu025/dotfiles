#!/usr/bin/env python3
"""验证 Hermes config.yaml 里每一个 tier 模型真实可调用。

用法：
    python3 scripts/verify_tiers.py [--config ~/.hermes/config.yaml]

存在两个必须绕开的陷阱（细节见 SKILL.md）：

1. 端点。MiniMax 的 chat 必须走 /text/chatcompletion_v2，
   不是 OpenAI 的 /chat/completions（后者返回 401 authorized_error）。
2. 凭据。yaml.safe_load 会把 api_key 脱敏成占位符，必须用正则读原文。

并且：HTTP 200 不等于成功，真正的状态在响应体的
base_resp.status_code 里（0 = 成功，1004 = 鉴权失败）。
"""
import argparse
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.request

import yaml

# config 里可能带 'minimax/xxx' 形式的前缀，映射回真实模型 id
ALIAS = {"minimax/MiniMax-M3": "MiniMax-M3",
         "minimax/MiniMax-M2.7": "MiniMax-M2.7"}

# 非 chat 类能力：单独的端点与请求体
EMBEDDING_MODELS = {"embo-01", "nomic-embed-text"}


def read_key(raw_text: str) -> str:
    """从 config 原文正则取 api_key，绕过 safe_load 的脱敏。"""
    m = re.search(
        r"^providers:\s*\n  custom:\s*\n\s+api_key:\s*'?([^'\n]+?)'?\s*$",
        raw_text, re.M)
    if not m:
        sys.exit("找不到 providers.custom.api_key")
    return m.group(1)


def call(base, key, path, payload, timeout=90):
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        f"{base}{path}",
        headers={"Authorization": f"Bearer {key}",
                 "Content-Type": "application/json"},
        data=json.dumps(payload).encode())
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            body = r.read().decode()
            return r.status, body, time.time() - t0
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:120], time.time() - t0
    except Exception as e:
        return -1, f"{type(e).__name__}: {e}", time.time() - t0


def check_chat(base, key, model):
    st, body, el = call(base, key, "/text/chatcompletion_v2", {
        "model": ALIAS.get(model, model),
        "messages": [{"role": "user", "content": "说ok"}],
        "max_tokens": 2000})
    if st != 200:
        return False, f"HTTP {st}", el
    d = json.loads(body)
    code = d.get("base_resp", {}).get("status_code")
    txt = (d.get("choices") or [{}])[0].get("message", {}).get("content", "")
    if code not in (0, None):
        return False, f"status_code={code}", el
    return bool(txt), (f"{el:.1f}s" if txt else "空输出"), el


def check_embedding(base, key, model):
    st, body, el = call(base, key, "/embeddings", {
        "model": model, "texts": ["测试"], "type": "db"})
    if st != 200:
        return False, f"HTTP {st}", el
    d = json.loads(body)
    v = d.get("vectors") or []
    return bool(v), (f"{len(v[0])}维" if v else "无向量"), el


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="/home/saber/.hermes/config.yaml")
    args = ap.parse_args()

    raw = open(args.config).read()
    cfg = yaml.safe_load(raw)          # 仅用于结构与模型名
    key = read_key(raw)                # 凭据走正则
    base = cfg["providers"]["custom"]["base_url"].rstrip("/")

    targets = []
    tiers = cfg.get("fallback_base_model_routing", {}).get("tiers", {})
    for name, v in tiers.items():
        if isinstance(v, dict) and v.get("model"):
            targets.append((name, v["model"]))
    if cfg.get("model"):
        targets.append(("主模型", cfg["model"]))
    fb = cfg.get("fallback_base_model_routing", {}).get("model")
    if fb:
        targets.append(("fallback", fb))

    print("=" * 66)
    print(f"{'tier':<12}{'模型':<26}{'耗时':<9}结果")
    print("=" * 66)
    allok = True
    for name, model in targets:
        if model in EMBEDDING_MODELS:
            ok, info, _ = check_embedding(base, key, model)
        else:
            ok, info, el = check_chat(base, key, model)
            info = f"{el:.1f}s {info}" if ok else info
        allok &= ok
        print(f"{name:<12}{model:<26}{info:<9}{'✅' if ok else '❌'}")
    print("=" * 66)
    print(f"全部可用: {'是 ✅' if allok else '否 ❌'}")
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())