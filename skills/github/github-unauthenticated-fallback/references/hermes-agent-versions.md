# hermes-agent Version Tracking

Manual lookup via HTML scraping (GitHub API rate-limited without auth).

## Latest Known State (2026-08-06)

| Item | Value |
|---|---|
| Latest release tag | `v2026.8.3` |
| Latest commit SHA | `aaf9688519cca58dd5f76a589a0911aff269b060` |
| Installed version | `v2026.4.30` (commit `f27fcb6a82b8487174ca941c15e7a5887371eede`) |
| Status | **4 months behind** |

## Latest 5 Tags (from tags page scrape)

1. `v2026.8.3`
2. `v2026.7.30`
3. `v2026.7.20`
4. `v2026.7.7.2`
5. `v2026.7.7`

## Cron Check Command

```python
# Run via execute_code or terminal — use execute_code for HTTP + regex
import subprocess, re, os

def scrape(url):
    result = subprocess.run(
        ["curl", "-s", "--max-time", "15",
         "-H", "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
         url],
        capture_output=True, text=True
    )
    return result.stdout

# Releases page — latest tag
html = scrape("https://github.com/NousResearch/hermes-agent/releases")
tags = re.findall(r'/NousResearch/hermes-agent/releases/tag/([^"]+)"', html)
tags = list(dict.fromkeys(tags))
print(f"Latest tag: {tags[0] if tags else 'unknown'}")

# Commits page — latest SHA
html = scrape("https://github.com/NousResearch/hermes-agent/commits")
shas = re.findall(r'/NousResearch/hermes-agent/commit/([a-f0-9]{40})', html)
shas = list(dict.fromkeys(shas))
print(f"Latest SHA: {shas[0] if shas else 'unknown'}")

# Tags page — top 5
html = scrape("https://github.com/NousResearch/hermes-agent/tags")
top_tags = re.findall(r'/NousResearch/hermes-agent/releases/tag/([^"]+)"', html)
top_tags = list(dict.fromkeys(top_tags))[:5]
print(f"Top 5 tags: {', '.join(top_tags)}")
```