---
name: reflexion-loop
description: Reflexion自我反思循环：Generator-Evaluator-Reflector模式，无需梯度更新即可提升Agent质量，91% HumanEval
---

# Reflexion 自我反思循环

基于 Shinn et al. (NeurIPS 2023) - Verbal Reinforcement Learning

## 核心效果

| 数据 | 来源 |
|------|------|
| 91% HumanEval pass@1 | Shinn 2023 |
| 38%→71% 首次部署成功率 | Harbor Support 案例 |
| +34% 质量提升 | coding/writing/tool-use 平均 |
| 1.6x token 额外开销 | vs base model |

## 三组件循环

```
Actor（生成） → Evaluator（评分） → Reflector（反思） → 重试
                ↓ fail              ↓
            记录到记忆         追加到 episodic memory
```

### Actor
生成初始响应。如果有反思历史，将其注入 prompt。

### Evaluator
返回结构化评分：
```json
{"score": 0.85, "verdict": "pass/fail", "specific_issues": [...]}
```
评分方式：
- **代码任务**：运行测试用例
- **文本任务**：LLM judge
- **工具任务**：执行结果验证

### Reflector
生成 2-3 句结构化反思：
```
1. 什么具体错误发生了
2. 为什么发生
3. 下次怎么改
```

规则：禁止"be more careful"类泛泛之言，必须具体到工具名+错误字符串。

## 在 Hermes 中的用法

```bash
# 对今日失败进行反思
python3 ~/.hermes/self-improvement/agent_core.py reflexion
```

反思结果保存在 `~/.hermes/self-improvement/logs/reflections.json`。

## 与其他方案对比

| 方案 | 适用场景 | 不用时 |
|------|---------|--------|
| Reflexion | 多步决策、可重置环境 | 一次性问答 |
| Self-refine | 单 artifact 打磨（SQL/代码）| 无可执行验证 |
| RLHF/DPO | 离线大规模偏好数据 | 工具快速迭代 |

## 生产检查清单

1. ✅ 定义可靠的 binary/scalar evaluator
2. ✅ Actor loop 含工具 schema 和观测格式化
3. ✅ 反思模板限制 50-150 tokens
4. ✅ 每任务 max trials + 人类升级路径
5. ✅ episodic memory 有 task 键值，过期自动清理
6. ✅ 反射内容脱敏（无 secrets/PII）
7. ✅ 嵌入/检索记忆（可选，用于多样化任务）
8. ✅ 跟踪：成功率、trial-to-success 次数、token 成本

## 与 Hermes 集成

Reflexion 循环已内置于 `agent_core.py reflexion` 命令。

下次任务失败时：
1. 记录 failure：`agent_core.py failure <action> <error>`
2. 运行反思：`agent_core.py reflexion`
3. 下次同类任务，agent 自动读取 reflections.json 获取历史教训

## 相关研究

- SWE-RL (Meta)：self-play 生成 bug 再修复，+10.4 points
- HyperAgents (Meta 2026)：meta agent 可修改自己，跨域迁移
- RAR (Retrieval-Augmented Reflexion)：用向量检索扩展记忆
