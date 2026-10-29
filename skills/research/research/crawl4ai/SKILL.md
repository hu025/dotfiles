---
name: crawl4ai
description: Crawl4AI — LLM友好网页爬虫，支持自适应爬取、MCP服务器、Markdown输出、RAG管道。触发词：网页爬取/AI爬虫/llm友好的网页抓取/Deep crawl/Adaptive crawling
version: 1.0.0
category: research
metadata:
  hermes:
    tags: [Web Scraping, LLM, RAG, MCP, Adaptive Crawling, AI Agent]
    related_skills: [scrapling, duckduckgo-search, domain-intel]
    homepage: https://github.com/unclecode/crawl4ai
    github_stars: "65k+"
prerequisites:
  commands: [crawl4ai, crawl4ai-setup, crawl4ai-doctor, docker]
  python_pkgs: [crawl4ai]
---

# Crawl4AI — LLM-Friendly Web Crawler (65k+ GitHub Stars)

## 核心定位

Crawl4AI 将网页转换为 LLM 可直接消费的 Markdown（而非 HTML 混乱文本），专为 RAG pipeline、Agent 动态信息获取、数据管道设计。

**与 Scrapling 的关键区别**：
- Crawl4AI = 专注 LLM 输出质量（Markdown 干净输出 + 自适应爬取停止机制）
- Scrapling = 通用网页抓取 + 反爬 + 浏览器自动化

## 核心能力

### 1. 自适应爬取（Adaptive Crawling）⭐ 2026 新特性

传统爬虫盲目爬取所有页面，自适应爬取引入智能停止机制：

```python
from crawl4ai import AsyncWebCrawler, AdaptiveCrawler

async with AsyncWebCrawler() as crawler:
    adaptive = AdaptiveCrawler(crawler)
    result = await adaptive.digest(
        start_url="https://docs.python.org/3/",
        query="async context managers"
    )
    relevant_pages = adaptive.get_relevant_content(top_k=5)
```

**三层评分系统**：
- **Coverage**：收集的页面覆盖查询词程度
- **Consistency**：跨页面信息一致性
- **Saturation**：新页面是否还在增加新信息

当三个指标显示"足够信息"时自动停止，避免无效爬取。

### 2. MCP 服务器（v0.8+ 内置）

内置 MCP server，AI Agent 可直接通过 MCP 协议调用：

```bash
crawl4ai --mcp-server
# 或 Docker 部署
docker run -p 8000:8000 unclecode/crawl4ai:latest
```

### 3. LLM 提取策略

支持任意 LLM Provider（OpenAI/Anthropic/Bedrock 等）进行结构化数据提取：

```python
from crawl4ai import LLMExtractionStrategy, LLMConfig

config = LLMConfig(
    provider="openai/gpt-4o-mini",
    backoff_base_delay=5,
    backoff_max_attempts=5,
    backoff_exponential_factor=3
)

strategy = LLMExtractionStrategy(
    llm_config=config,
    instruction="Extract table data",
    input_format="html"  # 支持 html/markdown/fit_markdown
)
```

### 4. Deep Crawl（深度爬取）

Deep Crawl 支持：
- **Crash Recovery**：长时间爬取可暂停/恢复，`resume_state` + `on_state_change` callbacks
- **Prefetch 模式**（v0.8.5+）：跳过 Markdown 生成，5-10x 加速 URL 发现

```python
from crawl4ai import CrawlerRunConfig

config = CrawlerRunConfig(prefetch=True)  # 快速 URL 发现
```

### 5. 反爬对抗（Anti-Bot Detection，v0.8.5+）

三层自动反爬检测：
- **Tier 1**：检测已知厂商模式（Cloudflare/Akamai/DataDome/PerimeterX）
- **Tier 2**：小页面通用阻止指标
- **Tier 3**：结构完整性检查（空壳页面、JS 重页面无内容）

自动代理升级：数据中心代理 → 住宅代理 → 自定义异步函数降级

### 6. Docker API Server

安全强化（v0.9.0+）：默认关闭 + 需认证 + TLS 验证

```bash
# 启动（安全默认）
docker run -e CRAWL4AI_API_TOKEN=your_token -p 8000:8000 unclecode/crawl4ai:latest

# API 调用
curl -H "Authorization: Bearer $CRAWL4AI_API_TOKEN" \
     http://localhost:8000/md -d '{"urls": ["https://example.com"]}'
```

### 7. 安全修复（v0.9.3，2026-08-31）

关闭 5 个协调披露漏洞：PDF 路径任意文件写入、SSRF、XSS、Docker Playground token 窃取。

## 快速安装

```bash
pip install -U crawl4ai
crawl4ai-setup
crawl4ai-doctor
```

## 适用场景

| 场景 | 推荐方案 |
|------|---------|
| RAG Pipeline 批量爬取 | Crawl4AI（Markdown 输出质量最高） |
| Agent 动态信息获取 | Crawl4AI MCP Server |
| 无限深度爬取直到"足够" | AdaptiveCrawler |
| 反爬网站（Cloudflare 等） | Crawl4AI Anti-Bot Tier 架构 |
| 通用网页抓取 + 反爬 | Scrapling |

## 与现有工具关系

- **补充** `scrapling`：Scrapling 更通用（反爬+浏览器自动化），Crawl4AI 更专注 LLM 输出
- **替代** `web_search + web_extract`：需要编程的深度爬取时，用 Crawl4AI 替代
- **互补** `duckduckgo-search`：搜索发现 URL → Crawl4AI 提取内容

## 版本状态

- 最新稳定版：v0.9.3（2026-08-31，安全修复版）
- GitHub Stars：65k+，最受欢迎的 AI 友好爬虫
- MCP Server：v0.8+ 内置
- Cloud API：封闭 Beta 中（2026-09）
