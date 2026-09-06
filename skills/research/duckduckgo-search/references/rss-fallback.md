# RSS Feeds as Research Fallback

When both `ddgs` CLI and browser tools are unavailable, timing out, or returning empty results, **RSS feeds via `terminal` + `curl`** provide a reliable content retrieval path.

## Why RSS Works When Search Fails

- RSS is plain HTTP — no JavaScript rendering, no Cloudflare challenges
- Many niche industry sites (news, blogs, academic) publish full RSS feeds
- `curl` is universally available; no pip install needed
- Parsing via `grep -E "<title>|<pubDate>"` gives structured headlines fast

## Workflow

### Step 1: Identify the RSS feed URL

Common patterns:
```
https://<domain>/feed/
https://<domain>/rss/
https://<domain>/feed/rss/
```

Add `.xml` extension if unsure:
```
curl -s --max-time 10 "https://example.com/feed/" | head -c 200
```

### Step 2: Fetch and Parse

```bash
# Fetch RSS, extract titles + pubDates
curl -s --max-time 30 "https://dronedj.com/feed/" \
  | grep -E "<title>|<pubDate>" | head -40

# Fetch full raw feed
curl -s --max-time 30 "https://www.suasnews.com/feed/" | head -c 8000
```

### Step 3: Extract Full Article Content

Once you have a target article URL, fetch it directly and parse paragraphs:

```bash
# Extract article body paragraphs
curl -s --max-time 30 "https://dronedj.com/2026/05/12/dji-autel-drone-ban-fcc/" \
  | grep -oP '(?<=<p>)[^<]+' | head -20
```

## Verified Drone Industry RSS Feeds

| Source | URL | Notes |
|--------|-----|-------|
| DroneDJ | `https://dronedj.com/feed/` | Consumer/professional drone news |
| sUAS News | `https://www.suasnews.com/feed/` | Defense, commercial UAV, policy |
| The Verge | `https://www.theverge.com/rss/search?q=drone` | General tech, use search query RSS |
| Reuters | `https://feeds.reuters.com/reuters/technologyNews` | Add `?q=drone` or similar |

## curl Tips for RSS/HTML

```bash
# Always set a timeout
curl -s --max-time 30 "..."

# Set a User-Agent to avoid 403s
curl -s --max-time 30 \
  -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
  "https://example.com/feed/"

# Check HTTP status before parsing
curl -s -o /dev/null -w "%{http_code}" --max-time 10 "https://example.com/feed/"
# 200 = OK, 302 = redirect (follow with -L), 4xx/5xx = problem
```

## Parsing Approaches

### Extract titles/dates from RSS (XML)
```bash
curl -s "https://dronedj.com/feed/" \
  | grep -E "<title>|<pubDate>" \
  | sed 's/<[^>]*>//g' \
  | head -30
```

### Extract paragraphs from HTML article
```bash
# grep -oP for Perl regex (most reliable)
curl -s "https://example.com/article/" \
  | grep -oP '(?<=<p>)[^<]+' | head -20

# If grep -oP not available, use sed or python
curl -s "https://example.com/article/" \
  | sed -n 's/.*<p>\([^<]*\)<\/p>.*/\1/p' | head -20
```

## Limitations

- **No search ranking** — you must know or guess the target site
- **No snippet/preview** — RSS gives full items; HTML gives full articles
- **Feed may be outdated** — check `<lastBuildDate>` in the feed header
- **No images/media** — just text content
- **Encoding issues** — some feeds use HTML entities (`&#8217;`); `head -c` truncation can cut mid-entity

## Sequence for "All Search Tools Failed"

1. `curl` the target domain's `/feed/` or `/rss/` — check lastBuildDate
2. Extract titles/dates with `grep -E "<title>|<pubDate>"`
3. Identify relevant articles from titles
4. `curl` each article URL + `grep -oP '(?<=<p>)[^<]+'` for body
5. Synthesize from raw article text

## When to Use This vs. scrapling

| Approach | Use When |
|----------|----------|
| RSS `curl` | Search tools failed, you know the domain, need fast headlines |
| scrapling | Need full page rendering, CSS selection, anti-bot bypass |
| ddgs/搜索引擎 | You don't know the specific site, need ranked results |
