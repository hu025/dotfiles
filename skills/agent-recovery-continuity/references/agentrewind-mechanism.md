# AgentRewind — 可恢复执行的机制设计（与 SF1/SF2/SF5 对照）

Source of record: Zhuang, Chen, Duan, Zheng, Li, Zhang. *"AgentRewind:
Recoverable Execution for Long-Horizon LLM Agents."* arXiv:2608.14380v1,
cs.AI, 2026-08-14. (UCAS / IIIS Tsinghua / Zhongguancun Academy / CASIA)

Code: https://github.com/Futuresis/replay-agent-recorder
Bench: https://github.com/Kelvin-Coffee/MettleBench

本文件是主 SKILL.md 安全视角（SF1–SF5）的**构造侧对应物**：安全论文说
"rollback 会打破执行连续性"，这篇说"怎么设计 rollback 才既有效又（在受控
状态下）一致"。两篇合起来读才完整。

## 1. 问题结构：forward-only 轨迹

标准 agent loop 只能追加，不能截断：

```
u_t ~ π(c_t)
(s_{t+1}, o_{t+1}) = T(s_t, u_t)
c_{t+1} = U(c_t, u_t, o_{t+1})
τ = ((c_0,s_0), u_0, o_1, (c_1,s_1), …)
```

早期错误 u_k 的影响被 bake 进每一个后续 c 和 s。已有缓解（plan refinement、
safety check）只降低每步出错概率，**不提供错误发生后的恢复**——而长程任务
的失败概率随步数复合增长。

三种恢复哲学，严格包含关系：
- **Continue/retry**：什么都不撤销，只追加纠正动作（= rewind-to-present）
- **Restart**：环境与上下文都回初始态，只带文本经验（= rewind-to-beginning）
- **Rewind**：回**中间**点——保留错误之前已验证的进展，只丢弃错误及其下游
  后果。Rewind 严格更一般；工程难点在让任意中间目标既**可选**又**可安全恢复**。

## 2. AgentRewind 机制（三个部件）

**(a) 双通道记录器（透明，不改变交互）**
- Agent Context Recorder：每对 LLM 输入/输出
- Environment State Recorder：每次 tool 引起的受控环境变更（workspace 文件级 diff）
- 在**每个 LLM 决策边界 t** 合并为状态检查点 `d_t = (c_t, s_t)`
  **配对的时刻就是全部技巧**：两半在同一逻辑瞬时捕获，日后恢复 d_t 保证
  agent 的信念与它看到的世界互相一致。分开、不同步地检查点会导出 SF2。

**(b) 元数据 η_t**：d_t 与 d_{t+1} 之间的执行段摘要（diff+narrative），
供 agent 选回滚点用，不参与恢复。（评审指出这是 UI/决策支持物，不是状态）

**(c) Rewind 模块 — 暴露给 agent 的两个额外工具**
```
backtrack_candidates(reason) ->
    最多 80 个候选检查点 + 各自元数据 η_t
backtrack_commit(record_uid, memory_summary, reason) ->
    确定目标 d_k，同时提交 rewind memory m（自由文本，写给"未来的自己"）
```
提交后的两行核心机制：
```
s_k' ← s_k                       # 受控环境回滚
c_k' ← Inject(c_k, M)            # 注入累积的 rewind memory 集合 M
```
被丢弃分支的 LLM 输出与 tool 结果**从执行日志恢复，不重新生成/重执行**
（→ SF4 的"unbound nondeterministic replay"风险仍在，见 §5）。

## 3. MettleBench（评测基准，82 任务 / 640 准则）

- 源自 5 个工程基准：Terminal-Bench 2.0 (28), ProgramBench (22), SWE-bench
  (18), ProjectEval (7), GitTaskBench (7)。保留工件与可执行环境，重写任务
  说明为"一串相互依赖的验收准则"。
- **有序 checklist，反馈只给第一条未满足项**，全表对 agent 隐藏。
- 评分 = checklist progress（满足前缀长度 / 准则总数），不只是二值成功。
- 明确筛查过存在纯 forward-only 解，82 任务中至少 70 个被某个模型在
  Continue 下解出 → 基准独立于任何恢复机制。
- Workspaces 走 HuggingFace tarball 分发（含 git repo、符号链接、权限位，
  纯 git checkout 会丢失）。

## 4. 实测数字（GPT-5.4 默认，mini-SWE-agent harness）

主对比（MettleBench, 82 任务）：
| Strategy | Success ↑ | Checklist Progress ↑ |
|---|---|---|
| Continue | 62.2% | 81.4% |
| Restart w/ Experiences | — | 波动大，进度有回退 |
| Safety Review (AgentDoG) | GPT-5.4 下显著更差 | 不稳定 |
| **AgentRewind** | **87.8% (+25.6pp)** | **94.3% (+12.9pp)** |

跨 harness 一致性（GPT-5.4，同设置）：
| Harness | Continue | AgentRewind |
|---|---|---|
| mini-SWE-agent | 62.2 / 81.4 | 87.8 / 94.3 (+25.6) |
| FnCallAgent (Qwen-Agent) | 58.5 / 77.9 | 81.7 / 91.4 (+23.2) |
| CodeAgent (smolagents) | 67.1 / 83.0 | 82.9 / 89.7 (+15.8) |

