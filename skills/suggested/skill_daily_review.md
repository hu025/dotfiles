# 每日回顾与改进流程 — Daily Review Skill

## 何时使用
每天会话结束前，或收到用户指令"做每日回顾"时。

## 步骤

### 1. 读取今日记录
```bash
python3 ~/.hermes/self-improvement/agent_core.py status  # 当前系统状态
# 日报路径: ~/.hermes/self-improvement/reports/daily/daily_YYYY-MM-DD.md
```

### 2. 核心问题自检（5 分钟）
- [ ] 今天用户最核心的需求是什么？完成了吗？
- [ ] 哪些地方花了过多时间？为什么？
- [ ] 有没有可以自动化的重复操作？
- [ ] 记忆库中是否有需要更新的信息？
- [ ] 有没有遇到新工具/更好方法可以替代现有方案？

### 3. 记录结果
```bash
python3 ~/.hermes/self-improvement/agent_core.py success "<主要成就>"
python3 ~/.hermes/self-improvement/agent_core.py improve "<领域>" "<改进内容>" "<效果>"
```

### 4. 告知用户
用一段简洁的中文总结：
- 今天做成了什么（最多 3 条）
- 发现了什么可改进的地方
- 明天会主动做什么（1-2 条）

## 格式要求
中文，简洁，有数据（不用"很棒"这类模糊词）。
