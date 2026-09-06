# GitHub Network Isolation — China / Blocked ISP Workarounds

## Symptoms

- `curl https://github.com` or `git clone https://github.com/...` hangs → timeout
- `curl https://api.github.com/...` **works** (API has different routing)
- `git ls-remote git@github.com:...` hangs on SSH port 22
- Both 443 (HTTPS) and 22 (SSH) fail, but GitHub API succeeds

## Root Cause

Many China ISPs and some corporate networks block outbound connections to GitHub's CDN/edge nodes on ports 443 and 22. The API uses different backend infrastructure and routes through different peers, so it often works when the web/SSH endpoints don't.

## Diagnostic Commands

```bash
# Test HTTPS connectivity (times out if blocked)
curl -v --connect-timeout 10 https://github.com 2>&1 | head -20

# Test GitHub API (usually works if HTTPS is blocked)
curl -s --connect-timeout 10 https://api.github.com/repos/NousResearch/hermes-agent | python3 -c "import sys,json; print(json.load(sys.stdin)['full_name'])"

# Test SSH port 22
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no git@github.com 2>&1
```

## Workarounds (in priority order)

### 1. SSH Key Auth (Best — permanent fix)

**Critical nuance**: `ssh -T git@github.com` succeeding (auth success) does NOT mean `git fetch` over SSH will work. Git's SSH transport opens a separate TCP connection and runs `git-upload-pack` over it — this can be blocked even when the interactive SSH auth succeeds. This system showed exactly that pattern: SSH auth worked, git fetch timed out.

If port 22 reaches `git@github.com` but fails with `Permission denied (publickey)`:
→ SSH works, just needs a registered key.

If `ssh -T git@github.com` succeeds but `git fetch` times out:
→ SSH auth is fine, but git protocol (git-upload-pack) is blocked on port 22. Use codeload CDN instead.

```bash
# Generate Ed25519 key (one-time)
ssh-keygen -t ed25519 -C "your-email@domain.com" -f ~/.ssh/id_ed25519

# Display public key for GitHub
cat ~/.ssh/id_ed25519.pub
```

Add the public key to GitHub: **Settings → SSH and GPG Keys → New SSH Key**

Then configure SSH to use this key:
```bash
# ~/.ssh/config
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
```

After adding the key, verify:
```bash
ssh -T git@github.com
# Should say: "Hi YourUsername! You've successfully authenticated..."
```

### 2. GitHub Mirror Sites (Partial — works for some users)

| Mirror | URL Pattern | Status |
|--------|-------------|--------|
| gitclone.com | `https://gitclone.com/github.com/...` | TCP connects, but also needs to reach GitHub upstream — may still hang |
| gitee.com | Manual sync required | Full mirror, but requires manual/Gitee Action setup |
| fastgit.xyz | `https://download.fastgit.xyz/...` | Often blocked in China (DNS-level) |

Note: Most GitHub mirrors proxy back to GitHub origin — if the origin is unreachable from your VPS, the mirror won't help either.

### 3. API-Based Single-File Updates (Always works)

When git transport is completely blocked but API works:

```bash
# Get latest commit SHA via API
curl -s "https://api.github.com/repos/NousResearch/hermes-agent/commits?per_page=1&sha=main" | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['sha'])"

# Compare local vs remote
curl -s "https://api.github.com/repos/NousResearch/hermes-agent/compare/LOCAL_SHA...REMOTE_SHA" | python3 -c "import sys,json; d=json.load(sys.stdin); print('ahead:', d['ahead_by'], 'behind:', d['behind_by'], 'files:', len(d['files']))"

# Download individual files via raw.githubusercontent.com (may or may not work)
curl -sL "https://raw.githubusercontent.com/NousResearch/hermes-agent/REMOTE_SHA/path/to/file" -o path/to/file

# Get file content via API
curl -s "https://api.github.com/repos/NousResearch/hermes-agent/contents/path/to/file?ref=REMOTE_SHA" | python3 -c "import sys,json,base64; print(base64.b64decode(json.load(sys.stdin)['content']).decode())"
```

### 4. Use a Proxy / VPN

If you have a proxy server:
```bash
git config --global http.proxy http://proxy-host:port
git config --global https.proxy http://proxy-host:port
```

