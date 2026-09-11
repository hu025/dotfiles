---
name: playwright-mcp
description: Microsoft Playwright MCP — AI浏览器自动化，accessibility tree替代截图，35K stars Apache-2.0，2026-09最新v0.0.79
---

# Playwright MCP 浏览器自动化技能（v0.0.79 · 2026-09）

## 核心数据
- **GitHub**: github.com/microsoft/playwright-mcp
- **stars**: 35.7K+（2026-09）
- **License**: Apache-2.0
- **下载量**: ~6.15M npm downloads/周
- **当前版本**: v0.0.79（2026-08，Playwright 1.62）
- **核心差异**: accessibility tree 而非截图 — token高效+确定性

## 架构设计

**核心洞察**：传统方法要么让 agent 写 CSS selector（脆弱），要么给 vision model 截图（贵+非确定性）。Playwright MCP 暴露 ~40-50 工具，agent 通过 accessibility snapshot 中的稳定 ref ID（如 `ref="e42"`）定位元素。

```
AI Agent → MCP Server → Playwright API → Chromium/Firefox/WebKit
```

**MCP vs CLI 选择**（官方推荐）：
- **MCP**：探索式、自我修复、长时自主会话
- **CLI**（@playwright/cli）：高吞吐 coding agent 工作流，4x 更少 token

## 安装

```bash
npx @playwright/mcp@latest                    # 快速安装
hermes mcp add playwright npx @playwright/mcp@latest  # Hermes

# Claude Code
claude mcp add playwright npx @playwright/mcp@latest

# Cursor
# Settings → MCP → Add new MCP Server → command: npx @playwright/mcp@latest

# Junie
# ~/.junie/mcp/mcp.json
{
  "mcpServers": {
    "Playwright": { "command": "npx", "args": ["-y", "@playwright/mcp@latest"] }
  }
}
```

## 核心工具（Core Tools）

| 工具 | 说明 |
|------|------|
| `browser_navigate` | 导航到 URL，支持非2xx状态码返回 |
| `browser_navigate_back` | 后退 |
| `browser_snapshot` | 捕获 accessibility tree（主视窗方式） |
| `browser_click` | 按 ref ID 点击（非坐标） |
| `browser_type` | 按 ref ID 输入 |
| `browser_fill_form` | 一次性填充多个表单字段 |
| `browser_select_option` | 下拉选择 |
| `browser_hover` | 悬停 |
| `browser_drag` | 拖拽 |
| `browser_press_key` | 键盘事件（Enter/Escape等） |
| `browser_take_screenshot` | 截图（支持 scale/CSS-device-pixel/WebP 格式） |
| `browser_evaluate` / `browser_run_code` | 执行 JavaScript / Playwright 代码 |
| `browser_file_upload` | 文件上传 |

## 新增工具（v0.0.74+ 2026）

| 工具 | 版本 | 说明 |
|------|------|------|
| `browser_find` | v0.0.78 | 正则/文本搜索 accessibility snapshot，定位元素（比全量 snapshot 便宜） |
| `browser_generate_locator` | v0.0.79 | 将 ref ID 转为稳定的 Playwright locator |
| `browser_verify_element_visible` | v0.0.79 | 验证元素可见性 |
| `browser_video_show_actions` | v0.0.76 | 录制视频叠加操作标注 |
| `browser_video_hide_actions` | v0.0.76 | 隐藏视频操作标注 |
| `browser_list_tabs` | 2026新 | 列出所有标签页 |
| `browser_switch_tab` | 2026新 | 切换标签页 |
| `browser_close_tab` | 2026新 | 关闭标签页 |

## CLI 模式（Playwright CLI）

```bash
npx playwright install --with-deps        # 安装浏览器
playwright show-trace trace.zip          # 调试 trace

# CLI+Skills 工作流（推荐 coding agent）
npx @playwright/cli@latest generate-locator e21   # ref → 稳定 locator
npx @playwright/cli@latest run-code verify.ts     # 运行前验证代码片段

# 浏览器录制
npx @playwright/cli@latest open https://example.com
# → 录制并导出 Playwright 测试代码
```

## 版本历史（2026 重要版本）

| 版本 | 日期 | 关键更新 |
|------|------|----------|
| v0.0.79 | 2026-08 | locator生成器 + screenshot WebP + codegen多语言(JS/Python/Java/C#) + settle delay |
| v0.0.78 | 2026-07-09 | `browser_find`搜索 + 更少噪音的distilled snapshots + --mobile/--device模拟 |
| v0.0.77 | 2026-06-29 | screenshot缩放选项(CSS vs device px) + 心跳超时可配置 + 敏感信息过滤 |
| v0.0.76 | 2026-06-10 | 视频操作标注 + output-max-size限制 + Firefox BiDi |
| v0.0.75 | 2026-05-07 | 共享浏览器隔离启动 + extension CDP命令转发 |
| v0.0.74 | 2026-05-06 | extension模式多标签管理 |

## 配置选项

```bash
# 基础
npx @playwright/mcp@latest --headless                    # 无头（默认）
npx @playwright/mcp@latest --browser chromium|firefox|webkit

# 能力扩展
--caps=vision,pdf,testing                               # 启用额外能力

# 截图选项
--screenshot-scale css|device                           # CSS像素 vs 设备像素

# 移动端模拟
--mobile                                                  # 启用移动UA
--device="iPhone 15 Pro"                                 # 设备型号

# 输出限制
--output-max-size 1024000                               # 字节，防止超大响应

# HTTP server 模式
npx @playwright/mcp@latest --port 8080
```

## Playwright MCP vs browser-use 对比

| 维度 | Playwright MCP | browser-use |
|------|---------------|-------------|
| 页面表示 | Accessibility tree | 视觉/screenshot |
| Token 消耗 | 低（~200-400/snapshot） | 高（screenshot视窗） |
| 确定性 | 高（ref ID稳定） | 低（坐标/pixel） |
| 适用场景 | 精确UI交互 | 复杂视觉理解 |
| 免费 | 完全免费（MIT） | 开源免费，云服务付费 |
| Agent 支持 | 所有MCP客户端 | 专用Python/CLI |
| 安全 | `isolated`模式必须用 | 沙箱隔离可选 |

## 安全使用

⚠️ **默认权限极大**：`browser_run_code_unsafe` + 已登录Chrome = 完整系统访问能力。

```bash
# 高风险：私人数据 + 不可信内容 + exfiltration通道
# 必须用 isolated 或 docker 配置文件

# isolated 模式（推荐）
npx @playwright/mcp@latest --isolated

# Docker 模式
docker run -p 8080:8080 mcp/playwright-mcp
```

## 基准测试结果

- **WebVoyager**: 使用 accessibility tree 方法在多个基准上表现 SOTA
- **token 效率**：相比 screenshot 方法节省 ~10x token
- **下载量**：6.15M/周（npm），远超其他 MCP server

## 来源链接
- GitHub: https://github.com/microsoft/playwright-mcp
- Releases: https://github.com/microsoft/playwright-mcp/releases
- Docs: https://playwright.dev/docs/getting-started-mcp
- MCP Directory: https://mcp.directory/server/playwright
