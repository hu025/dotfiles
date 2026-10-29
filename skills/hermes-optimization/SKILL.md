---
name: hermes-optimization
description: Hermes Agent 性能优化：上下文压缩、技能裁剪、模型路由最佳实践
---

# Hermes Agent 性能优化

## 上下文压缩配置（已验证有效）

```yaml
# ~/.hermes/config.yaml
agent:
  max_turns: 50          # 原200，减少token爆炸

compression:
  enabled: true
  hygiene_hard_message_limit: 400   # 原600
  protect_last_n: 40                # 原50
  protect_first_n: 3                # 新增：保护前3条
  target_ratio: 0.08               # 原0.1，更激进

context:
  max_context_turns: 60            # 原100
```

**生效方式**：`hermes config set <key> <value>`（不接受直接 patch config.yaml）

**compactor 写作原则**：用声明式语句，不要流水账。要写"做了什么决定"而非"执行了什么命令"。

## 技能裁剪（减少注入开销）

隐藏不用的技能域：
```bash
cd ~/.hermes/skills
for d in antigravity apple blockchain communication data-science diagramming dogfood email gaming gifs health hyperliquid media mlops mlops/evaluation mlops/inference mlops/models mlops/research model-routing note-taking red-teaming smart-home social-media; do
  [ -d "$d" ] && mv "$d" ".$d"
done
```
恢复：`for d in .*; do [ -d "$d" ] && mv "$d" "${d#.}" 2>/dev/null; done`

## 模型路由策略

- **默认 → minimax/m3**（2026-09-07 升级，80.5% SWE-bench，1M 上下文，$0.30/M tokens）
- ETF分析/复杂推理 → nvidia/mistralai/mistral-large-3-675b
- 代码调试 → nvidia/llama-3.3-nemotron-super-49b

### MiniMax M3 注意事项（重要）

M3 使用 **Interleaved Thinking**：thinking 块必须完整保留并回传，压缩或截断会**静默损坏响应**（无报错）。

配置原则：
- `protect_last_n` 保持 40+，确保 thinking 链不被切断
- M3 reasoning_split 可分离 thinking/content，但 Hermes 不要 strip 任何 `<think>` 标签
- 切换命令：`hermes config set model minimax/m3`


### MiniMax 额度耗尽的连锁失败（2026-10-14）

**关键失败模式**：MiniMax 额度耗尽时 HTTP 402 会导致**所有 cron job 连锁失败**。
发现 cron 集体失败时优先检查 MiniMax 余额，而不是逐个查 job。

**格式注意**：`hermes config set model` 写无前缀格式（如 `minimax-m2.7`），
避免与 cron job 保存格式不一致导致所有 unpinned cron 跳过。

### agent_core.py 硬编码陷阱（2026-10-14）

`~/.hermes/self-improvement/agent_core.py` 中有两类硬编码，每次模型切换后必须同步检查：

**1. 硬编码模型名**（line ~537）：`"minimax-m2.7"` → 改为当前主模型
**2. 硬编码 API Key + 模型名**（line ~759）：直接拼接 key 字符串和模型名，绕过 `_get_api_key()` → 改为调用 `_get_api_key()` + 当前模型

**症状**：gateway 正常但 cron 全部失败（HTTP 402 或硬编码 key 无效）。
**修复后**必须同步更新 `~/.hermes/cron/jobs.json` 中所有任务的 `model_snapshot` 字段。

## Session Search 优于记忆查询

- 记忆是持久快照（不常变化的事实）
- Session Search 是动态查询（问"上次怎么处理的X"）

## 优化后记录

```bash
python3 ~/.hermes/self-improvement/agent_core.py improve "hermes" "<具体改动>" "<效果>"
```

## 记忆库精简（每次大会话后执行）

MEMORY.md 超过 10KB 会导致每次会话注入过多 token。发现膨胀时直接重写：

```bash
# 检查大小
wc -c ~/.hermes/memories/MEMORY.md ~/.hermes/memories/USER.md

# 目标：MEMORY.md < 3KB，USER.md < 2KB
# 重写原则：
#   - 删除所有过时模型切换记录（噪音）
#   - 压缩为声明式语句，不要流水账
#   - 保留：凭证、系统状态路径、用户偏好、技能位置
# 写入：write_file（直接覆盖，不追加）
```

