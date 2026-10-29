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

## 快速启动 CDP 浏览器

```bash
# 1. Chromium 已在系统路径（/usr/sbin/chromium），无需额外安装
/usr/sbin/chromium --version

# 2. 启动 headless chromium + CDP 调试端口
/usr/sbin/chromium --headless=new --remote-debugging-port=9222 --no-sandbox --disable-gpu --disable-dev-shm-usage

# 3. 验证连接（不是 ws://！是 http://）
BU_CDP_URL=http://127.0.0.1:9222 browser-harness << 'PY'
print(page_info())
PY
# 期望: {'url': 'chrome://newtab/', 'title': ..., 'w': ..., 'h': ...}
```

**在 Hermes 中使用 browser_exec 工具**：直接调用即可，browser_exec 已内置 BU_CDP_URL 环境变量。

**Pitfall**: 使用 `ws://127.0.0.1:9222` 会报错 `unreachable after 30s: <urlopen error unknown url type: ws>`，必须填 `http://`。

**Pitfall**: `browser-use doctor` 在连接真实浏览器时输出不准确，用 `browser-harness <<'PY'

**常见错误：**
- `ws://...` → 错误 `unreachable after 30s: <urlopen error unknown url type: ws>`，必须填 `http://host:port`
- Hermes venv 中命令是 `browser-harness` 而非 `browser-use`
- `import langchain` FAIL → browser-use Python Agent 模式不可用，需单独安装 `langchain langchain_community`
print(page_info())
PY` 验证才是金标准。

#### 三条互不相干的坑：二进制名、浏览器发现、后台启动

**① `browser-use` 和 `browser-harness` 是两个不同的二进制，不在一个 venv 里**

| 命令 | 由谁提供 | 用途 |
|---|---|---|
| `browser-use` | `browser_use` 包 | 旧版 CLI（`browser-use open <url>` 等） |
| `browser-harness` | `browser_harness` 包 | 新版 Rust harness 封装，Hermes 实际用这个 |

两者经常不在同一个 site-packages 里。**跑之前先确认二进制存在**，
不要假设装了 `browser-use` 就有 `browser-harness`（或反过来）：

```bash
for v in ~/.hermes/hermes-agent/.venv ~/.hermes/hermes-agent/venv ~/.hermes/hermes-agent/venv_new; do
  [ -d "$v/bin" ] && echo "$v: $(ls $v/bin | grep -E '^(browser-use|browser-harness)$' | tr '\n' ' ')"
done
```

**② 浏览器发现机制：`BU_CDP_URL` 是可靠路径，自动发现不是**

harness 的 daemon 会先扫**浏览器默认 profile 目录**下的 `DevToolsActivePort`
文件（`~/.config/chromium`、`~/.config/google-chrome` 等），扫不到才 fallback 到
9222/9223 端口。因此：

- **可靠做法**：显式设 `BU_CDP_URL=http://127.0.0.1:9222`（注意是 `http://` 不是 `ws://`）
- **自动发现失效的典型原因**：浏览器是用自定义 `--user-data-dir` 启动的，
  于是 `DevToolsActivePort` 被写到了那个自定义目录而不是默认 profile 目录，
  daemon 扫不到 → 报 `chrome-not-running: no supported Chromium-family browser is running`
- **Hermes 自带浏览器会注入 `--incognito --user-data-dir=<scratch>`**，
  所以 Hermes 的 `browser_exec` 与独立跑的 harness CLI 会互相“看不见”对方，
  两套同时用同一端口时容易互抢 profile

**③ 后台启动浏览器：用 `background=true`，不要用 shell 包裹符**

```bash
# ✗ 终端工具会拦截（"uses shell-level background wrappers"），且进程会随 shell 退出
nohup chromium ... & disown
setsid chromium ... &

# ✓ 终端工具自己跟踪
terminal(background=True, command="exec chromium --headless=new --remote-debugging-port=9222 ...")
```

