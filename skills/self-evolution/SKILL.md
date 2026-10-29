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
python3 ~/.hermes/self-improvement/agent_core.py success "<做了什么>" "<详细说明>"

# 失败（如有）
python3 ~/.hermes/self-improvement/agent_core.py failure "<失败的事>" "<错误信息>"

# 学到新东西
python3 ~/.hermes/self-improvement/agent_core.py learning "<学到什么>" "<来源>" "<效果>"

# 改进了什么
python3 ~/.hermes/self-improvement/agent_core.py improve "<领域>" "<改进内容>" "<结果>"

# 同步到 hermes
~/dotfiles/bin/sync-skills

# commit dotfiles
~/dotfiles/bin/deploy-dotfiles push
```

## 主动侦察（每会话至少做一次）

### 1. 系统状态
```bash
python3 ~/.hermes/self-improvement/agent_core.py status
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

## 「全部修复」的执行方法论

用户说「仔仔细细检查」「全部修复」时，要的是**整件事做完**，不是找到第一个问题就汇报。执行顺序：

1. **先扫一遍再动手** — 跑一遍所有健康面（磁盘、DB、服务、日志错误模式、cron 状态、数据源），把问题**列全**再按严重度排序。逐个发现逐个汇报会让用户以为已经结束了。
2. **每个修复都要有真实验证输出** — 改完跑一遍确认，而不是「应该好了」。工具输出是唯一证据。
3. **区分「已修好」和「不可修」** — 网络层封锁、平台架构限制这类要**直说不可修并给出诊断方法**，不要写成待办。把它记成「永久不能用」是错的：写「先跑这个诊断确认，resolver 可能会变」。
4. **修复后自己验证一遍修复路径** — 比如把刚修好的东西改回坏的状态，确认巡检能自动发现并修回来。
5. **自建的工具/脚本本身也会有 bug** — 写完必须实跑。我这次写巡检脚本时自己踩了三个坑（curl 状态码提取、日志时间窗、cron 失败判定），全是测试才发现的；不实跑就会每天给用户发假警报。

**汇报口径**：先给结论（修好了什么、还剩什么不可修），再给验证数据。**不把「计划做」说成「已做完」**——本轮就有封装脚本写完但没跑验证的情况，应明确说明。

## 补自旧副本的独有内容（self-evolution，合并于 2026-10-29）

# pip show 显示已装，但 import 失败 → 检查模块名是否与包名不同
HP=$(ls ~/.hermes/hermes-agent/venv/bin/python3 2>/dev/null || ls ~/.hermes/hermes-agent/.venv/bin/python3 2>/dev/null)
"$HP" -m pip show <pkg>  # 查包信息
"$HP" -c "import <pkg>"  # 试 import
# 例：letta 包 → 模块名是 letta_code（非 letta）
# 检查最新 cron 输出是否有 402 错误（MiniMax 额度耗尽）
ls -lt ~/.hermes/cron/output/ | head -3

**版本检查**：`hermes --version` + `hermes update --check`。当 GitHub 有新版本但 PyPI 未同步时，用 `git fetch cnb --tags && git checkout <tag> && pip install -e .` 手动升级。

## agent_core.py 记录命令

```bash
python3 ~/dotfiles/self-improvement/agent_core.py success "<做了什么>" "<详细说明>"
python3 ~/dotfiles/self-improvement/agent_core.py failure "<失败的事>" "<错误信息>"
python3 ~/dotfiles/self-improvement/agent_core.py learning "<学到什么>" "<来源>" "<效果>"
python3 ~/dotfiles/self-improvement/agent_core.py improve "<领域>" "<改进内容>" "<结果>"
```
