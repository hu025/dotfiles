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

- 默认 → minimax-m2.7（廉价快速）
- ETF分析/复杂推理 → nvidia/mistralai/mistral-large-3-675b
- 代码调试 → nvidia/llama-3.3-nemotron-super-49b

## Session Search 优于记忆查询

- 记忆是持久快照（不常变化的事实）
- Session Search 是动态查询（问"上次怎么处理的X"）

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

## 优化后记录

```bash
python3 ~/.hermes/self-improvement/agent_core.py improve "hermes" "<具体改动>" "<效果>"
```
