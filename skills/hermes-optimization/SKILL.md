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
