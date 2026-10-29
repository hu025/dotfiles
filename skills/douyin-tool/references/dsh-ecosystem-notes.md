# DSH + QQ + 抖音 生态调研笔记（2026-10-29）

## 那张截图的来源

作者是「蓝色大肥鱼」（抖音号 @予…图文），GitHub 账号与仓库：

| 仓库 | 内容 |
|---|---|
| `18862258568qz-commits/deepseek-plugin-collection-bluefishovo` | **主仓库**：qq-bridge + qq-agent-presets + qq-mode-console + 人格卡 + 控制台 + 语音三链路。README 有「给别人的安装清单」 |
| `jackey670/dsh-douyin-whale` | **抖音工具层**：热榜/搜索/抽帧/原生分享卡片/受控私信 + 定时调度器 + 本地 HTTP API :7709 |
| `Derpyu520/qq-bridge` | 上游原版（3107 star），蓝色大肥鱼是 fork |
| `deepseek-ai/deepseek-harness` | DSH 本体（264773 star），默认 Web UI `http://127.0.0.1:3080` |

截图里的「5 个坑」只看清前两条：
1. **端口**：DSH 端口每次随机，配置文件要程序化同步
2. **模型**：provider 必须 `deepseek-account`，否则 407

第 3~5 条那张长截图被裁掉了。我在主仓库 `docs/guides/DSH_SETUP.md` 的「常见问题」和
`docs/README.md` 里找到了同类内容的完整版本（下面「坑位全集」）。

## 坑位全集（来自 DSH_SETUP.md 常见问题 + whale README FAQ）

1. **DSH 端口随机**：DSH Web UI 端口每次启动可能变，桥接配置要程序化同步（不能写死）。
2. **provider 必须是 `deepseek-account`**：DSH 里 DeepSeek 账号鉴权（`x-dsh-auth-token`）与 API key
   （`llm-deepseek`）是两条独立路径。用 key 走账号端点会被拒（407）。
3. **HTTP token 与 WS token 是两个不同的值**：SnowLuma 同一账号的 OneBot HTTP（默认 3000）与
   WebSocket（默认 3001）token 不同，`config.json` 的 `snowluma.accessToken` 只能存一个（HTTP 那个）。
   所以启动日志先报「连接断开（1006）」再报「已连接」是**正常的**——那是 WS token 自愈。
   真正的问题是「token 自愈失败」。
4. **`httpUrl` 指向了 WS 端口 → HTTP 426**：HTTP API 与 WebSocket 端口必须分开填。
5. **白名单 fail-closed**：`allow.private` / `allow.groups` 为空且 `allowAllWhenEmpty: false`
   ⇒ 桥接**不响应任何消息**。这是刻意设计，不是坏了。
6. **没装 DSH 端 = QQ 上毫无反应**：跳过 `setup-dsh.mjs` 时桥接不崩，但群聊/仿真会话会因为
   拿不到 `qq-chat` preset 被**拒绝建会话**（日志 `⛔ 群聊/仿真会话缺少 preset`）。
   同样 fail-closed：绝不回退到带 bash/文件工具的默认 preset。
7. **DSH 0.1.7 起启动 token 只存在内存**：每进程现生成的随机数，不落盘。旧办法（从
   `~/.dsh/guard/logs/server-*.out.log` 读 token）已失效。正确做法是用
   `~/.dsh/.credentials.yaml` 的持久化签名密钥离线铸造 Cookie。
8. **preset 机制在 0.1.7 变了**：不再是 `~/.dsh/.agent-presets/<名>/` 目录，而是 profile 里的一条
   `@deepseek-ai/dsh-agent-preset` 行，由 `plugins/qq-agent-presets` bundle 提供。
9. **`settings/update` 在 0.2.0 是多参数 RPC**：args 是 `{ ns, patch, expectedRevision }` 平铺，
   不是 `{ request: {...} }`（传 request 会被网关拒为 `gateway/arguments-invalid`）。
10. **DSH 0.1.5 起 `dsh-persona` 只接受 `prefix`/`suffix`/`complete`/`includeRuntimeContext`**：
    旧写法 `text:` 会被 schemastery 静默忽略，于是报出来的是「缺 `prefix`」。