Remove later:
```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
```

### 5. codeload.github.com CDN (Best for Tarball Downloads)

**codeload.github.com** is GitHub's official tarball CDN and often routes through different network paths than the main `github.com` web endpoint. Use it instead of `api.github.com` for tarball downloads:

```bash
# Preferred URL (faster, different CDN routing)
curl -sL "https://codeload.github.com/NousResearch/hermes-agent/tar.gz/v2026.5.16" \
  -o /tmp/hermes-upgrade.tar.gz \
  -w "HTTP:%{http_code} SIZE:%{size_download} SPEED:%{speed_download}\n" \
  --connect-timeout 10 --max-time 900

# Fallback: api.github.com tarball (works with PAT if needed)
curl -sL "https://api.github.com/repos/NousResearch/hermes-agent/tarball/TAG" \
  -H "Accept: application/vnd.github+json" \
  -o /tmp/hermes-upgrade.tar.gz
```

**Speed on blocked ISP links**: ~20-30KB/s via codeload. Monitor progress:
```bash
ls -lh /tmp/hermes-upgrade.tar.gz
tar -tzf /tmp/hermes-upgrade.tar.gz 2>/dev/null | wc -l   # entry count
```

**Verify completeness**: If download times out, check the last tarball entry and total entries vs the expected 2236 (for v2026.5.16). Partial downloads can be resumed with `curl -C -` if the server supports byte-range requests (test with `curl -sI -r 0-99 url | grep -i accept-ranges`).

**Extract after download**:
```bash
cd /tmp && tar -xzf hermes-upgrade.tar.gz
# Result: NousResearch-hermes-agent-COMMIT/ directory

# Merge into existing install:
cp -rpf NousResearch-hermes-agent-COMMIT/. ~/.hermes/hermes-agent/
rm -rf NousResearch-hermes-agent-COMMIT

# Verify:
cd ~/.hermes/hermes-agent && git log --oneline -1 && python3 -m hermes_cli.main --version
```

### 6. GitHub SSH via Proxy

```bash
# ~/.ssh/config
Host github.com
    HostName github.com
    User git
    ProxyCommand nc -X 5 -x proxy-host:port %h %p
    # or for HTTP proxy:
    # ProxyCommand curl -s --connect-timeout 5 -x http://proxy-host:port https://%h/%p
```

### 5. GitHub PAT Download for Release Tarballs

When git fetch times out but GitHub API with a PAT works, download the release tarball directly via API with PAT auth:

```bash
# Get PAT from hermes config.yaml (GITHUB_PERSONAL_ACCESS_TOKEN in mcp.github.env)
TOKEN=$(python3 -c "
import re
with open('/home/saber/.hermes/config.yaml') as f:
    for m in re.finditer(r'GITHUB_PERSONAL_ACCESS_TOKEN:\s*(\S+)', f.read()):
        print(m.group(1))
")

# Download release tarball with PAT auth
curl -L --connect-timeout 10 --max-time 300 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/NousResearch/hermes-agent/tarball/TAG" \
  -o /tmp/hermes-upgrade.tar.gz

# Verify partial download is valid gzip
file /tmp/hermes-upgrade.tar.gz
tar -tzf /tmp/hermes-upgrade.tar.gz | head -3
```

Speed on blocked ISP links: ~20-25KB/s. A 150MB tarball takes ~100 minutes. Use `--max-time` flags to avoid indefinite hangs.

### 5. GitHub PAT Tarball Download via API

```bash
# Get PAT from hermes config.yaml (GITHUB_PERSONAL_ACCESS_TOKEN in mcp.github.env)
TOKEN=$(python3 -c "
import re
with open('/home/saber/.hermes/config.yaml') as f:
    for m in re.finditer(r'GITHUB_PERSONAL_ACCESS_TOKEN:\s*(\S+)', f.read()):
        print(m.group(1))
")

# Download release tarball with PAT auth
curl -L --connect-timeout 10 --max-time 900 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/NousResearch/hermes-agent/tarball/TAG" \
  -o /tmp/hermes-upgrade.tar.gz

# Verify partial download is valid gzip
file /tmp/hermes-upgrade.tar.gz
tar -tzf /tmp/hermes-upgrade.tar.gz | head -3
```

