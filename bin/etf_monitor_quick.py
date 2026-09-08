#!/usr/bin/env python3
"""ETF 快速监控 - 每小时 cron 调用 etf_screener, 命中通过 Hermes 推送告警."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from etf_screener import main as screen, TOP_N, STOP_LOSS_PCT  # noqa: E402


def run() -> None:
    results = screen()
    if not results:
        return
    alerts = [r for r in results if r.get("chg_pct", 0) <= STOP_LOSS_PCT or
              r.get("score", 0) >= 8.0]
    if not alerts:
        return
    lines = [f"⚠️ ETF 告警 ({len(alerts)}/{len(results)})"]
    for r in alerts[:TOP_N]:
        lines.append(f"  {r['code']} {r['name']}: ¥{r['price']:.3f} "
                     f"{r.get('chg_pct', 0):+.2f}% score={r.get('score', 0):.1f}")
    print("\n".join(lines))


if __name__ == "__main__":
    run()
