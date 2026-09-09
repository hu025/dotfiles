# Secret Scanning — 凭证泄露检测 2026

## 四门防御模型

| Gate | 触发 | 工具 | 拦截能力 |
|------|------|------|---------|
| Gate 1: Pre-commit | 开发者本地 commit 前 | gitleaks / detect-secrets | 可 bypass（--no-verify），但拦 majority |
| Gate 2: CI diff scan | 每个 PR/push diff | gitleaks / betterleaks / GitGuardian | 拦 server-side secret |
| Gate 3: Git history sweep | 定时全量扫描 | trufflehog（验证型） | 找历史 secret，验证是否 still live |
| Gate 4: Platform monitoring | push 后自动触发 | GitHub Secret Scanning / GitGuardian | 通知 provider 自动 revocation |

> 单一工具≠覆盖。只跑 pre-commit 或只跑 CI 都是假安全。

---

## 工具选型决策树

```
需求: 快速 pre-commit + CI diff
└→ gitleaks (MIT, <1s/diff, 28k stars, feature-complete)
   └→ 但需持续开发? → betterleaks (MIT, 1.8k stars, 活跃)

需求: 历史扫描 + 验证 credential 是否 still live
└→ trufflehog (AGPL/commercial, 26k stars, 800+ verifier)

需求: 企业合规 + 公共 GitHub 监控 + 低误报
└→ GitGuardian (Commercial, ML 1-3% FP, SOC2/ISO27001)

需求: 已有 Semgrep SAST，想合并 secrets 检测
└→ Semgrep Secrets (AppSec Platform 的一部分)

需求: S3 bucket 内 secrets / PII
└→ AWS Macie / GCP Cloud DLP / Azure Purview
```

---

## Betterleaks — Gitleaks 官方继任者

> 原始作者宣告 Gitleaks feature-complete，专注 Betterleaks 开发。

**安装**:
```bash
# binary
curl -sSfL https://github.com/betterleaks/betterleaks/releases/latest/download/betterleaks_linux_amd64.tar.gz | tar -xz
sudo mv betterleaks /usr/local/bin/

# GitHub Action
- uses: betterleaks/betterleaks-action@v1
```

**核心优势** vs Gitleaks:
- **CEL 表达式验证**: 自定义 HTTP 验证逻辑（内部 API、数据库凭证等 TruffleHog 不覆盖的场景）
- **复合/多部件规则**: 声明相邻组件规则，通过 `components["rule-id"]?.secret` 关联分散的 token parts
- **BPE 分词**: cl100k_base 分词 + regex，CredData recall 98.6%（高于纯 regex）
- **完全兼容**: `.gitleaks.toml` / `GITLEAKS_CONFIG` / `gitleaks:allow` pragma 直接沿用

**配置示例** (`.betterleaks.toml`):
```toml
[rules.my-api-key]
description = "My internal API key"
regex = '''[aA][pP][iI]-?[kK][eE][yY].*['\"]([a-zA-Z0-9\-_]{32,})['\"]'''

[validation.my-api-key]
# CEL 表达式：自定义 HTTP 验证
expression = '''
http.send({
  method: "GET",
  url: "https://internal-api.example.com/validate",
  headers: {"X-API-Key": findings["my-api-key"].secret}
}).status == 200
'''
```

**GitHub Actions 用法**:
```yaml
name: Secret Scanning
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with: {fetch-depth: 0}
      - uses: betterleaks/betterleaks-action@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## TruffleHog — 凭证 live 验证

**核心能力**: 对每个候选 secret 调用 issuing API 验证是否 still active

```bash
# 扫描 git 历史
trufflehog git file:///path/to/repo \
  --json --no-update \
  | jq '.Results[] | select(.VerifiedCredential != null)'
```

**CI 集成** (只验证历史，不 blocking):
```yaml
- name: TruffleHog History Scan
  uses: trufflesecurity/trufflehog@main
  with:
    path: ./
    base: ${{ github.event.repository.default_branch }}
    head: HEAD
```

---

## Gitleaks — CI 快速拦截（Gate 1+2）

**GitHub Actions**:
```yaml
- uses: actions/checkout@v6
  with: {fetch-depth: 0}
- uses: gitleaks/gitleaks-action@v3
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}
```

**Pre-commit hook** (`.pre-commit-config.yaml`):
```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.0
    hooks:
      - id: gitleaks
```

---

## 最小化落地栈（推荐）

```yaml
# .github/workflows/secret-scanning.yml
name: Secret Scanning
on: [push, pull_request]

jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with: {fetch-depth: 0}
      - uses: betterleaks/betterleaks-action@v1   # 替换 gitleaks
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  trufflehog:
    runs-on: ubuntu-latest
    # 不 blocking，只报告 historical findings
    steps:
      - uses: actions/checkout@v6
        with: {fetch-depth: 0}
      - uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
```

> GitHub Secret Scanning 作为 Gate 4（自动 revocation）需要在 GitHub Settings 开启，无需 CI 配置。

---

## 误报率参考（2026 benchmark）

| 工具 | 误报率 |
|------|--------|
| Gitleaks（无调优）| 5-15% |
| TruffleHog 无验证 | 10-20% |
| Betterleaks | ~2-5% |
| GitGuardian ML | 1-3% |
| detect-secrets + baseline | 0-5% |

---

## 触发词

- "检查 secrets 泄露"
- "gitleaks 配置"
- "CI 凭证检测"
- "git 历史 secret 扫描"
