---
name: aacp
description: AACP (Agent Action Compression Protocol) — 协调消息内容压缩协议。2026-09-19 研究。
triggers:
  - AACP
  - agent coordination cost
  - multi-agent communication protocol
  - agent message compression
---

# AACP — Agent Action Compression Protocol

## 核心定位

**填补 MCP/A2A 之间的内容层空白。**

- MCP：工具调用层（agent→tool）
- A2A：任务路由层（agent→agent 跨轮次）
- **AACP：协调消息内容层（agent→agent 说什么）**

三层互补，协议栈关系：

```
Routing层: A2A (who receives the message)
Content层: AACP (what agents say to each other)
Tool层:   MCP (how agents invoke tools)
```

## 核心问题

现有框架（LangChain, CrewAI, AutoGen）中，每次 agent 间协调都需要 LLM 调用来生成自然语言指令。

**5-workflow × 59-hop 部门日场景实测：**
- 标准协调：59 次 LLM 调用
- AACP 压缩：全部消除（已知工作流）
- **结果：55%（AutoGen）~85%（Pydantic AI）总成本降低**

## 协议机制

### 四层编码器（零 LLM 成本优先）

```
请求 → Tier0 社区规则库（零成本匹配）
     → Tier1 本地哈希缓存（零成本命中）
     → Tier2 模式匹配（零成本规则命中）
     → Tier3 LLM 编码（仅对全新指令，一次性）
```

### 关键数据

- ** amortisation benchmark**：240 编码操作，91.6% 成本节省，仅 6 次 Tier3 LLM 调用
- **社区规则库**：241 条预验证规则，覆盖 7 个领域
- **支持框架**：LangChain / CrewAI / AutoGen / Pydantic AI（各独立 PyPI 包）
- **RFC**：draft-mackay-aacp-03，2026-06，IETF Internet-Draft（有效至 2026-12-19）

### AACP Packet 格式

管道分隔的确定性字符串，由规则编码器或 LLM 生成：

```
<action>|<target>|<params>|<result_format>
```

结构化 → 可验证 → 可审计 → 可回放。

## 与 Hermes 的关联

**直接价值：**

1. **多 agent 协调压缩**：Hermes 的 subagent 间通信若采用 AACP，可消除冗余 LLM 调用
2. **Agent 间消息确定性**：AACP 使协调消息从自然语言变为类型化指令，减少歧义
3. **规则库可扩展**：241 条社区规则覆盖常见协调模式，可直接复用
4. **与现有协议互补**：MCP（工具）+ A2A（路由）+ AACP（内容）三层完整

**潜在集成点：**
- `delegate_task` 的 agent 消息格式 → AACP 压缩
- `mission-control` 的 agent 间通信 → AACP 编码

## 安装与使用

```bash
# Python 框架集成
pip install aacp-langchain   # 55% 成本降低
pip install aacp-crewai     # 框架级集成
pip install aacp-autogen    # 55% 成本降低
pip install aacp-pydantic   # 85% 成本降低

# 社区规则库
pip install aacp-sdk        # 核心 SDK + 规则注册表
```

## 关键限制

- **MCP/A2A 已有路由**：AACP 不替代路由协议，依赖已有传输层
- **协调消息专用**：非协调类的普通消息不适用 AACP
- **IETF Draft 状态**：非最终标准，可能有breaking变化

## 参考

- 规范：https://datatracker.ietf.org/doc/html/draft-mackay-aacp-03
- 官网：https://aacp.dev
- PyPI：https://pypi.org/search/?q=aacp
