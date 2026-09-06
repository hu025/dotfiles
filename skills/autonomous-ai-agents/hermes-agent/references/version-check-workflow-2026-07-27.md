# hermes-agent 版本检查正确流程 (2026-07-27)

## 教训

用户说"已是最新"但实际 PyPI 上有更新的包未显示。根因：
1. 本地 `pip show`/`pip index versions` 只查 PyPI 索引
2. PyPI 可能因 `Requires-Python` 限制不显示最新版本
3. 正确做法：**同时查 GitHub API**，取真实最新版本

## 正确检查流程

```bash
# 1. 查 PyPI（本地缓存）
pip index versions hermes-agent

# 2. 查 GitHub（真实最新）
curl -s --max-time 10 "https://api.github.com/repos/NousResearch/hermes-agent/releases/latest" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('GitHub latest:', d['tag_name'], '\nPublished:', d['published_at'])"

# 3. 查当前安装的版本
pip show hermes-agent | grep Version

# 4. 查 git commit（如果 git clone 安装）
cd ~/.hermes/hermes-agent && git log --oneline -1
```

## GitHub vs PyPI 版本差异场景

| 场景 | GitHub | PyPI | 原因 |
|------|--------|------|------|
| Python 3.14 环境 | 0.19.0 | 0.15.2 (最高) | `Requires-Python >=3.11,<3.14` |
| 网络超时 | 0.19.0 | 0.15.2 | PyPI 已同步但 git fetch 失败 |
| 刚发布 | v2026.7.20 | 可能未同步 | PyPI 同步延迟 |

## 本次实际情况（2026-07-27）

- GitHub 最新：`v2026.7.20` / `0.19.0`（发布于 2026-07-20）
- PyPI 可见：`0.15.2`（Python 3.14 兼容上限，`Requires-Python >=3.11,<3.14`）
- 本地安装：`0.15.2`

**升级尝试结果：**
- `pip install --upgrade hermes-agent==0.19.0` → ❌ PyPI 版本过滤，pip 最高只能取 0.15.2
- `pip install git+https://...@main` → ❌ GitHub git 操作（git-upload-pack）超时（120s），codeload CDN 也超时
- `git fetch origin main` → ❌ 超时，但 `curl api.github.com` 成功（API 走不同路由）

**结论**：Python 3.14 环境下暂时无法升级到 0.19.0，需等兼容版本或降级 Python 到 3.12。

**可选升级路径：**
1. **降级 Python**：`pacman -S python311`，重建 venv，再 pip 装 0.19.0
2. **CDN tarball**（网络好转后）：`curl -sL "https://codeload.github.com/.../v2026.7.20" -o /tmp/hermes.tar.gz`，解压覆盖
3. **等待** PyPI 发布 Python 3.14 兼容的 0.15.x 补丁版本
