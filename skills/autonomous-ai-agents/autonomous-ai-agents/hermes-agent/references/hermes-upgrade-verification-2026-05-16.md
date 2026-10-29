# hermes-agent 升级验证与网络隔离场景 (2026-05-16)

## 核心教训：版本判断优先顺序

当 git fetch 因网络问题失败时，**不要只看 git log 判断版本**。使用多信号验证：

```bash
# 1. 运行中的进程版本（最可靠）
./venv/bin/hermes --version
# → Hermes Agent v0.14.0 (2026.5.16)

# 2. pip 元数据
pip show hermes-agent | grep Version

# 3. 源码 pyproject.toml
grep '^version' pyproject.toml

# 4. git log（可能落后）
git log --oneline -1
```

**重要**：如果 `hermes --version` 显示 v0.14.0 但 git log 显示 v0.13.0 的 commit，说明代码通过 pip install 或手动解压 tarball 已经更新，git 只是没有拉取成功。运行中的系统**已经是新版**，无需再折腾 git。

## 本次升级结果

- **目标**：v0.13.0 (v2026.5.7, commit `498bfc7bc`) → v0.14.0 (v2026.5.16, commit `8487dfb`)
- **结果**：工作目录和 venv 已运行 v0.14.0（hermes --version 确认）
- **git 状态**：停留在 v0.13.0 commit（网络原因无法 fetch）
- **新功能文件已存在**：
  - `tools/computer_use_tool.py` (39 行)
  - `tools/video_generation_tool.py` (561 行)
  - `tools/music_generation_tool.py` (138 行)
  - `tools/x_search_tool.py` (424 行)
  - `tools/lazy_deps.py` (608 行)
  - `agent/transports/codex_app_server.py` (368 行)
  - `agent/plugin_llm.py`
  - `agent/video_gen_provider.py`
  - `plugins/music_gen/`
- **pyproject.toml**：已更新为 `version = "0.14.0"`
- **pip 已安装**：Version: 0.14.0，Location: venv

## 网络隔离升级路径（无 git fetch）

当 SSH (git-upload-pack) 和 HTTPS git 均超时时：

### 方式 A：curl CDN tarball（推荐）

```bash
# 直接 CDN（443端口，路由独立）
curl -L "https://codeload.github.com/NousResearch/hermes-agent/tar.gz/v2026.5.16" \
  -o /tmp/hermes.tar.gz

# 断点续传（如果下载中断）
curl -L -C - "https://codeload.github.com/NousResearch/hermes-agent/tar.gz/v2026.5.16" \
  -o /tmp/hermes.tar.gz
```

### 方式 B：API tarball

```bash
curl -L "https://api.github.com/repos/NousResearch/hermes-agent/tarball/v2026.5.16" \
  -o /tmp/hermes.tar.gz
```

### 解压覆盖安装

```bash
cd ~/.hermes/hermes-agent
tar -xzf /tmp/hermes.tar.gz --strip-components=1

# 验证
./venv/bin/hermes --version

# 更新 venv 中的包
./venv/bin/pip install -e . --quiet

# 重启 gateway
systemctl --user restart hermes-gateway.service
```

### 验证解压完整性

```bash
# 检查 entry 数量（v0.14.0 应有 ~2236 条）
tar -tzf /tmp/hermes.tar.gz | wc -l

# gzip 头部校验
python3 -c "import gzip; gzip.GzipFile('/tmp/hermes.tar.gz').read(512); print('gzip OK')"
```

## v0.14.0 重大更新（2026-05-16 发布）

- Windows 原生支持 (WSL 之外的原生 Windows)
- `pip install hermes-agent` 直接安装
- Lazy dependencies（按需加载工具依赖）
- Supply-chain 安全审计（CI/CD 自动检查）
- OpenAI 兼容本地代理
- 冷启动减少 19 秒
- CDP 加速 180x（browser 工具）
- 新 slash 命令：`/handoff`
- 新工具：`vision_analyze`, `x_search`, `computer_use`
- 新工具集：`video`, `computer_use`
- 新插件：`music_gen/minimax/`, `image_gen/minimax/`
- 新平台适配器：msgraph_webhook, slash_access
- 80+ 新测试文件（总计 ~900 测试文件）