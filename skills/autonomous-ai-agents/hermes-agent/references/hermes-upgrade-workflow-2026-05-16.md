# GitHub Tarball Download — Upgrade Workflow (2026-05-16)

## Session Summary

Attempted upgrade from v0.13.0 (v2026.5.7, commit `498bfc7bc`) to v0.14.0 (v2026.5.16, commit `8487dfb`).

**Key findings:**
- SSH to github.com:22 succeeds (auth: `Hi hu025!`)
- `git fetch` over SSH times out — git protocol (git-upload-pack) is blocked even when interactive SSH works
- `curl api.github.com` works, `curl github.com` hangs
- codeload.github.com works at ~24KB/s (2236 entries, ~14MB compressed)
- GitHub API returns `assets: []` for releases — no release assets, only auto-generated tarballs
- hermes-agent v2026.5.16 tarball: 2236 entries, 14.6MB compressed, commit `8487dfb57d2f2f7b310a2b3eb692b32674af22cd`

## Verified Download URLs

```
# codeload CDN (preferred — different routing than api.github.com)
https://codeload.github.com/NousResearch/hermes-agent/tar.gz/v2026.5.16

# API tarball (also works, same speed)
https://api.github.com/repos/NousResearch/hermes-agent/tarball/v2026.5.16

# GitHub API release endpoint
https://api.github.com/repos/NousResearch/hermes-agent/releases/tags/v2026.5.16
```

## Partial Download Recovery

The session's `/tmp/hermes-codeload.tar.gz` had 14MB of 14.6MB (3154/3154 entries visible to tar -tzf but gzip EOF error on actual extraction). The tarball listing was complete but the gzip stream was truncated at 14MB. The remaining 0.6MB was never received.

**Lesson**: Always verify gzip stream integrity before assuming a partial download is usable:
```bash
python3 -c "import gzip; gzip.GzipFile('/tmp/hermes-upgrade.tar.gz').read(512); print('OK')"
```

## Upgrade Verification Checklist

After extracting tarball over existing install:
```bash
cd ~/.hermes/hermes-agent

# 1. Verify new commit
git log --oneline -1
# Expected: 8487dfb57d2 (v2026.5.16)

# 2. Verify new version
python3 -m hermes_cli.main --version
# Expected: v0.14.0

# 3. Verify key new files exist
ls run_agent.py cli.py pyproject.toml package.json 2>/dev/null | wc -l

# 4. Check for breaking changes
git log --oneline v2026.5.7..v2026.5.16 --stat | tail -20

# 5. Rebuild web UI (required after major version upgrade)
cd ~/.hermes/hermes-agent/web && npm install && npm run build

# 6. Restart gateway
systemctl --user restart hermes-gateway.service
hermes doctor
```

## Python 版本兼容性 — 升级决策树

hermes-agent 新版本通常对 Python 版本有约束。查 `Requires-Python`：

```bash
curl -s --max-time 10 "https://api.github.com/repos/NousResearch/hermes-agent/releases/latest" \
  | python3 -c "import sys,json,re; d=json.load(sys.stdin); [print(a['name'], re.search(r'Requires-Python: (.*)', a.get('body','')).group(1) if re.search(r'Requires-Python: (.*)', a.get('body','')) else '') for a in d.get('assets',[])]"

# 快速查本地 Python
python3 --version
# 本地 venv 的 Python
/home/saber/.hermes/hermes-agent/venv/bin/python3 --version
```

**决策：**

| 本地 Python | PyPI 最高版本 | GitHub 最新 | 行动 |
|------------|-------------|-----------|------|
| 3.11–3.13 | 0.19.0 | 0.19.0 | `pip install --upgrade hermes-agent` |
| 3.14+ | 0.15.2 | 0.19.0 | **无法从 PyPI 升级**，见下方路径 |
| 任意 | - | 任意 | `pip install git+https://...@vX.X.X`（git 超时时失败）|
| 任意 | - | 任意 | CDN tarball 安装（推荐，见下）|

**路径 1：CDN tarball（网络慢但可靠）**
```bash
TAG="v2026.7.20"   # 从 GitHub API 查到的版本
curl -sL "https://codeload.github.com/NousResearch/hermes-agent/tar.gz/$TAG" -o /tmp/hermes.tar.gz

# 验证完整性
python3 -c "import gzip; gzip.GzipFile('/tmp/hermes.tar.gz').read(512); print('OK')"

# 解压覆盖（保留原 venv）
tar -xzf /tmp/hermes.tar.gz -C /tmp --strip-components=1
cp -r /tmp/hermes-agent/* ~/.hermes/hermes-agent/
```

**路径 2：降级 Python（根治）**
```bash
# Arch Linux
sudo pacman -S python311 python311-venv
cd ~/.hermes/hermes-agent
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade hermes-agent
```

## Network Path Priority (for blocked ISP environments)

1. `codeload.github.com` (port 443) — best for tarballs
2. `api.github.com` (port 443) — works for API calls
3. SSH port 22 — interactive auth works, git protocol blocked
4. `raw.githubusercontent.com` (port 443) — may work for individual file updates