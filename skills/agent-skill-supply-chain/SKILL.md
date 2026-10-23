---
name: agent-skill-supply-chain
description: "Use when installing, updating, or publishing agent skills (SKILL.md). Covers OWASP AST02 provenance controls, version pinning/immutability, scanner-bypass evidence, and the 5-layer install hardening pattern."
metadata:
  author: self
  version: "1.0.0"
  owasp: AST02
---

# Agent Skill 供应链安全（AST02）

Skill 不是被动文档，是**运行时的可执行文本**。OWASP Agentic Skills Top 10 把供应链列为 AST02（Critical）——因为 skill 继承 agent 的全部凭证集，被污染的 skill 拿到的不是沙箱权限，是 agent 的完整权限。

## 何时用这个技能

- 从任何非本地来源安装/更新 skill（marketplace、GitHub repo、他人分享）
- 给自己的 skill 目录做发布前审查
- 怀疑某个 skill 更新后行为变了（rug-pull）
- 审核别人提交的 skill PR

## 核心结论：扫描器不够用

**不要指望自动扫描替代流程控制。** 实测数据：

| 来源 | 发现 |
|---|---|
| Koi Security（2026-02，ClawHub 审计） | 2857 个 skill 中 **341 个恶意（11.9%）** |
| arXiv:2605.11418（2026-05） | 语义规避让治理期分类器放行率 **36.5%–100%**（取决于配置） |
| Trail of Bits（2026-06） | skills.sh / ClawHub 的"先发货后加固"模型，**所有兜底扫描器 1 小时内被绕过** |
| Unit 42（2026-02~05） | ClawHub 集成 VirusTotal + ClawScan 后仍持续有恶意 skill 逃逸；手法是**把文件撑大到超过扫描器处理阈值** |
| Air Security（2026-06-24） | 142836 个在线 skill 中 **17822（12.4%，670万次安装）** 依赖至少一个不可信外部资源 |
| Air Security（2026-07-02） | **925 个 skill 服务的 13.4 万 agent** 坐在可秒级劫持的来源上（作者账号被删、域名过期、云应用槽位释放）。研究者重注册 skills.sh 上最流行的视频生成 skill（原 11483 次安装）的已删作者账号，市场页面的星标/信任/安装量**全部保留** |

结论：**供应链防线必须是传统那一套**——内部/批准市场策展 + 版本锁定 + 控制谁能发布和更新。扫描器是补充，不是主体。

## 四种攻击面

1. **Registry Flooding** — 协调上传数百个恶意 skill 挤掉正常搜索结果
2. **Dependency Confusion** — 污染**嵌套依赖**而非顶层 skill，绕过表层扫描。实例：名为 "Summarize YouTube Videos" 的 skill 实际 import `yutube-dl-core`（typosquat），payload 在嵌套层
3. **Config-File Hijacking** — 在仓库配置文件（hooks、`.claude/settings.json`、`ANTHROPIC_BASE_URL`）里塞执行指令。**CVE-2025-59536 / CVE-2026-21852**：clone 并打开恶意仓库即触发 RCE + API key 外泄，用户看不到任何弹窗
4. **Maintainer Account Takeover** — 攻陷可信作者的账号，推带后门的版本

补充：**rug-pull**——初始版本审查通过后，作者再推恶意更新。只审首版是不够的，每次更新都要重新审。

## 落地：安装/更新前的 5 层检查

按 tech-leads-club/agent-skills 的 CLI defense-in-depth 实现。这五层每层独立成立，单点绕过不够用。

### 1. 名称净化（挡路径穿越）
```
去掉 / \ 路径分隔符
去掉 \0 : * ? " < > | （含 null 字节与 Windows 禁止字符）
去掉首尾的点和空格
折叠连续的点（消灭 ".."）
去掉前导点（挡隐藏文件）
截断到 255 字符
```
拦住：`../../../etc/passwd`、`skill\0name`、`/etc/passwd`、`.hidden`、`a`×300

