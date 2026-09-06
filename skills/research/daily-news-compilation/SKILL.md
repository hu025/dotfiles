---
name: daily-news-compilation
description: Gather, extract, and compile daily news briefs from Chinese-language and multi-language sources using browser tools and RSS feeds when specialized vertical media sites are unreachable. Use when the user asks for a daily news briefing, morning news report, industry digest, or similar recurring news aggregation task.
version: 1.1.0
author: hermes-agent
license: MIT
metadata:
  hermes:
    tags: [news, briefing, daily, Chinese, RSS, browser, industry-digest]
    related_skills: [searxng-search, scrapling, duckduckgo-search]
    fallback_for_toolsets: [web]
---

# Daily News Compilation

Compile a daily news briefing from multiple sources — primarily Chinese-language news sites — when specialized vertical media sites are unreachable. This skill covers source selection, browser-based extraction, and formatting.

## Source Strategy

### Tier 1 — Preferred (browser-accessible)

| Source | URL Pattern | Notes |
|--------|-------------|-------|
| 36氪 (36kr.com) | `https://36kr.com/search/articles/{keyword}` | **Primary source** — search pages accessible via browser; article URLs only in rendered DOM (use `browser_console`). RSS at `/feed` returns 30 items but zero drone results. Newsflash (`/newsflashes`) has real-time 快讯 but infrequent drone items. |
| 澎湃新闻 | `https://www.thepaper.cn/` | Chinese general news, accessible |
| 观察者网 | `https://www.guancha.cn/` | Chinese news, often accessible |

## Known Unreachable Sites

These sites are **unreachable** from this environment — do not waste time retrying:
- `81uav.cn` — connection refused
- `uav168.com` — connection timeout
- `uav321.com` — connection timeout
- `uavvision.top` — DNS resolution failure
- `yuchenw.com` — returns unrelated server content, encoding issues
- `dronebigs.com` — DNS resolution failure
- `df3000.com` — connection timeout
- `uav.huanqiu.com` — returns JS-redirect skeleton (~12KB), not content
- `www.ithome.com` — returns ~2KB, no content
- `www.163.com/search` — JS-redirect to 404
- `news.163.com` — JS-blocked

Full validated list: `references/chinese-drone-media-status.md`

## Workflow

### Step 0: Fallback when no web backend is configured

If `hermes tools` shows no web provider configured, `web_search_tool` and `web_extract_tool` are unavailable. However, `browser_navigate` and `browser_console` **do not** require a web backend — the 36kr workflow works without any configuration.

Fallback only when browser is also unavailable:
1. **Bing HTML search** — `https://cn.bing.com/search?q=关键词` returns ~100–180KB of structured HTML
2. **RSS feeds** — only useful if the feed is known to contain the target topic. For drone news, 36kr RSS (https://36kr.com/feed) yields zero drone results — do NOT rely on it

### Step 1: Identify today's date

```bash
date "+%Y年%m月%d日"
```

### Step 2: Search 36kr for target keywords (browser — PRIMARY method)

**Critical**: 36kr search result pages render article URLs (`/p/{id}`) **only in the JavaScript-rendered DOM** — they are NOT present in static HTML. You MUST use `browser_console` to extract them.

1. `browser_navigate` to `https://36kr.com/search/articles/{keyword}`
2. Run in `browser_console` to extract article URLs:
```javascript
(() => {
  const links = Array.from(document.querySelectorAll('a'));
  return links.filter(a => a.href.includes('/p/')).map(a => ({
    href: a.href,
    text: a.innerText.substring(0, 80)
  })).slice(0, 20);
})()
```

Key drone keywords: `低空经济`, `无人机`, `eVTOL`, `大疆`, `植保`, `货运无人机`

### Step 3: Extract article content

After `browser_navigate` to `36kr.com/p/{id}`:
1. Use `browser_snapshot(full=true)` first — article text is already in the accessibility tree
### Article content extraction

After `browser_navigate` to `36kr.com/p/{id}`, **use `browser_snapshot(full=true)` first** — the article body is already in the accessibility tree and is sufficient for most articles.

Only fall back to `browser_console` JS when `browser_snapshot` is truncated:

```javascript
(() => {
  const article = document.querySelector('article') || document.querySelector('.article-content') || document.querySelector('[class*="content"]');
  let text = '';
  if (article) text = article.innerText;
  else {
    const paragraphs = document.querySelectorAll('p');
    paragraphs.forEach(p => { text += p.innerText + '\n'; });
  }
  const title = document.querySelector('h1')?.innerText || document.title;
  return {title, text: text.substring(0, 3000)};
})()
```

**Rule of thumb**: `browser_snapshot(full=true)` first. `browser_console` only when snapshot is truncated or missing article body.

### Step 4: Check 36kr Newsflash for real-time updates
### Step 5: Format the briefing (user-specified format — follow exactly)

Target format (user requirement):
```
📰 **无人机行业早报** YYYY年MM月DD日

**【分类】标题（核心事实，1-2句）**

**【分类】标题（核心事实，1-2句）**

**【分类】标题（核心事实，1-2句）**
```

Rules:
- Header: `📰 **无人机行业早报** YYYY年MM月DD日`（用 `date "+%Y年%m月%d日"`）
- **总输出不超过500字（中文）** — 每条只写1-2句核心事实，不要展开描述
- **3-5条**资讯，按重要性排序
- 分类标签用：**技术突破**、**行业应用**、**政策动态**、**市场数据**、**行业洞察**
- 每条格式：`**【分类】标题**` 换行后跟1-2句事实概述，不要加 `来源：` 行
- **只回复资讯内容，不要任何说明、前缀或结语** — 直接从标题行开始输出

## Limitations

- **36kr search page**: Shows ~8 results per page; scroll or reload to see more
- **Do not rely on search snippets**: Navigate to article pages for full content
- **Language**: User expects Chinese output

## Pitfalls

- **eVTOL search page may yield empty `/p/` list from `browser_console`** even when articles are visible in the accessibility snapshot. Some 36kr keyword search result pages (notably `eVTOL`) lazy-load article links only after scroll or user interaction — `browser_console` returns 0–1 results while the snapshot shows 8. Workaround: switch to the broader `低空经济` keyword, which surfaces the same eVTOL articles plus more. Always verify `browser_console` returns 5+ URLs before proceeding; if <3, try a different keyword or `低空经济` as fallback.
- **Do not retry unreachable sites**: The list above was validated across many attempts — accept sites as down
- **Do not use simple HTTP requests for Baidu**: Page is JS-rendered; use browser tools or 36kr search
- **Date format**: Use `date "+%Y年%m月%d日"` for correct Chinese date format
- **Encoding errors**: Always decode with `errors='replace'` to avoid `UnicodeDecodeError` crashes
- **RSS may return HTML (404)**: Valid RSS is typically >1KB with `<item>` tags visible. Responses <2KB are error/redirect pages.
