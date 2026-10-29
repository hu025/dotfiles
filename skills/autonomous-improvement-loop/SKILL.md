---
name: autonomous-improvement-loop
description: 自主改进循环工作流。Ralph Wiggum模式：迭代小任务+自我验证+持续进化
---

# 自主改进循环 — Autonomous Improvement Loop

## 核心模式

每次会话结束时自动执行（不需要用户触发）：

```
1. 记录本次会话 → agent_core.py
2. 检查可自动化项 → 发现重复操作立即脚本化
3. 修复任何 skill 错误 → 不拖延
4. commit 到 dotfiles → ~/dotfiles/bin/deploy-dotfiles push
```

## Ralph Wiggum 编码循环（适用于编程任务）

当处理复杂编程任务时：
1. 将任务拆解为原子级小任务（每任务 ≤ 1 个 AI session）
2. 每任务独立执行：写代码 → 验证 → commit
3. 验证失败 → 记录错误 → 换方向
4. 最多尝试 3 次同一问题的不同解法

## 主动侦察清单（每会话至少做一项）

### 系统状态
```bash
python3 ~/.hermes/self-improvement/agent_core.py status
```

### 可自动化发现
- 同一个操作出现 2 次 → 写脚本替代
- 手动流程超过 5 步 → 优化为 1-2 步
- skill 有错误 → 立即修复

### 记忆库检查
- 用户隐含偏好（从重复行为推断）
- 陈旧信息（30 天未更新且不再相关）

## 每周架构审查（六维）

1. **模型层** — 当前模型是否最优？延迟/质量/成本平衡
2. **记忆层** — 矛盾信息？过时偏好？新增行为模式？
3. **技能层** — 错误/过时/可合并？
4. **工具层** — 依赖安全？重复操作脚本化？
5. **浏览器自动化** — 稳定？新页面结构？
6. **自主改进** — 本周成功率趋势，最该改进的 1-3 点

## 陷阱与排查

### autonomous_research HTTP 401
`autonomous_research()` 调用 `localhost:8642/v1/chat/completions` 时：
- **必须**提供有效的 `Authorization: Bearer <API_SERVER_KEY>` 请求头
- subagent 子进程**不继承**父进程环境变量（`get_secret("API_SERVER_KEY")` 在 subagent 中返回空）
- 正确做法：从 `~/.hermes/auth.json` 的 `credential_pool` 获取，或从 systemd service 环境变量注入
- 验证：`curl -s -X POST http://localhost:8642/v1/chat/completions -H "Authorization: Bearer <key>" -H "Content-Type: application/json" -d '{"model":"minimax-m2.7","messages":[{"role":"user","content":"hi"}],"max_tokens":5}'`
- gateway 8642 端口强制校验 API key，不允许无认证访问

### subagent 无法重启 gateway
gateway 进程本身不能执行 `systemctl --user restart hermes-gateway.service`（SIGTERM 会同时杀死子进程）。解决：用 `delegate_task` 在独立子 agent 中执行重启。

### 相关参考
- `references/api-server-key.md` — API_SERVER_KEY 获取、配置、验证的完整指南

## 禁止事项

- 不做无意义循环
- 磁盘 < 500MB 时停止非必要操作
- 不安装未验证的依赖
- 不删除用户数据

## 速度控制

- 单次问题：最多 3 次不同解法，失败则记录 + 跳过
- 单次尝试：超过 10 分钟无进展 → 记录 + 换方向
- 资源警告：磁盘 < 1GB 时主动停止非必要操作
