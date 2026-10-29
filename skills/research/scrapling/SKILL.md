---
name: scrapling
description: Web scraping with Scrapling - HTTP fetching, stealth browser automation, Cloudflare bypass, and spider crawling via CLI and Python.
version: 1.0.0
author: FEUAZUR
license: MIT
metadata:
  hermes:
    tags: [Web Scraping, Browser, Cloudflare, Stealth, Crawling, Spider]
    related_skills: [duckduckgo-search, domain-intel]
    homepage: https://github.com/D4Vinci/Scrapling
prerequisites:
  commands: [scrapling, python]
---

# Scrapling

[Scrapling](https://github.com/D4Vinci/Scrapling) is a web scraping framework with anti-bot bypass, stealth browser automation, and a spider framework. It provides three fetching strategies (HTTP, dynamic JS, stealth/Cloudflare) and a full CLI.

**This skill is for educational and research purposes only.** Users must comply with local/international data scraping laws and respect website Terms of Service.

## When to Use

- Scraping static HTML pages (faster than browser tools)
- Scraping JS-rendered pages that need a real browser
- Bypassing Cloudflare Turnstile or bot detection
- Crawling multiple pages with a spider
- When the built-in `web_extract` tool does not return the data you need

## Installation

```bash
pip install "scrapling[all]"
scrapling install
```

Minimal install (HTTP only, no browser):
```bash
pip install scrapling
```

With browser automation only:
```bash
pip install "scrapling[fetchers]"
scrapling install
```

## Quick Reference

| Approach | Class | Use When |
|----------|-------|----------|
| HTTP | `Fetcher` / `FetcherSession` | Static pages, APIs, fast bulk requests |
| Dynamic | `DynamicFetcher` / `DynamicSession` | JS-rendered content, SPAs |
| Stealth | `StealthyFetcher` / `StealthySession` | Cloudflare, anti-bot protected sites |
| Spider | `Spider` | Multi-page crawling with link following |

## CLI Usage

### Extract Static Page

```bash
scrapling extract get 'https://example.com' output.md
```

With CSS selector and browser impersonation:

```bash
scrapling extract get 'https://example.com' output.md \
  --css-selector '.content' \
  --impersonate 'chrome'
```

### Extract JS-Rendered Page

```bash
scrapling extract fetch 'https://example.com' output.md \
  --css-selector '.dynamic-content' \
  --disable-resources \
  --network-idle
```

### Extract Cloudflare-Protected Page

```bash
scrapling extract stealthy-fetch 'https://protected-site.com' output.html \
  --solve-cloudflare \
  --block-webrtc \
  --hide-canvas
```

### POST Request

```bash
scrapling extract post 'https://example.com/api' output.json \
  --json '{"query": "search term"}'
```

### Output Formats

The output format is determined by the file extension:
- `.html` -- raw HTML
- `.md` -- converted to Markdown
- `.txt` -- plain text
- `.json` / `.jsonl` -- JSON

## Python: HTTP Scraping

### Single Request

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
for q in quotes:
    print(q)
```

### Session (Persistent Cookies)

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate='chrome') as session:
    page = session.get('https://example.com/', stealthy_headers=True)
    links = page.css('a::attr(href)').getall()
    for link in links[:5]:
        sub = session.get(link)
        print(sub.css('h1::text').get())
```

### POST / PUT / DELETE

```python
page = Fetcher.post('https://api.example.com/data', json={"key": "value"})
page = Fetcher.put('https://api.example.com/item/1', data={"name": "updated"})
page = Fetcher.delete('https://api.example.com/item/1')
```

### With Proxy

```python
page = Fetcher.get('https://example.com', proxy='http://user:pass@proxy:8080')
```

## Python: Dynamic Pages (JS-Rendered)

For pages that require JavaScript execution (SPAs, lazy-loaded content):

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch('https://example.com', headless=True)
data = page.css('.js-loaded-content::text').getall()
```

### Wait for Specific Element

```python
page = DynamicFetcher.fetch(
    'https://example.com',
    wait_selector=('.results', 'visible'),
    network_idle=True,
)
```

### Disable Resources for Speed

Blocks fonts, images, media, stylesheets (~25% faster):

```python
from scrapling.fetchers import DynamicSession

with DynamicSession(headless=True, disable_resources=True, network_idle=True) as session:
    page = session.fetch('https://example.com')
    items = page.css('.item::text').getall()
```

### Custom Page Automation

```python
from playwright.sync_api import Page
from scrapling.fetchers import DynamicFetcher

def scroll_and_click(page: Page):
    page.mouse.wheel(0, 3000)
    page.wait_for_timeout(1000)
    page.click('button.load-more')
    page.wait_for_selector('.extra-results')

page = DynamicFetcher.fetch('https://example.com', page_action=scroll_and_click)
results = page.css('.extra-results .item::text').getall()
```

## Python: Stealth Mode (Anti-Bot Bypass)

For Cloudflare-protected or heavily fingerprinted sites:

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch(
    'https://protected-site.com',
    headless=True,
    solve_cloudflare=True,
    block_webrtc=True,
    hide_canvas=True,
)
content = page.css('.protected-content::text').getall()
```

### Stealth Session

```python
from scrapling.fetchers import StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:
    page1 = session.fetch('https://protected-site.com/page1')
    page2 = session.fetch('https://protected-site.com/page2')
```

## Element Selection

All fetchers return a `Selector` object with these methods:

### CSS Selectors

```python
page.css('h1::text').get()              # First h1 text
page.css('a::attr(href)').getall()      # All link hrefs
page.css('.quote .text::text').getall() # Nested selection
```

### XPath

```python
page.xpath('//div[@class="content"]/text()').getall()
page.xpath('//a/@href').getall()
```

### Find Methods

```python
page.find_all('div', class_='quote')       # By tag + attribute
page.find_by_text('Read more', tag='a')    # By text content
page.find_by_regex(r'\$\d+\.\d{2}')       # By regex pattern
```

### Similar Elements

Find elements with similar structure (useful for product listings, etc.):

```python
first_product = page.css('.product')[0]
all_similar = first_product.find_similar()
```

### Navigation

```python
el = page.css('.target')[0]
el.parent                # Parent element
el.children              # Child elements
el.next_sibling          # Next sibling
el.prev_sibling          # Previous sibling
```

## Python: Spider Framework

For multi-page crawling with link following:

```python
from scrapling.spiders import Spider, Request, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 10
    download_delay = 1

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
                "tags": quote.css('.tag::text').getall(),
            }

        next_page = response.css('.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page)

result = QuotesSpider().start()
print(f"Scraped {len(result.items)} quotes")
result.items.to_json("quotes.json")
```

### Multi-Session Spider

Route requests to different fetcher types:

```python
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class SmartSpider(Spider):
    name = "smart"
    start_urls = ["https://example.com/"]

    def configure_sessions(self, manager):
        manager.add("fast", FetcherSession(impersonate="chrome"))
        manager.add("stealth", AsyncStealthySession(headless=True), lazy=True)

    async def parse(self, response: Response):
        for link in response.css('a::attr(href)').getall():
            if "protected" in link:
                yield Request(link, sid="stealth")
            else:
                yield Request(link, sid="fast", callback=self.parse)
```

### Pause/Resume Crawling

```python
spider = QuotesSpider(crawldir="./crawl_checkpoint")
spider.start()  # Ctrl+C to pause, re-run to resume from checkpoint
```

## Pitfalls

- **Browser install required**: run `scrapling install` after pip install -- without it, `DynamicFetcher` and `StealthyFetcher` will fail
- **Timeouts**: DynamicFetcher/StealthyFetcher timeout is in **milliseconds** (default 30000), Fetcher timeout is in **seconds**
- **Cloudflare bypass**: `solve_cloudflare=True` adds 5-15 seconds to fetch time -- only enable when needed
- **Resource usage**: StealthyFetcher runs a real browser -- limit concurrent usage
- **Legal**: always check robots.txt and website ToS before scraping. This library is for educational and research purposes
- **Python version**: requires Python 3.10+

## Anti-bot platforms: structured data, not just pages

When a site serves a **captcha interstitial** to headless browsers, and you
need structured data (titles, authors, engagement counts, media URLs) rather
than a readable page, the extraction path is different from Scrapling's
fetchers. Three rules carry the whole class of work:

1. **Headless Chromium is detected; a patched fingerprint is what passes.**
   A stealth browser (CloakBrowser) reports `navigator.webdriver == False`
   and gets the real page plus the risk-control cookies. Headless is fine —
   the earlier assumption that a captcha wall implies you need a *headed*
   browser is wrong; it implies you need a *patched* one.
2. **Intercept the page's own API responses; never construct the request.**
   A hand-built call to a detail endpoint returns
   `403 Blocked by ArgusSecurityPlugin Sign Invalid` — the signature cookie is
   bound to the request context. The page's own XHRs are already signed, so
   register a response handler and read the payload it received. Scroll to
   paginate the feed.
3. **Fetch media over plain HTTP, not through the browser.** Captured CDN URLs
   are signed; a plain GET with `Referer` + a desktop `User-Agent` downloads
   them and needs **no cookies**. Routing bytes through the page fails because
   the platform's security SDK patches `window.fetch` and breaks cross-origin
   fetches.

Full worked recipe (stealth-browser install, the XHR-interception pattern, the
Netscape cookie-jar format rules, the QR-login endpoint, keeping a stealth
browser alive across a long wait, and the checklist before declaring a site
unreadable): `references/anti-bot-platform-reading.md`.

`scripts/fetch_login_qr.py` — fetches a fresh login QR for a QR-login site by
calling the QR endpoint from inside the stealth browser's own page context.
Runnable as-is after editing `SITE_HOST` / `QR_PATH` / `QUERY`. Writes a
`*.meta.json` sidecar with the token and expiry.

**Mint short-TTL artifacts on demand, not from a background refresher.** A
login QR lives ~60 s and the page does *not* re-request one when it expires —
a watcher that only listens for responses never sees a second code, and a
code sent late is a wasted scan. Run the generator when the user says they
are ready, tell them the expiry time, and let a separate watcher poll for the
scan result. Give the generator and the watcher **different browser
profiles**: two chromium instances on one profile directory die with
`Failed to create a ProcessSingleton`. The token is server-issued and not
profile-bound, so separating them is safe.

**Reading is not writing.** A login credential on a scraper unlocks *reading*
— public content behind that account. It does not authorize posting,
commenting, liking, following, or DMing. If the user hands over an account
for scraping, use it to read. If they later want publishing, that is a
separate explicit authorization — say what the account would be used for and
get agreement on the scope (what to publish, where, how often, and whether a
human reviews it) before writing anything under that identity.

**State the capability delta before asking for a credential.** A dedicated
account often unlocks less than expected: measure what the *anonymous*
session can already do, and say plainly which one capability the login would
add. On a QR-login platform, public feed + video detail + download usually
work without any account; the real delta is often just search and complete
comment threads. Offering that breakdown — and often recommending *not*
logging in — is better service than eagerly asking for credentials. Logging in
also raises risk (a cookie lands on disk; the platform's risk control is
stricter on authenticated sessions), so an unused account is a net liability.

**Authorisation is scope-specific, and the boundary is write vs read.** When
a user says "the account is yours", that covers reading and using it within
the task at hand; it does not by itself authorise broadcasting under that
identity. Read the request as: act freely *inside* the granted scope, and ask
once — with the scope spelled out — before crossing into anything
irreversible (publishing, posting, contacting people). Say plainly what you
will and will not do with it rather than discovering the boundary by asking
permission for every small step.

**Cookie-jar export trap:** Python's `http.cookiejar` asserts
`domain_specified == initial_dot`, so in a Netscape cookie file the domain
column and the includeSubdomains column must agree (`.site.com`↔`TRUE`,
`site.com`↔`FALSE`). Disagreement makes the tool reject the whole file, and
`expires` must be a future epoch — session cookies (`-1`) get skipped.

## Cloudflare / Bot-Protected Site Workarounds

When `StealthyFetcher` is unavailable or `browser_navigate` gets blocked, try these in order:

1. **GitHub raw content** — most reliable: `https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}` → direct download, no Cloudflare
2. **GitHub API + tree walk** — use `https://api.github.com/repos/{owner}/{repo}/contents` to list directory contents, then download files via raw URLs
3. **Douyin CDN images** — Douyin `douyinpic.com` URLs 403 when accessed directly. Add headers:
   ```bash
   curl -sL -H "Referer: https://www.douyin.com/" -H "User-Agent: Mozilla/5.0 ..." "<url>" -o output.webp
   ```
   Then convert with Pillow if needed: `Image.open('a.webp').save('a.jpg', 'JPEG')`
4. **Thingiverse / GrabCAD / Printables / Cults3D** — all block non-browser clients with Cloudflare. Use `browser_navigate` if available, or search via GitHub instead

## Downloading large assets when a single connection is throttled

Some CDNs and the GitHub release-asset endpoint cap each connection hard
(observed: ~25 KB/s per connection). A single stream then takes hours for a
few hundred MB. The API asset endpoint supports `Range`, so N workers over
fixed-size ranges multiply throughput (observed: 12 workers × 4 MB ranges →
~230 KB/s, a 9× improvement, turning a 137-minute fetch into 14).

```python
# each worker writes its own .partN file; concatenate, then verify
ranges = [(i, pos, min(pos + CHUNK - 1, total - 1)) for i, pos in ...]
with cf.ThreadPoolExecutor(max_workers=12) as ex:
    ex.submit(fetch, i, start, end, out)   # GET with Range: bytes=start-end
# then concatenate in order and sha256 against the digest the API published
```

Retry each range with a bounded attempt count, resuming from what the part
file already holds. **Verify the sha256 against the digest the release
metadata advertises** before using the file.

## Vision Tool Local File Limitation

When downloading images for analysis via `vision_analyze`:
- **Must use paths under `/home/saber/`** — `/tmp/` is blocked with `Access denied`
- Download to e.g. `~/.hermes/cache/` then copy from `/tmp/` there
- Pipeline: `curl -o /tmp/file.jpg → cp to ~/.hermes/cache/ → vision_analyze(/home/saber/.hermes/cache/file.jpg)`