Speed on blocked ISP links: ~20-25KB/s. A 150MB tarball takes ~100 minutes. Use `--max-time` flags to avoid indefinite hangs.

### 6. codeload.github.com CDN (Best for Tarball Downloads)

```bash
gh auth login
gh repo sync
```
gh CLI sometimes uses different transport than raw `git`.

## GitHub Release Assets

Releases have no attached `.zip`/`.tar.gz` assets (confirmed for hermes-agent):
```bash
curl -s "https://api.github.com/repos/NousResearch/hermes-agent/releases/latest"
# → assets: [] (empty)
```

## GitHub SSL/TLS Errors

### "unknown value given to http.version: 'HTTP/1.0'"
This appears as a **warning** (exit code 0, not fatal) during `git fetch` or `git ls-remote`. It's a libcurl version mismatch — git was built against a newer curl that doesn't accept `HTTP/1.0` as a valid `http.version` value. The operation still succeeds (FETCH_HEAD is updated, remote refs are fetched).

**Not a blocker** — if `git fetch` completes and shows the expected commit SHAs, ignore this warning.

### "SSL_read: unexpected eof while reading"
Usually indicates the GitHub server closed the connection mid-transfer — typically a transient network issue or ISP-level interference. Retry often succeeds. If persistent, switch to the API-based approach (workaround #3 above).

### Git clone/fetch hangs, API works
→ Primary symptom of GitHub CDN blocking in China/ISP-filtered networks. Use SSH diagnostic:
```bash
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no git@github.com 2>&1
# Permission denied (publickey) → SSH port 22 is reachable, just needs SSH key registered
# Times out → both 22 and 443 blocked; use API-based single-file updates
```

#### Git Config URL Rewrite Trap

When switching from HTTPS to SSH remote, `git remote set-url` may appear to succeed but `git remote -v` still shows HTTPS. This means a **global or system-level gitconfig** has a `url."https://github.com/".insteadOf` rewrite that overrides the per-repo setting.

**Diagnose**:
```bash
git config --list --show-origin | grep -i "insteadOf\|url\."
# Or check the actual .git/config file directly:
grep -A2 '\[remote "origin"\]' .git/config
```

**Fix**:
```bash
# Remove the rewrite rule (if added by some tool like GitHub CLI)
git config --global --unset url."https://github.com/".insteadOf

# Then set the remote explicitly in the repo's .git/config
git config remote.origin.url git@github.com:NousResearch/hermes-agent.git
```

**Always check `.git/config` directly** — `git remote -v` shows the rewritten URL, but `.git/config` shows the actual configured URL. This discrepancy is the key diagnostic sign.

- hermes-agent repo: `https://github.com/NousResearch/hermes-agent`
- Current local version: `v2026.5.7` (v0.13.0, commit `498bfc7bc`, 2026-05-07)
- Latest remote version: `v2026.5.16` (v0.14.0, 2026-05-16) — 808 commits ahead
- **GitHub API token for MCP**: `GITHUB_PERSONAL_ACCESS_TOKEN` stored in `config.yaml` under `mcp.github.env` — PAT format is `github_pat_...`, not `ghp_...`
- hermes-agent tarball URL: `https://api.github.com/repos/NousResearch/hermes-agent/tarball/TAG`
  - No release assets attached; tarball is auto-generated by GitHub from repo at tag
  - hermes-agent releases have `assets: []` — always use tarball approach
- Speed on blocked ISP: ~20-25KB/s via PAT auth; SSH also blocked even with key auth
- Local install: `~/.hermes/hermes-agent`
- Local HEAD check: `cd ~/.hermes/hermes-agent && git rev-parse HEAD`
- Compare local vs remote: `cd ~/.hermes/hermes-agent && git fetch origin main --depth=1 && git log --oneline FETCH_HEAD ^HEAD`
- venv path: `~/.hermes/hermes-agent/venv/bin/python`

## Version Monitoring (Cron Job)

When git fetch is blocked, use the GitHub API for version monitoring:
```
0 */6 * * * curl -s "https://api.github.com/repos/NousResearch/hermes-agent/tags?per_page=1" | python3 -c "import sys,json; t=json.load(sys.stdin); print(t[0]['name'], t[0]['commit']['sha'])"
```
