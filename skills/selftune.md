---
name: selftune
description: SelfTune agent skill observability and self-improvement toolkit. Triggers: "skills health", "skill drift", "which skills are working"
---

# SelfTune — Agent Skill Observability & Self-Improvement

> 2026-09-14 research — 新发现工具，skill sprawl 问题的一站式解法

## 核心定位

**SelfTune = Skill 资产的可观测性 + 自动进化平台**

解决的问题：
- 技能分散在多个 agent 的多个目录里（Hermes skills/、Claude Code skills/、Codex skills/...）
- 同一技能多个副本，不知道哪个是最新
- 技能描述与实际使用模式不匹配（用户说"做 PPT"，什么都没触发）
- 技能表现好不好只能靠猜测，没有数据

---

## 核心功能

### 1. Skill 发现与清点
```bash
npx selftune@latest doctor                        # 诊断本机所有 skill 位置
npx selftune@latest skills audit --json           # 完整审计，JSON 输出
```
- 扫描所有支持的 agent home 目录（Hermes、Claude Code、Codex、OpenCode、Pi）
- 识别重复安装、版本漂移、需要修复的技能

### 2. Skill 健康度检测
```bash
npx selftune@latest skills consolidate --all-safe --dry-run --json
```
- 发现"应该触发但没触发"的技能（undertriggering）
- 检测版本冲突、孤立副本
- 提供修复建议，不自动删除任何东西（dry-run 默认）

### 3. Skill Set（技能集）管理
```bash
# 从项目捕获当前使用的技能
npx selftune@latest sets capture --project /path/to/project --json

# 预览部署计划（安装前）
npx selftune@latest sets plan --set <set-name> --project /path/to/project --json
```
- Skill Set = 精确版本锁定的技能集合
- 跨 agent 同步：同一套技能可以在 Claude Code、Hermes、Codex 中使用同一版本
- 预览安装目标，不会有意外文件变更

### 4. 自动 Skill 进化（核心创新）
SelfTune 从真实会话中学习，**自动重写技能描述**以匹配用户实际说话方式：

```
观察 → 检测 gap → 生成改进提案 → 验证 → 自动回滚
```
- 7 个实时 hook 捕获每次查询和触发结果
- 识别"你说'做PPT'但技能叫'create-presentation'"的语义漂移
- 众包进化提案（团队版）：匿名用户信号汇聚

### 5. Skill 分发
```bash
# 创建私有分享包（精确版本、不可变）
# recipient 需要许可证验证
# 链接可过期、可撤销
```
- 不上传技能库到云端（默认本地）
- 云服务仅用于团队分发，不持有个人技能库

---

## 架构设计

### 三个入口
| 入口 | 用途 |
|------|------|
| **Agent Skill** | 安装后告诉 agent "initialize selftune"，之后 agent 自己管理 |
| **Desktop App** | 可视化浏览所有技能、证据、改进历史 |
| **CLI** | 自动化工作流、CI 集成 |

### 数据边界
- Skill 文件、位置、会话历史**默认本地存储**
- Cloud 仅在明确需要团队分发时才启用
- **Open Source + MIT 许可证**

### 验证回路
```
真实会话观察 → gap 检测 → 提案生成 → 会话验证 → 通过则部署 / 失败则自动回滚
```

---

## 安装方式

```bash
# 1. 作为 agent skill 安装
npx skills add selftune-dev/selftune

# 2. 初始化
告诉 agent："initialize selftune"

# 3. 本机诊断
npx selftune@latest doctor
```

**前置条件**：
- Node.js 22+ 或 Bun
- 至少一个支持的 agent CLI（Claude Code / Codex / OpenCode / OpenClaw / Pi）
- 至少一个已安装的 skill 或包含 skill 文件夹的项目

---

## 对 Hermes Agent 的价值

### 立即可用
1. **技能健康度检测**：运行 `selftune audit` 诊断 Hermes 所有 skills 的状态
2. **跨 agent 同步**：如果同时使用 Claude Code 或 Codex，SelfTune 能统一管理所有 agent 的技能版本
3. **undertriggering 检测**：发现当前"应该触发但没触发"的技能，填补描述语义缺口

### 与现有架构的互补
- **hermes-skill-library-manager**：侧重于技能创建/编辑
- **SelfTune**：侧重于技能运行时观测 + 自动进化（基于真实会话数据）
- 两者结合 = 完整的技能生命周期管理

### 限制
- OpenClaw adapter 是实验性的（已知已卸载）
- 主要支持 Claude Code（最成熟），Codex/OpenCode 次之
- 自动进化功能在 Team 版（$49/月），个人用 Community 版（免费 5 skills）

---

## SelfTune CLI 速查

```bash
# 诊断
npx selftune@latest doctor

# 审计
npx selftune@latest skills audit --json
npx selftune@latest skills consolidate --all-safe --dry-run --json

# 技能集
npx selftune@latest sets capture --project /path/to/project --json
npx selftune@latest sets plan --set <name> --project /path --json

# 配置
selftune library configure   # 连接到 SelfTune Cloud 或自托管
selftune library sync        # 同步库
selftune library status      # 查看状态
selftune diagnostics         # 诊断
```

---

## 来源链接
- 官网：https://selftune.dev
- GitHub：https://github.com/selftune-dev/selftune
- NPM：https://npmjs.com/package/selftune
- 文档：https://docs.selftune.dev
