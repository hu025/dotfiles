---
name: github-pat-management
version: "1.0"
author: self
description: GitHub PAT 管理与 git push
---

# GitHub PAT 管理

## PAT 类型与权限

| 类型 | 创建地址 | push 权限 |
|------|---------|----------|
| Fine-grained | github.com/settings/tokens/new | ✗ 通常无（即使 repo=true）|
| Classic | github.com/settings/tokens/new | ✓ 需勾选 `repo` |

**经验**：Fine-grained PAT API 读 OK，但 `git push` 几乎总是 403。**创建仓库用 API，push 必须 Classic PAT**。

## 验证 Token

```bash
curl -s -H "Authorization: token $PAT" https://api.github.com/user | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('login','ERROR'))"
```

## 创建仓库

```bash
curl -s -X POST \
  -H "Authorization: token $PAT" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{"name":"仓库名","private":false}'
```

## Push（需 Classic PAT）

```bash
git remote set-url origin "https://${PAT}@github.com/USERNAME/REPO.git"
git push -u origin main
```

## 当前（2026-09-07）
- hu025/dotfiles 已创建，Fine-grained PAT push 返回 403，需换 Classic PAT
