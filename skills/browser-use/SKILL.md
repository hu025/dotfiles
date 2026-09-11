---
name: browser-use
description: AI浏览器自动化：browser-use库控制真实浏览器完成网页任务，支持多LLM(MiniMax/Claude/GPT)，MIT开源，113K stars，CLI 3.0 + Rust后端
---

# browser-use 浏览器自动化技能（v0.13.10+ · 2026-09）

## 核心数据
- **GitHub**: github.com/browser-use/browser-use
- **stars**: 106K+（2026-09）
- **License**: MIT
- **Python**: >= 3.11（推荐 3.12）
- **当前版本**: v0.13.10+（2026-09）
- **架构**: Python API → Rust core → CDP Browser Harness

## 安装
```bash
uv add browser-use              # 推荐用 uv
pip install browser-use         # 或 pip
browser-use doctor             # 验证安装
```

## Browser CLI 模式（2026 新增）
| 模式 | 命令 | 说明 |
|------|------|------|
| Headless | `browser-use open <url>` | 默认，快速不可见 |
| Headed | `browser-use --headed open <url>` | 可见窗口调试 |
| Real Chrome | `browser-use --profile "Default" open <url>` | 使用已有登录/cookies |
| Connect | `browser-use --connect open <url>` | 附加到运行中的Chrome |
| CDP URL | `browser-use --cdp-url ws://... open <url>` | 连接任意CDP浏览器 |
| Cloud | `browser-use cloud connect` | 云浏览器+代理 |

**连接已运行的Chrome（无需重新登录）：**
```bash
browser-use --connect open https://github.com      # 自动发现CDP
browser-use --profile "Default" open https://gmail.com  # 直接用已有profile
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

## v2026 新特性（与旧技能对比）
| 特性 | 旧版 | 新版（2026） |
|------|------|-------------|
| 渲染引擎 | Playwright | 纯 CDP + Rust Harness |
| 性能 | 较慢 | 2-3x 提升 |
| JavaScript | 不支持 | Agent 可编写并执行 JS |
| 云浏览器 | V1 API | V4 API + X402 计费 |
| Agent | Python only | Python + Rust beta agent |
| 集成 | 1000+ | 1000+ + AgentMail |
| 免费额度 | 付费 | Free tier 含 scheduled tasks |

## 关键新功能

### 1. JavaScript 执行
Agent 可直接在页面中编写和执行 JavaScript，实现精确控制和复杂交互：
```python
from browser_use import Agent
agent = Agent(task="提取所有商品价格", llm=llm)
```

### 2. Cloud SDK（V4 API）
```python
from browser_use_sdk.v4 import BrowserUse
client = BrowserUse(api_key="bu_...")
run = client.runs.create("任务描述", model="grok-4.5")
result = client.runs.wait_for_completion(run.id)
```

### 3. MCP Server 集成
browser-use 可作为本地 MCP server，暴露浏览器自动化能力给所有 MCP 兼容客户端。

**启动本地 MCP server：**
```bash
uvx --from 'browser-use[cli]' browser-use --mcp
```

**Claude Desktop 配置（~/.config/Claude/claude_desktop_config.json）：**
```json
{
  "mcpServers": {
    "browser-use": {
      "command": "uvx",
      "args": ["--from", "browser-use[cli]", "browser-use", "--mcp"],
      "env": { "OPENAI_API_KEY": "your-key" }
    }
  }
}
```

**Cursor（~/.cursor/mcp.json）：**
```json
{
  "mcpServers": {
    "browser-use": {
      "command": "uvx",
      "args": ["--from", "browser-use[cli]", "browser-use", "--mcp"],
      "env": { "OPENAI_API_KEY": "your-key" }
    }
  }
}
```

**Hosted MCP server（云端，无需本地安装）：**
```bash
# Claude Code
claude mcp add --transport http browser-use https://api.browser-use.com/mcp

# Claude Desktop
npx mcp-remote https://api.browser-use.com/mcp \
  --header "X-Browser-Use-API-Key: your-api-key"
