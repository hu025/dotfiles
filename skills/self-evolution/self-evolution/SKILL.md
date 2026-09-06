---
name: self-evolution
description: 自我进化操作手册。触发词：「强化」「进化」「自我改进」
---

# 自我进化操作手册

## 核心原则
- 每次会话结束前自动记录成就/失败/学习/改进
- 主动发现重复操作并自动化
- 技能错误立即修复，不拖延
- 进化过程全部 commit 到 ~/dotfiles

## 每次会话结束前

```bash
# 主要成就
python3 ~/dotfiles/self-improvement/agent_core.py success "<做了什么>" "<详细说明>"

# 失败（如有）
python3 ~/dotfiles/self-improvement/agent_core.py failure "<失败的事>" "<错误信息>"

# 学到新东西
python3 ~/dotfiles/self-improvement/agent_core.py learning "<学到什么>" "<来源>" "<效果>"

# 改进了什么
python3 ~/dotfiles/self-improvement/agent_core.py improve "<领域>" "<改进内容>" "<结果>"

# 同步到 hermes
~/dotfiles/bin/sync-skills

# commit dotfiles
~/dotfiles/bin/deploy-dotfiles push
```

## 主动侦察（每会话至少做一次）

### 1. 系统状态
```bash
python3 ~/dotfiles/self-improvement/agent_core.py status
```
关注：磁盘空间、核心服务状态、ESP32 连接（如适用）

### 2. 发现可自动化项
- 同一个操作出现 2 次以上 → 写脚本替代
- 手动流程超过 5 步 → 优化为 1-2 步
- 任何 skill 有错误/过时 → 立即修复

### 3. 检查记忆库
- 用户的隐含偏好（从重复行为推断）
- 陈旧信息（30 天未更新且不再相关）

## 每周架构审查（六维）

1. **模型层** — 当前模型是否最优？延迟/质量/成本平衡
2. **记忆层** — 矛盾信息？过时偏好？新增行为模式？
3. **技能层** — 错误/过时/可合并？用户反复请求的领域有技能覆盖？
4. **工具层** — 依赖安全？重复操作脚本化？
5. **浏览器自动化** — 稳定？新页面结构？
6. **自主改进** — 本周成功率趋势，最该改进的 1-3 点

## 禁止事项
- 不做无意义循环
- 磁盘 < 500MB 时停止非必要操作
- 不安装未验证的依赖
- 不删除用户数据

## 架构参考
详细 dotfiles 进化仓库模式：agent-engineering/self-evolution-monitor/references/dotfiles-evolution-architecture.md

## 进化速度控制
单次会话内：最多尝试 3 次同一问题的不同解法，3 次失败则记录 + 跳过。
单次尝试：超过 10 分钟无进展 → 记录失败 + 换方向。
