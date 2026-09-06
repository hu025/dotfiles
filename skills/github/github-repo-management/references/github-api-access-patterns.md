# GitHub API Access Patterns

## Standard Access: curl / Python

Most environments can reach `api.github.com` directly:

```bash
# curl (authenticated)
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/owner/repo/releases/latest

# curl (unauthenticated — public repos only, 60 req/hr)
curl -s https://api.github.com/repos/owner/repo/releases/latest

# Python urllib with SSL disabled (for restrictive environments)
python3 -c "
import urllib.request, ssl, json
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
req = urllib.request.Request(
    'https://api.github.com/repos/owner/repo/releases/latest',
    headers={'User-Agent': 'Hermes-Agent'}
)
with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
    print(json.loads(r.read()))
"

# Python subprocess curl fallback (recommended in execute_code)
import subprocess, json
r = subprocess.run(
    ['curl', '-sL', '--max-time', '20',
     '-H', 'Authorization: token $GITHUB_TOKEN',
     'https://api.github.com/repos/owner/repo/releases/latest'],
    capture_output=True, text=True
)
data = json.loads(r.stdout)
```

## TLS-Failed Fallback: Browser Navigation

Some server environments fail TLS to `api.github.com` with:
```
SSL routines::unexpected eof while reading
```

Both `curl -sLk` and Python `urllib` fail with this error, even with SSL verification disabled. In these environments, the browser tool can reach the same API endpoints:

```python
# 1. Navigate to the API URL (the browser handles TLS internally)
browser_navigate(url="https://api.github.com/repos/owner/repo/releases/latest")

# 2. Extract the JSON body as plain text
# Use browser_console expression to get the raw JSON string
result = browser_console(expression="document.body.innerText")
data = json.loads(result)  # parse the extracted JSON

# For paginated endpoints (commits, tags, etc.)
browser_navigate(url="https://api.github.com/repos/owner/repo/commits?per_page=1")
result = browser_console(expression="document.body.innerText")
commits = json.loads(result)
latest_sha = commits[0]["sha"]  # full 40-char SHA

browser_navigate(url="https://api.github.com/repos/owner/repo/tags?per_page=5")
result = browser_console(expression="document.body.innerText")
tags = json.loads(result)
tag_names = [t["name"] for t in tags]
```

**Key pattern:** `browser_console(expression="document.body.innerText")` returns the raw API response body as a string, which can then be `json.loads()` in Python or processed in the agent.

**Note:** If the API requires authentication, the browser must be authenticated with GitHub (logged in to the web UI). For public read-only endpoints (releases, tags, commits), no auth is needed in the browser.

## Release / Tag / Commit Comparison Pattern

Use this 3-step pattern to check if a repo is up to date:

```python
# Step 1: Latest release tag
browser_navigate(url="https://api.github.com/repos/owner/repo/releases/latest")
r = browser_console(expression="document.body.innerText")
latest_tag = json.loads(r)["tag_name"]  # e.g. "v2026.7.20"

# Step 2: Latest commit SHA
browser_navigate(url="https://api.github.com/repos/owner/repo/commits?per_page=1")
r = browser_console(expression="document.body.innerText")
latest_sha = json.loads(r)[0]["sha"]  # full 40-char hex

# Step 3: Latest tags (top 5)
browser_navigate(url="https://api.github.com/repos/owner/repo/tags?per_page=5")
r = browser_console(expression="document.body.innerText")
tags = json.loads(r)
tag_names = [t["name"] for t in tags]

# Compare with installed version
if latest_tag != current_tag:
    print(f"UPDATE AVAILABLE: {latest_tag}")
if latest_sha != current_sha:
    print(f"NEW_COMMITS: {latest_sha}")
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `SSL routines::unexpected eof while reading` | Server TLS stack incompatibility with GitHub | Use browser navigation fallback (above) |
| `curl: (35) TLS connect error` | Same TLS stack issue | Try `--ipv4` flag, or use browser fallback |
| Empty response from API | Rate limit (unauthenticated) | Add `-H "Authorization: token $GITHUB_TOKEN"` or use authenticated browser session |
| `browser_console` returns None | Page didn't fully load | Wait for `browser_snapshot` before calling `browser_console` |
| JSON parse error on `document.body.innerText` | GitHub returns HTML (redirect to login page) | Ensure browser is authenticated, or use `browser_navigate` with `-L` equivalent (follow redirects is default) |