### 2. 文件系统隔离（resolve 后再比）
对 `base` 和 `target` 都做 `normalize(resolve())`，然后要求 target 以 `base + sep` 开头或等于 `base`。用 OS 的 `sep` 拼接，防止 `/allowed/dir../escape` 这类前缀欺骗。**每次 write/read/delete 都过这一关**。

### 3. Symlink Guard（默认不信任）
- 用 `lstat()` 而非 `stat()`——不跟随链接，防 TOCTOU
- 解析最终 target，验证仍在允许目录内（链式链接也要查到底）
- 捕获 `ELOOP`（循环链接）并强制移除

### 4. Lockfile 完整性
- 严格 schema 校验每次读取，畸形条目拒绝而非静默吞掉
- 原子写：`备份 → 写 .tmp → rename`；进程中途被杀旧文件完好
- 每个 skill 记录全文件内容的 SHA-256 → 装后被改动可检测
- 删除必须有 lockfile 授权；`--force` 绕过要写审计日志

### 5. 审计轨迹（append-only）
```json
{"action":"install","skillName":"codenavi","agents":["cursor"],"success":1,"failed":0,"timestamp":"2026-02-25T10:00:00Z"}
{"action":"remove","skillName":"codenavi","agents":["cursor"],"success":1,"failed":0,"forced":false,"timestamp":"2026-02-25T11:00:00Z"}
```
JSON Lines，只追加永不覆盖。这是本机所有 skill 操作的取证记录。

## 落地：版本不可变 + 撤回账本

registry 侧最值得抄的设计（skills-yaml/registry，skm 工具规范）：

**精确版本目录不可变。** `vMAJOR.MINOR.PATCH` 一旦进入生产分支，其路径、文件类型、可执行位、字节内容全部冻结。修正必须发新版本号。CI 用 `task registry:check` 对比 `origin/main`，拒绝目录内的删除/新增/变更。别名（`latest`/`default` 符号链接）可以前移，但必须保持在包内且自洽。

**撤回不是删除。** 一个不能继续公开的版本（例如泄漏了私有基础设施或个人数据）：
1. 删掉版本目录
2. 在根 `WITHDRAWN.yaml` 记一笔：
```yaml
schema_version: 1
withdrawn:
  - coordinate: system/devops-manager@1.0.0
    withdrawn: "2026-09-19"
    reason: >-
      为什么这个版本不能继续发布，以及由什么替代。
```
3. 同一次变更里发布替代版本，把 `latest`/`default` 指过去，保证包仍可解析
4. 撤回记录**永久保留**——它是"为什么这个版本号解析为空"的答案

> 撤回不等于擦除。内容仍在 Git 历史、fork 和任何已 clone 的副本里。当作已公开处理，泄露本身另行处置。

**撤回的版本号选择看消费方看到的变化**：撤回若改变了 skill 告诉 agent 该做什么，至少是 minor release，不是 patch。

**依赖用精确坐标，不用范围。**
```yaml
metadata:
  skm-version: "0.1.0"
  skm-dependencies: "workspace/write-spec@0.2.0, workspace/review-changes@0.2.0"
```
每个坐标必须锁定同一可信 registry 中的精确版本、真实存在、且依赖图无环。skill 保持独立版本；bundle/release manifest 记录一组**测试过的组合**，但不强制 lockstep 升版。

**所有嵌套依赖锁到不可变 hash**，不是版本范围：
```
# 差：版本范围
requests>=2.25.0

# 好：锁 hash
requests==2.31.0 --hash=sha256:58cd2187c01e70e6e26505bca751777aa9f2ee0b7b4300988b709f44e013003f996
```

## 落地：签名与溯源（OWASP AST02 缓解措施）