```

**环境变量：**
| 变量 | 说明 |
|------|------|
| OPENAI_API_KEY | OpenAI API key（必需） |
| ANTHROPIC_API_KEY | Anthropic API key（替代方案） |
| BROWSER_USE_HEADLESS | false=显示浏览器窗口 |
| BROWSER_USE_DISABLE_SECURITY | true=禁用浏览器安全特性 |
| BROWSER_USE_MCP_SESSION_TIMEOUT_MINUTES | 会话超时（默认10分钟） |

**新增 MCP 工具（2026新增，未在旧技能中列出）：**
| 工具 | 说明 |
|------|------|
| browser_get_html | 获取页面原始HTML，可指定CSS选择器 |
| browser_list_tabs | 列出所有打开的标签页 |
| browser_switch_tab | 切换到指定标签页 |
| browser_close_tab | 关闭指定标签页 |
| browser_list_sessions | 列出所有活跃会话 |
| browser_close_session | 关闭指定会话 |
| browser_close_all | 关闭所有会话 |
| browser_extract_content | 从页面提取结构化内容 |
| retry_with_browser_use_agent | 回退到AI agent执行复杂任务（最后手段） |

**MCP 作为客户端（调用其他 MCP 工具）：**
browser-use 还可以作为 MCP client，动态注册外部 MCP 工具（如 filesystem、database）作为 browser-use action：
```python
from browser_use.mcp import MCPClient, MCPToolWrapper
```

### 4. Scheduled V4 Agents
V4 agent 支持定时任务（pause/resume），可自动化周期性工作。

### 5. Agency Skill
主动研究模式：Agent 主动研究、准备、返回后续问题，仅在外部操作前请求批准。

### 6. Session Sharing
通过 `/share/v4` 链接分享会话，支持拇指反馈。

### 7. X402 定价
管理已有会话免费（轮询/读取/停止），仅开新浏览器收费。

## Cloud API 定价（2026-08 更新）
- Proxy 数据：$5/GB（原价 $10/GB）
- 最小充值：$5（原价 $25）
- Free tier 含 scheduled tasks（1小时最小间隔）
- BYOK 缓存读取按折扣价（非全价）

## 新增发现（2026-09 更新）

### 1. v0.13 Rust Core Beta Agent
Browser Use 0.13 引入全新 Rust 后端 beta agent，架构：
```
Python API → Rust core → Browser Harness → Web task done
```
- `from browser_use.beta import Agent`（新 beta agent）
- `from browser_use import Agent`（旧版 Python agent，保留不变）
- 适配当前前沿模型，提供更直接的浏览器控制循环

### 2. BU 3.0 基准测试（2026-09）
- BU 3.0 在 100 个真实浏览器任务上达到 **SOTA**：
  - **WebVoyager**: 89.1% 成功率
  - **Browser Use 内部 benchmark**: 对标主要竞品
- 基准测试完全开源：github.com/browser-use/benchmark（131 stars）

### 3. Stealth Browser Infrastructure（2026 新增）
内置反反爬能力：
- Cloudflare / DataDome / PerimeterX 等反Bot保护自动绕过
- 真实浏览器指纹（TLSJA3/4、HTTP/2）
- CAPTCHA 处理（Cloudflare Turnstile）
- Proxy 轮换支持 195+ 国家
- 免费加入：$0.02/browser-hour 起

### 4. 性能突破（20 steps/minute）
- 自研 LLM Gateway 降低 6x 延迟
- BU 2.0：+12% 准确率，同等速度
- BU 3.0（最新）：精度再提升

## 新模型支持（2026）
- Grok 4.5 (xAI)
- Kimi K3 (MoMoonshot)
- Claude Fable 5
- GLM / MiniMax 原生支持
- bu-2-0-mini-preview
- bu-3-max（最新旗舰）

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
6. 不暴露 agent 的控制面或 Chrome CDP 端口到公网
7. 浏览不可信站点时需要确认再执行购买/发布等操作
