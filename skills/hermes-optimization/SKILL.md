---
name: hermes-optimization
description: Hermes Agent 性能优化：上下文压缩、技能裁剪、模型路由最佳实践
---

# Hermes Agent 性能优化

## 上下文压缩优化（已验证有效）

```yaml
# ~/.hermes/config.yaml
agent:
  max_turns: 50          # 原200，控制在50以内避免token爆炸

compression:
  enabled: true
  hygiene_hard_message_limit: 400   # 原600，减少overhead
  protect_last_n: 40                # 保留最近40条
  protect_first_n: 3                # 保留前3条（system prompt）
  target_ratio: 0.08                # 原0.1，压缩更激进
```

**compactor 写入原则**：用声明式语句写目标和决策，不要流水账。

## 技能裁剪

隐藏不用的技能域，减少注入开销：
```bash
cd ~/.hermes/skills
for d in apple creative data-science diagramming dogfood email gaming gifs media note-taking red-teaming smart-home social-media; do
  [ -d "$d" ] && mv "$d" ".$d"
done
```
不删除，只是 rename 掉，恢复：`mv .$d $d`

## 模型路由策略

**默认廉价，必要时升级**：
- 默认任务 → minimax-m2.7（便宜，快速）
- 代码/调试 → nvidia/llama-3.3-nemotron-super-49b
- ETF分析/复杂推理 → nvidia/mistralai/mistral-large-3-675b

## 工具输出截断

```yaml
tool_output:
  max_bytes: 50000
  max_lines: 2000
```

## Session Search 优于记忆查询

记忆是持久快照，Session Search 是动态查询。问"我们上次怎么处理X的" → 用 session_search。

## 自我进化记录

每次优化后记录：
```bash
python3 ~/.hermes/self-improvement/agent_core.py improve "hermes-optimization" "<具体改动>" "<效果>"
```
