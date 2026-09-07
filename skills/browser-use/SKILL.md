---
name: browser-use
description: AI浏览器自动化：browser-use库控制真实浏览器完成网页任务，支持多LLM(MiniMax/Claude/GPT)，MIT开源，113K stars，CLI 3.0 + Rust后端
---

# browser-use 浏览器自动化技能（v0.13.10 · 2026-09）

## 核心数据
- **GitHub**: github.com/browser-use/browser-use
- **stars**: 113K+（2026-09）
- **License**: MIT
- **Python**: >= 3.11（推荐 3.12）
- **当前版本**: 0.13.10（2026-09-03）
- **架构**: 已从 Playwright 切换到纯 CDP（Rust Browser Harness）

## 安装
```bash
uv add browser-use              # 推荐用 uv
pip install browser-use         # 或 pip
browser-use doctor             # 验证安装
```

## Hermes 集成
browser-use 已被 Hermes 内置为 `browser_exec` 工具（基于 CLI 3.0）。

### browser_exec 使用示例
```python
# 浏览器执行（Hermes 内置）
# agent 编写 Python 脚本执行多步操作
new_tab("https://example.com/login")
fill("#email", email)
fill("#password", password)
click("button[type=submit]")
wait_for_text("Dashboard")
print(page_info())
```

## CLI 3.0 核心命令
```bash
browser-use auth login          # 登录 Browser Use Cloud
browser-use auth status         # 查看认证状态
browser-use doctor             # 诊断安装
browser-use skill install      # 为 Claude Code/Codex 安装 skill
browser-use open <url>         # 打开网页
browser-use state              # 查看可交互元素
browser-use click <n>          # 点击元素
browser-use type "text"        # 输入文字
browser-use screenshot <file>  # 截图
browser-use close              # 关闭
```

## v2026 新特性（与旧版对比）
| 特性 | 旧版 | 新版（2026） |
|------|------|-------------|
| 渲染引擎 | Playwright | 纯 CDP + Rust Harness |
| 性能 | 较慢 | 2-3x 提升 |
| JavaScript | 不支持 | Agent 可编写并执行 JS |
| 云浏览器 | V1 API | V4 API + X402 计费 |
| Agent | Python only | Python + Rust beta agent |
| 免费额度 | 付费 | Free tier 含 scheduled tasks |

### 1. JavaScript 执行
Agent 可直接在页面中编写和执行 JavaScript，实现精确控制和复杂交互。

### 2. Cloud SDK（V4 API）
```python
from browser_use_sdk.v4 import BrowserUse
client = BrowserUse(api_key="bu_...")
run = client.runs.create("任务描述", model="grok-4.5")
result = client.runs.wait_for_completion(run.id)
```

### 3. Scheduled V4 Agents
V4 agent 支持定时任务（pause/resume），可自动化周期性工作。

### 4. Agency Skill
主动研究模式：Agent 主动研究、准备、返回后续问题，仅在外部操作前请求批准。

### 5. Session Sharing + X402
通过 `/share/v4` 链接分享会话；管理已有会话免费，新开浏览器收费。

### 6. 新模型支持（2026）
- Grok 4.5 (xAI)
- Kimi K3 (Moonshot)
- Claude Fable 5
- GLM / MiniMax 原生支持
- bu-2-0-mini-preview

## Cloud API 定价（2026-08）
- Proxy 数据：$5/GB（原价 $10/GB）
- 最小充值：$5（原价 $25）
- Free tier 含 scheduled tasks（1小时最小间隔）
- BYOK 缓存读取按折扣价

## MCP Server 生态
- **mcp-browser-use** (Saik0s): browser-use 封装为 MCP server
  `pip install mcp-browser-use`
- **BrowserMCP** (browsermcp): 复用本地浏览器 profile，避免 bot 检测
  `pip install browsermcp`
- **browser-use-camoufox** (WebRobot): Firefox/Camoufox 隐身浏览器 fork

## Benchmark（2026）
- WebVoyager: browser-use 89.1% > OpenAI CUA 87% > Comet 87%
- WebArena: Comet > browser-use（复杂多站任务）
- Odysseys: browser-use #1（87.4% accuracy）

## Chrome DevTools for agents
Chrome DevTools 新增 agent 调试支持：console logs / network / accessibility tree 实时可见，支持 20+ coding agent。

## 关键特性
- Agent 循环：观察→推理→执行→评估
- 多步规划（enable_planning=True）
- 循环检测（重复动作/页面停滞）
- 记忆系统（history.final_result()）
- 错误恢复（max_failures 重试）
- 思维模式（use_thinking=True）
- 1000+ 集成（Gmail, Slack, Notion等）
- Cloud API：stealth 浏览器 + proxy 轮换 + CAPTCHA 处理

## 最佳实践
1. headless=False 用于调试，True 用于生产
2. allowed_domains 限制权限
3. max_failures=3 防止死循环
4. enable_planning=True 用于复杂多步任务
5. 与 MiniMax/GPT/Claude 均可配合
6. 不暴露 CDP 端口到公网
7. 浏览不可信站点时需要确认再执行购买/发布等操作
