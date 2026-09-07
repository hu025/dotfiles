---
name: browser-use
description: AI浏览器自动化：browser-use库控制真实浏览器完成网页任务，支持多LLM(MiniMax/Claude/GPT)，MIT开源，108K stars
---

# browser-use 浏览器自动化技能

## 核心数据
- **GitHub**: github.com/browser-use/browser-use
- **stars**: 110K+（2026）
- **License**: MIT
- **Python**: >= 3.11

## 安装
```bash
pip install "browser-use[core]"   # 含 Rust 运行时
uv add browser-use               # 推荐用 uv
```

## 与 Hermes 集成（浏览器控制模式）
browser-use 已被 Hermes 内置为 browser_exec 工具。
如需更精细控制，可通过 Python 脚本调用：

```python
from browser_use.beta import Agent, BrowserProfile, ChatBrowserUse
import asyncio

async def browse_task(task: str):
    agent = Agent(
        task=task,
        llm=ChatBrowserUse(model='anthropic/claude-sonnet-4-6'),
        browser_profile=BrowserProfile(headless=False)
    )
    history = await agent.run()
    return history.final_result()
```

## 关键特性
- Agent循环：观察→推理→执行→评估
- 多步规划（enable_planning=True）
- 循环检测（重复动作/页面停滞）
- 支持 Playwright/Puppeteer/Selenium CDP
- 记忆系统（history.final_result()）
- 错误恢复（max_failures 重试）
- 思维模式（use_thinking=True）
- 1000+ 集成（Gmail, Slack, Notion等）
- Cloud API：stealth浏览器 + proxy轮换 + CAPTCHA处理

## MCP Server生态（2026新增）
- **mcp-browser-use** (Saik0s): browser-use封装为MCP server → Claude/任意MCP客户端可调用
  `pip install mcp-browser-use`
- **BrowserMCP** (browsermcp): 复用用户本地浏览器profile，避免bot检测，隐私优先
  `pip install browsermcp`
- **WebMCP**: Chrome 149 origin trial，AI agent通过MCP协议控制浏览器

## Benchmark（2026）
- WebVoyager: browser-use 89.1% > OpenAI CUA 87% > Comet 87%
- WebArena: Comet > browser-use（复杂多站任务）
- Odysseys: browser-use #1（87.4% accuracy）

## Chrome DevTools for agents（2026）
Chrome DevTools新增agent调试支持：console logs / network / accessibility tree实时可见。
现已支持browser-use等20+ coding agent。

## CLI 快速使用
```bash
browser-use open https://example.com   # 打开网页
browser-use state                      # 查看可点击元素
browser-use click 5                    # 点击元素5
browser-use type "hello"              # 输入文字
browser-use screenshot page.png       # 截图
browser-use close                     # 关闭
```

## Skill 安装（已有agent如Claude Code/Codex/Cursor）
```
Install or upgrade browser-use to the latest stable version with uv using Python 3.12, run `browser-use skill install` to register the skill, and connect it to my browser.
```

## 最佳实践
1. headless=False 用于调试，True 用于生产
2. allowed_domains 限制权限
3. max_failures=3 防止死循环
4. enable_planning=True 用于复杂多步任务
5. 与 MiniMax/GPT/Claude 均可配合
