---
name: agent-scheduling-reliability
description: Use when designing or debugging cron/queue job execution, retries, backoff, idempotency, dead-letter queues, or priority/fair scheduling for agent workloads. Trigger: "job queue", "retry storm", "idempotency key", "dead letter", "duplicate cron run", "backoff", "worker died mid-job", "priority scheduling".
---

# Agent Scheduling & Retry Reliability

调度层设计原则：**Cron 只入队，不干活**。失败重试、幂等、死信必须在队列层解决，而不是靠"重跑一遍"。

## 1. 分层：Trigger → Queue → Worker → Monitor

```
*/15 * * * * node enqueue-job.js     # cron 只写队列，立即返回
        ↓
   BullMQ / SQS / Cloudflare Queues   # 持久化信封 + 优先级 + 延迟重试
        ↓
   Worker（无状态，租约 + checkpoint） # 副作用只在这里发生
        ↓
   Heartbeat / DLQ 深度告警            # 验证触发真的发生了
```

反模式：`*/15 * * * * node run-agent.js`（cron 直接跑全流程，超时=丢任务，无 DLQ）。

## 2. 错误五分类（决策的根）

分类必须来自结构化错误信封（HTTP code + provider code + tool code），**不要对 message 字符串做匹配**。

| Class | 例子 | 动作 |
|---|---|---|
| transient | 429 / 5xx / 网络超时 / 连接重置 | 指数退避 + 全抖动重试 |
| permanent | 4xx（除 408/429）、校验失败、鉴权失败 | 不重试，直接上报失败 |
| semantic | 语法合法但内容错误（工具幻觉） | 带约束**重新规划**，不要盲重试 |
| policy | 安全/内容/配额拒答 | 走 fallback，**同输入重试无意义** |
| state | 上下文丢失、会话过期、记忆损坏 | 从 checkpoint 恢复后重试 |

**关键区分：retry ≠ recovery。**
- transient → 重试
- worker 中途死 → 从最后一个持久 checkpoint 恢复（不是从头）
- 副作用后超时（**ambiguous write**）→ 暂停、对外核实、再决定重放或标记完成

## 3. 退避参数（生产默认值）

```
sleep = random_between(0, min(cap, base * 2^attempt))   # AWS "Exponential Backoff and Jitter"
base  = 250ms (tool) / 1000ms (LLM)
cap   = 30000ms
max_attempts = 5 (tool) / 3 (LLM)
retry_budget = 每次 run 累计重试秒数上限 60s   ← 防长任务内部重试风暴
```

- 服务端给了 `Retry-After` 就**听服务端的**，否则用 full jitter。
- 无抖动的指数退避 = thundering herd：所有同时 429 的任务同一瞬间再撞一次。
- BullMQ 自定义 backoff strategy 返回 `-1` 即终止重试。

## 4. 幂等键：业务派生，不是 UUID

重复执行 ≠ 模型问题，是幂等问题。键必须代表"只想发生一次的**业务事件**"：

- `customer-123-daily-summary-2026-10-17`
- `ticket-9981-first-response`

固定：`hash(run_id + step_id + tool_name + tool_args)`。TTL 必须覆盖任务最长生命周期（默认 24h）；过期后重试被视为新意图，需重新鉴权。

对不支持幂等键的下游，做**客户端幂等缓存**：同 hash 命中则直接返回已记录结果。

BullMQ 里直接把业务键当 `jobId`——同键重复入队被忽略，天然去重。

## 5. Lease + Checkpoint（防"两个 worker 都在跑"）

```
acquireLease(jobId, workerId, ttl=900s)
  ↓
loadCheckpoint → 执行**一个有界步骤** → saveCheckpoint → renewLease → enqueueIfNeeded
  ↓ finally: releaseLease
```

信封必备字段：`jobId / attempt / maxAttempts / leaseOwner / idempotencyKey / checkpointVersion / resumeFrom / visibilityTimeout`。

步骤要小到"能放心重放"。每次尝试发一条 telemetry span。

## 6. 死信队列不是坟场

- 每个输入的 retry budget 跨生命周期累计（默认 5 次），不是每次调用重置。
- 耗尽 → 携完整元数据（原始 payload / 尝试数 / 错误轨迹 / 时间戳）入 DLQ。
- **每个 DLQ 必须有具名 owner + runbook 条目 + 修复后 replay 路径（用新幂等键）。**
- DLQ 深度超阈值即告警。补偿动作自身耗尽重试 → 也进 DLQ，绝不静默成功。

## 7. 多 agent 协同重试（防跨 agent 风暴）

多 worker 共享同一后端时，各自本地退避仍会同步重试。
**Leader-lease 重试窗口**：选一个 leader（etcd/Consul/分布式锁），只允许 leader 在窗口内发起重试，其余本地退避等待；leader 失联后重选，窗口重置。
保证同时重试的 agent 数 ≤ lease size（通常 1）。全局锁会成瓶颈，按 key 分片。

## 8. 优先级与公平调度

| 机制 | 语义 | 陷阱 |
|---|---|---|
| 严格优先级 | 高优先饿死低优先 | 必须加 aging：等待时长加权进优先级 |
| 加权公平(WFQ/虚拟时间) | 每租户保证份额 | 需要维护虚拟运行时间戳，成本高 |
| 老化(Aging) | 等待越久优先级越高 | 最省事，默认选它 |
| 限流器(令牌桶) | 平滑 RPM 到上游 | 与退避独立，两者都要 |

worker 侧：`concurrency=N` + `limiter:{max,duration}` 双限。concurrency 防打爆本地，limiter 防打爆上游。

## 9. 自检清单

- [ ] cron 只入队，不执行 agent 逻辑
- [ ] 每个副作用步骤都有业务派生的幂等键
- [ ] 退避带 full jitter，且尊重 Retry-After
- [ ] 有 per-run retry_budget 上限（默认 60s）
- [ ] permanent/policy 错误不重试
- [ ] semantic 错误重新规划而非盲重试
- [ ] 有 lease + heartbeat 防并发重复处理
- [ ] checkpoint 在每个有界步骤后持久化
- [ ] DLQ 有 owner、runbook、replay 路径
- [ ] 心跳/健康检查能证明"触发真的发生了"
- [ ] 优先级机制带 aging 防饥饿

## 落地到 Hermes

- cron job 靠 `hermes cron` 管理（漂移检测会 skip 未 pin 模型的 job，改模型前先 pause）。
- 定时脚本放 `~/.hermes/scripts/`（`--script` 只接受相对路径）。
- 长任务拆步骤：把 checkpoint 写进 memory/文件，避免失败后整段重来。

## 来源

- https://geodocs.dev/ai-agents/agent-error-recovery-patterns-spec
- https://negiadventures.github.io/blog/agent-retry-recovery.html
- https://dev.to/lars_winstand/i-wouldnt-trust-an-ai-agent-to-cron-alone-anymore-8-reliability-rules-id-ship-by-friday-82k
- https://dev.to/fabwaseem/building-an-ai-automation-pipeline-in-nodejs-with-bullmq-queues-retries-and-rate-limits-40d8
- https://dev.to/tamizuddin/beyond-the-happy-path-applying-distributed-systems-principles-to-fix-ai-agent-retry-loops-and-2fk6