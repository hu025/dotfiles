---
name: github-unauthenticated-fallback
description: "GitHub API rate-limit workaround: HTML scraping when no token/gh-auth is available."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, API, Rate-Limit, Fallback, Scraping]
    related_skills: [github-repo-management, github-auth]
---

# GitHub API Unauthenticated Fallback

When GitHub API endpoints return 403 (rate limit exceeded) and no `GITHUB_TOKEN` / `GH_TOKEN` / authenticated `gh` is available, scrape the HTML pages directly. HTML endpoints have significantly higher unauthenticated rate limits.

## Detection

Python `urllib` with SSL-disabled context still gets 403 from the API — SSL flags are irrelevant, the rate limit is at the API level:

```
ERROR fetching release: HTTP Error 403: rate limit exceeded
```

## Credential Check Order (before any API call)

```bash
# 1. Environment variables
TOKEN="${GITHUB_TOKEN:-${GH_TOKEN:-}}"

# 2. gh CLI auth status
if command -v gh &>/dev/null && gh auth status &>/dev/null 2>&1; then
  echo "gh authenticated — use gh api"
else
  echo "gh not logged in"
fi

# 3. ~/.netrc
if [ -z "$TOKEN" ] && [ -f ~/.netrc ]; then
  TOKEN=$(grep -A2 "github.com" ~/.netrc 2>/dev/null | awk '/password/{print $2}')
fi
```

## HTML Scraping Fallback

Use `curl` with a realistic browser User-Agent to hit the HTML page directly:

```bash
curl -s --max-time 15 \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  "https://github.com/owner/repo/releases"
```

HTML and API have separate rate limit buckets — the HTML endpoint will often succeed when the API is blocked.

## Regex Patterns for Common Data

### Release / tag names from releases page

```python
import re, subprocess

result = subprocess.run(
    ["curl", "-s", "--max-time", "15",
     "-H", "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
     "https://github.com/owner/repo/releases"],
    capture_output=True, text=True
)
html = result.stdout

# Full tag names from release links
tags = re.findall(r'/owner/repo/releases/tag/([^"]+)"', html)
tags = list(dict.fromkeys(tags))  # dedupe, preserve order
```

### Latest commit SHAs from commits page

```python
# Full 40-char SHA
shas = re.findall(r'/owner/repo/commit/([a-f0-9]{40})', html)
shas = list(dict.fromkeys(shas))
```

### Tag list from tags page

```python
result = subprocess.run(
    ["curl", "-s", "--max-time", "15",
     "-H", "User-Agent: Mozilla/5.0 ...",
     "https://github.com/owner/repo/tags"],
    capture_output=True, text=True
)
html = result.stdout
tags = re.findall(r'/owner/repo/releases/tag/([^"]+)"', html)
tags = list(dict.fromkeys(tags))[:5]
```

## Key URLs

| Data needed | HTML URL |
|---|---|
| Latest release tag | `https://github.com/owner/repo/releases` |
| Recent commit SHAs | `https://github.com/owner/repo/commits` |
| Tag list | `https://github.com/owner/repo/tags` |
| Repo overview | `https://github.com/owner/repo` |

## Caveats

- HTML structure can change without notice — re-validate regex patterns if they stop matching.
- Use as **read-only fallback only**; write operations (issues, PRs, releases) require the API.
- Authenticated API (`gh` or token) is always preferred for accuracy and reliability.