启动后**必须等几秒再验证**，Chromium 起来需要时间绑定端口：

```bash
sleep 8
curl -s -m 5 http://127.0.0.1:9222/json/version | head -3
```

**验证的黄金标准**是实际拉一个页面，而不是看 doctor 输出：

```bash
BU_CDP_URL=http://127.0.0.1:9222 browser-harness <<'PY'
ensure_real_tab()
print(page_info())
PY
```

`browser-use doctor` 会报 `[FAIL] daemon alive` / `[FAIL] active browser connections`
即使一切正常（它检查的是常驻 daemon，而 CLI 每次会现拉一个），
**不要把 doctor 的 FAIL 当成不可用**。

**多 Chrome 实例隔离方案：**
- 每个浏览器实例用独立 `--remote-debugging-port`（如 9222/9223/9224）
- 不同 session 的 daemon 指向不同端口即可

**④ 要常驻就用 systemd user service，不要靠 terminal(background=True)**
`terminal(background=True)` 起的浏览器挂在 `hermes-worker-proc_*.scope` 下：session 结束会被清理，gateway 重启后也不会自动拉起。要常驻就写 user unit：

```ini
# ~/.config/systemd/user/hermes-browser-cdp.service
[Unit]
Description=Hermes CDP Chromium - dedicated browser for browser-use CLI
After=network.target
[Service]
Type=simple
Environment=BU_CDP_PORT=9223
ExecStart=/home/saber/.hermes/scripts/start_browser_cdp.sh --headless
Restart=always
RestartSec=3
TimeoutStopSec=20
KillMode=mixed
[Install]
WantedBy=default.target
```
```bash
systemctl --user daemon-reload && systemctl --user enable --now hermes-browser-cdp.service
```
换端口时先 `kill` 旧实例再 `systemctl --user start`（端口被占会让新实例 bind 失败）。
**端口不能和 Hermes 自带浏览器抢**：Hermes 的 `browser_exec` 占用 9222，专用实例用 9223。

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

## 补自旧副本的独有内容（browser-use，合并于 2026-10-29）

- **架构**: 已从 Playwright 切换到纯 CDP（Rust Browser Harness）
### ⚠️ 关键：连接已运行的 Chrome（含远程调试端口）
# 在 Hermes 中用 background=true 启动（不要用 nohup/disown 包裹前台命令）
browser-use daemon 不会自动发现已有的 Chrome 调试端口，**必须通过环境变量指定**：
# 1. 启动 Chrome 带调试端口（用 terminal(background=True)，不要用 & 包裹）
#    浏览器进程必须脱离当前 shell，否则 shell 退出时进程被杀、CDP 端口随之消失
# 2. 设置环境变量（重要：不是 ws://，是 http://）
export BU_CDP_URL=http://127.0.0.1:9222
自己写的 wrapper 若像下面这样生成代码，就只是把任务字符串打印出来，
却返回 `ok: true` —— 一个**假成功**，会让人以为浏览器路径是通的：
code = f"ensure_real_tab()\nprint({task!r})"
正确做法是生成真正导航 + 抽取的代码，并用哨兵前缀回传结构化结果：
code = ("new_tab(%r)\nwait_for_load()\n" % url
+ "_data = _json.loads(js(" + repr(js_code) + "))\n"
+ "print('__BA_RESULT__' + _json.dumps(_data, ensure_ascii=False))\n")
Python 端解析 `__BA_RESULT__` 前缀那行拿 JSON；**解析不到就要返回 ok=False**，
**⑥ 本机 chromium 会被强制注入 `--user-data-dir=/tmp/org.chromium.Chromium.scoped_dir.XXX --incognito`**
即使自己显式指定默认 profile 也会被改写，所以 `~/.config/chromium/DevToolsActivePort`
**永远不会出现** —— 不要指望自动发现路径可用，直接用 `BU_CDP_URL`。