fact_store 清理：直接编辑 `~/.hermes/memories/MEMORY.md` 和 `~/.hermes/memories/USER.md`，不要依赖 HTTP API（端口 8642 的 fact_store API 不一定可用）。

## Skill 加载优化（RFC #64876 发现）

当前问题：Skill router 永久加载全部 150 skill descriptions（17k chars）
原因：router 指令"Partially relevant skills MUST be loaded"导致过度加载

优化方案：
1. skill description 字段 ≤ 60 chars，极简 self-contained
2. 分类目录结构：user-profile/ project/ environment/ procedural/
3. 利用 `skills_list` 作为天然索引（已返回 name + description）
4. agent 主动判断 `skill_view` 所需 skill

工具 schema 优化：
- tool_search deferral 阈值 10% context window → 对于 1M context = 105k tokens，永不触发
- 大量简单对话仍有 ~65k chars tool schema 开销
- 按需加载工具：只在 skill 实际需要时才加载其 schema


## ruamel.yaml namespace package 冲突（2026-10-14 根因）

**症状**：Cron 全部失败，`ModuleNotFoundError: No module named 'ruamel.yaml'`，但 `pip show ruamel.yaml` 显示已安装。

**根因**：Python 3.14 的 `.pth` 文件劫持了 `ruamel` namespace。`~/.local/lib/python3.14/site-packages/` 下的 pth stub 干扰了 tools Python 的 site-packages。

**修复**：
```bash
# 找到干扰的 pth 文件
ls ~/.local/lib/python3.14/site-packages/ruamel*.pth
# 删除（保留实际内容）
rm -f ~/.local/lib/python3.14/site-packages/ruamel*.pth
# 验证
python3 -c "import ruamel.yaml; print('OK')"
```

**预防**：工具链 Python（`~/.hermes/tools/python-3.14*/`）安装 ruamel.yaml 后立即验证 import。


## hermes-update 版本更新陷阱（2026-10-14）

**问题**：PyPI 稳定版经常落后 GitHub 数月。`hermes update` 只查 PyPI，导致误以为已是最新版本。

**正确路径（GitHub 领先时）**：
```bash
cd ~/.hermes/hermes-agent
git fetch cnb --tags  # 国内镜像，比 GitHub 快
git checkout v0.22.5  # 目标版本（用 git describe --tags 查当前）
HP=$(ls ~/.hermes/hermes-agent/venv/bin/python3 2>/dev/null || ls ~/.hermes/hermes-agent/.venv/bin/python3 2>/dev/null)
"$HP" -m pip install -e . --upgrade   # 注意: 会重装依赖, 执行前备份 config.yaml 并验证 import

# ⚠️ 2026-10-29 新增教训：手动 git checkout 会跳过官方收尾，导致
# install-stamp.json 缺失 + source-completion-pending 标记残留，
# 每次 CLI 调用报 "a source update is unfinished"。正确做法是 checkout 后
# 从独立 shell 跑一次 `hermes update` 让它写 stamp 并重建产品构建。
# 另：auto_upgrade.py 曾把 fetch 当 checkout 导致误报升级成功，已修（含 sha 校验）。
```

**验证**：`hermes update --check` 输出 `Up to date with the latest release (stable vX.XX.X)`

**症状**：`hermes --version` 显示旧版本，但 `hermes update` 说已最新。

## 补自旧副本的独有内容（hermes-optimization，合并于 2026-10-29）

- 换模型前 → 先 pause cron job，改完重建（防止 drift skip）
- **关键失败模式**：MiniMax 额度耗尽时 HTTP 402 会导致所有 cron job 连锁失败，发现 cron 集体失败时优先检查 MiniMax 余额
- 格式注意 → `hermes config set model` 写无前缀格式（如 `minimax-m2.7`），避免与 cron job 保存格式不一致导致所有 unpinned cron 跳过
**1. 硬编码模型名**（line ~537）：`"minimax-m2.7"` → 改为 `minimax-m3`
**2. 硬编码 API Key + 模型名**（line ~759）：直接拼接 key 字符串和 `minimax-m2.7`，绕过 `_get_api_key()` → 改为调用 `_get_api_key()` + `minimax-m3`
症状：gateway 正常但 cron 全部失败（HTTP 402 或硬编码 key 无效）。
修复后必须同步更新 `~/.hermes/cron/jobs.json` 中所有任务的 `model_snapshot` 字段。
