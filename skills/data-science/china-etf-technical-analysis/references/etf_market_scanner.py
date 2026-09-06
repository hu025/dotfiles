#!/usr/bin/env python3
"""
EastMoney push2 ETF Market Scanner
Fetches all A-share ETFs sorted by gainers/losers in one API call.
Works reliably in execute_code/sandbox via subprocess.run(shell=True).
"""
import subprocess, json, sys

ETF_API = (
    "https://push2.eastmoney.com/api/qt/clist/get"
    "?pn=1&pz=50&po=1&np=1"
    "&ut=bd1d9ddb04089700cf9c27f6f7426281"
    "&fltt=2&invt=2&fid={fid}"
    "&fs=b:MK0021+f:MK0022+f:MK0023"
    "&fields=f12,f14,f3,f2,f6"
)

def fetch_etfs(sort="chg", limit=10):
    """
    Fetch and sort A-share ETFs.
    sort: 'chg' (today % change), 'ytd' (YTD % change)
    Returns: list of dicts {code, name, chg, price, ytd}
    """
    fid = "f3" if sort == "chg" else "f6"
    url = ETF_API.format(fid=fid)

    r = subprocess.run(
        f'curl -s "{url}"',
        capture_output=True, text=True, timeout=10, shell=True
    )
    d = json.loads(r.stdout)
    etfs = d["data"]["diff"]

    if sort == "chg":
        etfs = sorted(etfs, key=lambda a: a["f3"], reverse=True)
    else:
        etfs = sorted(etfs, key=lambda a: a["f6"], reverse=True)

    result = []
    for x in etfs[:limit]:
        result.append({
            "code": x["f12"],
            "name": x["f14"],
            "chg": x["f3"],
            "price": x["f2"],
            "ytd": x["f6"],
        })
    return result

if __name__ == "__main__":
    sort = sys.argv[1] if len(sys.argv) > 1 else "chg"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    gainers = fetch_etfs("chg", limit)
    losers  = fetch_etfs("chg", limit)
    losers  = sorted(losers, key=lambda a: a["chg"])

    print("=== 今日涨幅TOP ===")
    for x in gainers:
        print(f"  {x['name']:18s} {x['code']:8s} {x['chg']:+.2f}%  现价:{x['price']}")

    print(f"\n=== 今日跌幅TOP ===")
    for x in losers[:10]:
        print(f"  {x['name']:18s} {x['code']:8s} {x['chg']:+.2f}%  现价:{x['price']}")