Terminal-Bench 2.0（89 任务，准则无序）：
Continue 78.7/88.7 → AgentRewind **83.1/90.2**；Restart w/ Exp 反而降到 70.8/79.2。

从**同一失败状态**配对恢复（50 条 Continue 失败轨迹，复制 context+env 后
各自恢复，失败计数重置）：
| Method | Recovery Rate ↑ | Δ Checklist Progress ↑ |
|---|---|---|
| Continue | 8.0% | +5.1pp |
| **AgentRewind** | **30.0%** | **+12.2pp** |

**消融（这是最有信息量的一张表）**：
| Variant | Success | Progress |
|---|---|---|
| Full AgentRewind | 87.8 | 94.3 |
| **w/o Environment Rewind** | **43.9** | **63.5** |
| w/o Context Rewind | 65.9 | 77.9 |
| w/o Rewind Memory | 51.2 | 69.4 |

→ **环境回滚是最大单一贡献者**（拿掉后掉 44pp，比拿掉 context 回滚掉 22pp
更致命）。原因直白：被丢弃后缀引入的环境变更不撤销就一直留在盘上。
Rewind memory 单独拿掉也掉 36pp——"记得上次为什么错"和"能回去"同等重要。

## 5. 必须一起记住的坑（评审 + 论文自陈）

1. **外部副作用不回滚。** 论文结论一句带过："currently restores only
   controlled state"。推 git 到远端、打 package registry、发 Slack、调付费
   API——被丢弃分支里做过这些 = agent 眼里世界干净了，真实世界没干净。
   **这正是 SF5**，且本篇没有任何检测机制；评审建议加"local reversible vs
   external irreversible"动作分类器，在执行前 surface。Hermes 侧的对应做法
   是把外部动作记进**回滚边界之外的 effect ledger**（主 SKILL.md 已有）。
2. **Rewind memory 只累积、从不剪枝。** 每次 rewind 注入的 M 只增不减，
   且每次 backtrack_candidates 都要一整轮 LLM 调用 + 把最多 80 条元数据塞进
   上下文。实验里"Rewinds per run: unlimited"，病态任务可能让纯机制开销吃掉
   大量 context budget。论文**没测** memory 随 run 增长的 token 曲线——这是
   已知的空白，不是已被排除的风险。
3. **外部验证才能识别停滞。** AgentRewind 依赖 MettleBench 的 checklist
   反馈告诉你"卡住了"。没有外部验证器的开放域任务里，"何时该 rewind"这个
   判断仍要 agent 自己或 monitor 做。
4. **同配置重复 3 次的一致率只有 74.7%**（656 个 (task, strategy, model)
   三元组，490 个三跑同结论）。per-cell 一致率最低 48.8%（Safety Review +
   GPT-5.4）。→ 任何单次 agent 评测数字都要当噪声大的样本看；比较两个机制
   时跑 ≥3 次并报一致率。
5. **不能防止错误，只能恢复。** 案例研究里 AgentRewind 犯了和 Continue
   完全相同的初始错误（catalog generator 用错 mode，到 8/10）——机制价值在
   "回得去 + 记得错在哪"，不在"不会错"。

## 6. 关联工具：replay-agent-recorder（可直接复用的工程物）

论文配套开源，MIT，local-first 时间旅行调试：
- **Record**：JSONL trace（OpenAI 兼容 chat completions、本地 tool call、
  语义事件、async 分支、沙箱文件副作用）
- **Replay**：复用已录 LLM/tool 输出，确定性重放，**不再调模型**（省 token
  且复现 flaky 失败）
- **Fork**：从任一 LLM 断点分叉，覆盖该点输出/assistant 消息/请求输入
- **Backtrack**：选记录的决策点 + 存有界 recovery summary
- **Git workspaces**：声明 workspace 树，跨 record/replay/fork/restore 跟踪文件副作用
- **Sandbox（实验性）**：经 Docker/Podman 检查点 container rootfs、文件、进程，
  **含 external-effect ledger**——注意这个 ledger 正是 SF5 的工程解
- **Visualize**：summary JSON / Graph IR / Mermaid / 离线 HTML explorer

## 7. 对 Hermes 的落地含义

- Hermes 的 `tools/checkpoint_manager.py` 是**单域**（workspace）检查点。SF 表里
  Hermes SF2=240/347 是三家框架里最高的，根因即"两个独立恢复的状态域"。
  AgentRewind 的构造是解药：**决策边界上同时捕获 context 与 workspace，
  恢复时两者一起动**。
- 给 agent 暴露 `backtrack_candidates` / `backtrack_commit` 两个工具比让它
  在 prompt 里"自己决定要不要 /undo"更有效——候选带元数据，选择质量取决于
  η_t 的摘要质量。
- **rewind memory 要写进 skill/记忆层，不要只留在对话里**：本仓库的做法是
  失败教训沉淀成 SKILL.md 的 lesson 行，天然跨 session 存活（比累积注入
  更接近"bounded"）。
- 外部动作（push、发消息、付费 API）继续按 effect ledger 处理；AgentRewind
  不替你解决这个。
