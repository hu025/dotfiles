# MPAC: Multi-Principal Agent Coordination Protocol

> 填补 MCP（工具调用/单主体）/A2A（任务委派/单主体）之间的空白——多主体跨信任边界协调协议

## 核心定位

**问题**：当独立主体的 agent 需要协调共享状态时（如两个工程师的 coding agent 编辑同一代码库、家庭成员规划共同旅行、不同组织的 agent 谈判联合决策），MCP 和 A2A 都不适用，协调退化为 ad-hoc 聊天、手动合并或静默覆盖。

**解决**：MPAC = Multi-Principal Agent Coordination Protocol，应用层协议，填补多主体跨信任边界协调的协议层空白。

## 五层架构

| 层级 | 职责 | 关键机制 |
|------|------|----------|
| **Session** | 管理多 agent 交互的整体上下文 | 连接建立/维持/终止 |
| **Intent** | agent 行动前必须声明意图（核心创新） | 意图前置声明 → 主动冲突预防 |
| **Operation** | 定义 agent 提议执行的具体操作 | 操作序列化和执行 |
| **Conflict** | 将冲突表示为一等结构对象（非错误） | 冲突分类 + 状态机流转 |
| **Governance** | 可插拔的人类介入仲裁层 | 规则定义 → 自动决策/人工审批 |

## 核心技术细节

- **21 种消息类型**：覆盖声明、操作、冲突、仲裁全生命周期
- **3 个状态机**：Session 状态机 / Conflict 状态机 / Operation 状态机（含规范转换表）
- **Lamport 时钟因果水印**：确保分布式动作逻辑正确排序
- **乐观并发控制**：类似代码合并管理，agent 并行工作，冲突仅在 commit 阶段处理
- **3 种安全配置文件**：open / authenticated / verified
- **2 种执行模型**：pre-commit（需审批后执行）/ post-commit（执行后提交）

## 性能数据

> 三 agent 跨模块代码审查基准测试（对照：串行人工调解基线）

- 协调开销减少 **95%**（68.65s → 3.02s）
- 壁钟加速 **4.8x**（131.76s → 27.38s）
- agent 决策时间不变（加速来自消除协调等待，非压缩模型调用）

## 与现有协议的关系

```
协议层          定位                    代表协议
─────────────────────────────────────────────────
工具调用层       单主体工具调用            MCP (Anthropic)
路由层           单主体任务委派            A2A (Google)
───────────────────────────以上均为单主体─────────
内容压缩层       LLM 成本优化              AACP
内容协调层       多主体跨信任边界协调       MPAC ← 新增
```

**互补非替代**：MPAC 与 MCP/A2A/AACP 并存，分别解决不同层面的协调问题。

## 实现状态

- **Python 实现** + **TypeScript 实现**：互操作，MIT 许可证
- 223 个测试用例，JSON Schema 测试套件
- 7 个 live 多 agent 演示（含 Claude 后端）
- arXiv: https://arxiv.org/abs/2604.09744（2026-04-10）

## 对 Hermes 的价值

1. **多 agent 场景**：Hermes 的 delegate_task 是单主体委派，MPAC 理念可指导跨信任边界协调设计
2. **冲突检测**：MPAC Conflict 层的一等冲突对象设计可用于任务队列冲突检测
3. **Governance 层**：人类介入仲裁机制可映射到 Hermes 的 tool approval 流程
4. **乐观并发**：MPAC 的 git-style 合并冲突解决思路可用于并发任务执行

## 触发词

- "多主体协调"、"跨组织 agent"、"多 agent 冲突"
- "MPAC"、"multi-principal"
- 任何需要多个独立 agent 协调共享资源的场景

## 参考资料

- https://arxiv.org/abs/2604.09744
- https://arsa.technology/machine-state/enabling-enterprise-grade-ai-collaboration-the-mpa-5xlq0tzs/