11. **升级 DSH 可能重置 profile 的 `package.json`**：把 bundle 条目删掉，症状是启动报
    `cannot resolve profile bundle`。重跑 `setup-dsh.mjs` + `dsh plugin --profile <p> install`。
12. **QQ 上没反应但桥接说「已连接」**：几乎总是 SnowLuma 的 `[Hook]` 收不到 QQ 数据，
    不是桥接的问题。
13. **agent 预设的 `{{cwd}}` 变量在 DSH 0.2.1 被删除**：每个回合在系统提示词装配阶段直接 error，
    模型一次都不跑（QQ 侧表现为「发消息完全没反应」）。这是 bluefish 仓库 v0.2.1-r1 修的 P0。
14. **`qq-mode` 卡片不出现**：DSH 的 settings 卡片只渲染「host 半 ∩ 声明该 key 的卡片」，
    `qq-mode-console` 只有 host 半，没有浏览器半，所以卡片永远不显示。已知限制。
15. **SnowLuma 升级不会换原生组件**：`native/snowluma-win32-x64.{dll,node}` 与
    `websocket-win32-x64.node` 在 1.14.9 与 1.14.20 之间逐字节相同，变的只有 JS 层。
    所以升级能修事件流水线/收发链路，但**修不了「原生 hook 挂不上 QQ」**。

## whale（抖音层）的工程取舍 —— 值得抄的

- **只读优先**：热榜/搜索/详情/评论/下载/抽帧都不产生公开写操作；写操作默认关闭，
  评论默认 dry-run。
- **不绕过验证码**：明确写「使用本机 Edge/Chrome + 独立 profile，不使用指纹注入，
  不绕过验证码」。触发了 `challenge_required` 就停下人工处理，**不写脚本硬刷**。
  （我们走的是相反路线 —— CloakBrowser 指纹注入，实测确实能过，但风险与合规性不同。）
- **单 worker + 抖动**：所有后端调用串行，翻页 3~8 秒高斯抖动，独立调用 1.8~3.2 秒，
  避免明显的机器人节奏。
- **小时配额 + 指数退避**：滚动 1 小时请求预算（默认 60），触发限流后 1/2/4/8/15 分钟退避。
- **凭证脱敏**：cookie / sessionid / passport_* / localStorage / storage_state 不出现在返回值、
  日志或报错里。
- **账号指纹**：记录首个登录账号的不可逆指纹，换号后写操作直接拒绝。
- **缺失即 `null`**：抖音数据稀疏，缺字段返回 `null`，不填 0、不猜。
- **发送闸**：两次发送最少隔 30 秒；风控/失败自动进冷却，冷却期内不开浏览器。
- **回读证据**：私信是否真发出去，用回读确认，不靠「调用没报错」。

## 与我们现有实现的关系

| 上游能力 | 我们现状 |
|---|---|
| 群聊仿真决策 | ✅ 已自实现 `~/.hermes/skills/group-sim/`（4 状态机 + 额度 + 白名单 + 安全边界） |
| 读抖音评论 | ✅ 已自实现 `~/.hermes/skills/douyin-tool/`（CloakBrowser stealth + 页面内 fetch） |
| QQ 接入 | ✅ Hermes 原生 qqbot 适配器，比 SnowLuma 路线轻得多 |
| 语音 | ✅ edge_tts 已在 hermes venv（7.2.7）+ MiniMax TTS 已验证 |
| 搜索 | ✅ Hermes web_search/web_extract 自带 SSRF 防护 |
| 抽屉式配额熔断 | ✅ 已自实现 `~/.hermes/scripts/quota_circuit_breaker.py` |
| 抖音发布/评论回复 | ❌ 未做（需要登录态 + creator 平台投稿流程 + 人工过发布风控） |

**结论**：没有需要整体安装的东西。值得吸收的是**工程习惯**（抖动、配额、退避、凭证脱敏、
账号指纹、缺失即 null、回读证据、fail-closed 白名单），不是代码本身。
