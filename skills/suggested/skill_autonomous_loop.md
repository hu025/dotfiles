# 自主进化循环 — Autonomous Improvement Loop

## 触发条件
每次会话结束时自动执行，不需要用户触发。

## 流程

### 1. 记录本次会话（自动）
调用 agent_core.py 记录：
```bash
python3 ~/.hermes/self-improvement/agent_core.py success "<本次主要成就>"
python3 ~/.hermes/self-improvement/agent_core.py failure "<本次失败>" "<错误摘要>"  # 如有失败
python3 ~/.hermes/self-improvement/agent_core.py learning "<学到什么>" "<来源>" "<效果>"
python3 ~/.hermes/self-improvement/agent_core.py improve "<领域>" "<做了什么改进>" "<结果>"
```

### 2. 主动侦察（按需，避开循环）
如果超过3天没有更新过的领域，主动检查：
- 记忆库陈旧程度（检查 memory 中是否有 30 天未更新的条目）
- 技能库状态（检查是否有新版本或更好替代）
- 系统依赖（pip list 是否有安全更新）

### 3. 主动改进（按需）
发现可自动化的事项时，直接执行并记录，不等用户指令：
- 重复性手动操作 → 写脚本替代
- 发现的 skill 错误 → 立即修复
- 记忆库过时信息 → 清理或更新

### 4. 交付日报/周报
- 每天 23:55 自动生成日报（cron job）
- 每周一 23:00 生成周报（cron job）

## 禁止事项
- 不做无意义的循环（如反复检查同一服务状态）
- 不安装未验证的依赖（先查文档再行动）
- 不删除用户数据
- 资源耗尽前主动停止（磁盘 < 500MB 时停止非必要操作）