1. **签名覆盖规范摘要**：签名必须覆盖 `SKILL.md` 的 canonical digest **加上所有声明的资源文件**——任何发布后篡改都使签名失效。标准方案 ES256 / ed25519。skill 格式还没有一等签名字段时，绑定可以放在 SKILL.md 的 `metadata` 扩展点。
2. **透明度日志**：registry 的所有操作（publish/update/delete）都要有类似 Certificate Transparency 的日志。
3. **吊销基础设施**：能吊销①整个签名密钥（连带所有它签的 skill）②按内容摘要吊销单个版本③整个发布者。host 在加载时查询吊销端点，缓存状态要有**有界新鲜窗口**。
4. **递归扫描依赖树**，不只扫顶层文件。
5. **内部镜像/白名单**：企业部署只从批准的镜像装。

## 审查清单

改动前后各跑一次：

- [ ] 这个 skill 有任何 unpinned 外部依赖吗？（域名、GitHub repo、pip/npm 包）
- [ ] 外部依赖的作者账号/域名健康吗？会不会被秒级劫持？
- [ ] 嵌套依赖里有没有 typosquat 风险？
- [ ] 配置文件（hooks / settings.json / env 覆盖）里有没有"打开即执行"的指令？
- [ ] 装完 skill 后，文件 SHA-256 记进 lockfile 了吗？
- [ ] 这次更新有没有改变它对 agent 的指令？（是→ 重新审查，不要继承旧信任）
- [ ] 单个 skill 文件大小是否异常大？（超过扫描器处理阈值是已知逃逸手法）

## 假阳性豁免

扫描器误报要走豁免清单，且**豁免必须带过期时间**，强制周期性复核——否则例外会变成永久例外：

```yaml
version: '1.0.0'
entries:
  - skill: my-skill
    code: W011
    reason: 从受信任的一方 API api.example.com 取数，是预期行为而非凭证外泄向量
    allowedBy: github.com/username
    allowedAt: '2026-01-01'
    expiresAt: '2027-01-01'
```
豁免清单进版本库、每个 PR 都被 review——不允许存在不可见的例外。

## 与本机现状的差距

Hermes 自带的 `skill_manage` / `~/.hermes/skills/` **没有**：lockfile、sha256 完整性记录、签名验证、吊销查询、append-only 审计日志。当前本机对 skill 供应链的防护**只等于**：git 仓库自身的提交历史 + 我作为 agent 的判断。本技能描述的是应当实现的控制，不是已存在的机制。

本地已有可复用工具：`~/dotfiles/skills/secret-scanning.md`、`skills/llm-security`、`skills/agent-runtime-guardrails`（运行时防御，与本文的**分发时**防御互补——不是替代关系）。

## 参考

- OWASP Agentic Skills Top 10 — AST02 Supply Chain Compromise: https://owasp.org/www-project-agentic-skills-top-10/ast02.html
- skills-yaml/registry VERSIONING.md（精确版本不可变 / WITHDRAWN.yaml 撤回账本）: https://github.com/skills-yaml/registry/blob/main/VERSIONING.md
- tech-leads-club/agent-skills SECURITY.md（CLI 五层防御 / 审计日志 / 扫描豁免）: https://github.com/tech-leads-club/agent-skills/blob/main/SECURITY.md
- Trail of Bits, *The Sorry State of Skill Distribution* (2026-06-03): https://blog.trailofbits.com/2026/06/03/the-sorry-state-of-skill-distribution/
- arXiv:2605.11418 *Under the Hood of SKILL.md*: https://arxiv.org/abs/2605.11418
- arXiv:2605.14460 *Payload-less Skills*: https://arxiv.org/abs/2605.14460
- Air Security: The Story of Skills / The Circus of Skills / SkillJacking — https://www.air.security/blog-posts/skilljacking
- JFrog Agent Skills Registry（商业实现参考）: https://jfrog.com/ai-catalog/skills-registry/
- Microsoft Agent Framework Skills（SKILL.md metadata 字段参考）: https://learn.microsoft.com/en-us/agent-framework/agents/skills