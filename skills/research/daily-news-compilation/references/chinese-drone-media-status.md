# Chinese Drone & Aviation Media Site Status

Validated by repeated testing from this environment (2025–2026).

## Unreachable ❌

| Site | URL | Issue |
|------|-----|-------|
| 81uav | 81uav.cn | Connection refused |
| UAV168 | uav168.com | Connection timeout |
| UAV321 | uav321.com | Connection timeout |
| UAV Vision | uavvision.top | DNS resolution failure |
| 宇辰网 | yuchenw.com | Returns unrelated server content; encoding error |
| DroneBigs | dronebigs.com | DNS resolution failure |
| DF3000 | df3000.com | Connection timeout |
| Diditimes | diditimes.com | Connection failure / 0 bytes |
| 无人机网 | uav51.net | Connection refused |
| 通航圈 | tonghangtai.com | Connection refused |
| 临云行 | linyunxing.com | Connection refused |
| 无人机之家 | uav.cc | Connection refused |
| 环球网低空经济频道 | uav.huanqiu.com | JS-redirect skeleton (~12KB); no content |
| IT Home (main) | ithome.com | Returns ~2KB only; no usable content |
| 网易新闻搜索 | news.163.com | JS-blocked / 404 |
| 新华网搜索 | so.news.cn | Returns empty or 404 |
| cnBeta RSS | cnbeta.com | 0 bytes |
| 新浪搜索 | tech.sina.com.cn | HTTP 403 |
| 知乎 | zhihu.com | HTTP 403 |
| 虎嗅 RSS | huxiu.com | Timeout |
| 极客公园 RSS | geekpark.net | HTTP 404 |
| 百度搜索 | baidu.com | JS/CAPTCHA blocking |
| 无人机网 | www.uavb.cn | Connection refused |
| 低空经济网 | www.dikongjj.com | Accessible but no drone-specific content |
| 低空经济网 (alt) | dikongjingji.com.cn | Partially accessible |

## Accessible ✅

| Site | URL | Notes |
|------|-----|-------|
| 36氪 | 36kr.com | **Primary drone source** — search pages via browser; RSS yields zero drone items |
| 澎湃新闻 | thepaper.cn | Main page accessible (~55KB) |
| 观察者网 | guancha.cn | Accessible |
| 智东西 | zhidx.com | RSS ~2.7KB; limited drone content |
| 爱范儿 | ifanr.com | RSS at /feed; 20+ items, filter by keyword |

## RSS Feeds Tested (2025–07, updated 2026-08)

| Feed | Status | Drone Items |
|------|--------|-------------|
| 36kr /feed | ✅ Works | **0 items** — do NOT rely on it |
| 爱范儿 /feed | ✅ Works | 0 drone items |
| 智东西 /feed | ✅ Small | No drone items |
| IT Home /rss | ✅ Works | 60 items, 0 drone |
| 量子位 /feed | ✅ Works | 10 items, 0 drone |

## `ddgs` CLI — Primary Fallback for Chinese Drone News

**`ddgs` CLI is available in the shell (`/home/saber/.local/bin/ddgs`) and is the fastest path for Chinese drone news without browser automation.**

### Quick Reference: Drone Briefing Commands

```bash
# Industry news
ddgs text -q "2026年8月 无人机 行业新闻" -m 10 -t m -r zh-cn 2>/dev/null

# Policy + low-altitude economy
ddgs text -q "无人机 政策 低空经济 开放 空域 2026年" -m 10 -t m -r zh-cn 2>/dev/null

# DJI new products
ddgs text -q "大疆 新品 Air 3S Flip Neo 2026" -m 8 -t m -r zh-cn 2>/dev/null

# eVTOL + commercial applications
ddgs text -q "eVTOL 无人机 订单 交付 2026" -m 8 -t m -r zh-cn 2>/dev/null

# Agriculture + logistics
ddgs text -q "无人机 农业植保 物流 配送 2026" -m 6 -t m -r zh-cn 2>/dev/null
```

| Flag | Meaning |
|------|---------|
| `-q` | Query (required) |
| `-m` | Max results |
| `-t m` | Time: d=day, w=week, m=month |
| `-r zh-cn` | Region filter |
| `2>/dev/null` | Suppress stderr |

### Limitations
- Returns titles + snippets (~200 chars), NOT full article text
- For full content: `curl` the `href` URL + `grep -oP '(?<=<p>)[^<]+'`

### Installation Check
```bash
command -v ddgs   # Returns path if available
pip show ddgs     # Check version
```

## 36kr Browser Workflow (Secondary)

### Search page — URLs in JS-rendered DOM only
- `https://36kr.com/search/articles/{keyword}`
- Key keywords: `低空经济`, `无人机`, `eVTOL`, `大疆`, `峰飞航空`

### Extract URLs (browser_console)
```javascript
(() => {
  const links = Array.from(document.querySelectorAll('a'));
  return links.filter(a => a.href.includes('/p/')).map(a => ({
    href: a.href, text: a.innerText.substring(0, 80)
  })).slice(0, 20);
})()
```

### Extract article content (browser_snapshot first, then console fallback)
```javascript
(() => {
  const article = document.querySelector('article') || document.querySelector('.article-content');
  let text = article ? article.innerText : '';
  if (!text) { const ps = document.querySelectorAll('p'); ps.forEach(p => { text += p.innerText + '\n'; }); }
  const title = document.querySelector('h1')?.innerText || document.title;
  return {title, text: text.substring(0, 3000)};
})()
```

### ⚠️ eVTOL search pitfall
The 36kr `/search/articles/eVTOL` page returns 0–1 URLs from `browser_console` even when 8 articles are visible in the snapshot. Use `低空经济` instead. If `browser_console` returns <3 URLs, switch keywords.

## Keyword Sets

**Primary**: `无人机`, `eVTOL`, `低空经济`, `大疆`, `植保`, `货运无人机`, `无人矿卡`
**Broader**: `飞行器`, `航空`, `快递`, `巡检`, `适航`, `通航`
**Companies**: `亿航`, `小鹏汇天`, `沃兰特`, `沃飞长空`, `峰飞航空`, `汇天`, `御风未来`, `宇树科技`, `自贡`

## Web Tools

When no web backend is configured, `browser_navigate`/`browser_console` still work (browser toolset). Only `web_search_tool`/`web_extract_tool` require a backend.