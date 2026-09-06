# OpenClaw 升级工作流参考

## 版本验证原则（每次升级前必做）

**不要**只看本地缓存、PyPI 页面或 npm view "latest" 标签就声称"已是最新"——必须实际查上游：

```bash
# 查真实最新版本
npm view openclaw dist-tags
openclaw --version   # 本地版本
```

对比后再决定是否升级。用户说过"你实际查一下"表明：未经上游核实就声称版本状态是违规行为。

---

## 2026-07-27 升级记录

### 背景
- 旧版本: OpenClaw 2026.6.10
- 新版本: OpenClaw 2026.7.1-2（npm 最新）
- update checker 报 2.0.0 但实际最新是 2026.7.1-2

### 步骤

1. **确认当前状态**
   ```bash
   openclaw --version
   # OpenClaw 2026.6.10 (aa69b12)
   ```

2. **彻底停止所有进程**
   - 不能只杀 node，watchdog 会立即拉起
   - 必须先 `pkill -f openclaw-watchdog`，再杀 node
   - 用 `kill -9` 确保干净

3. **npm 升级**
   ```bash
   npm install -g openclaw@latest
   # added 3 packages, and changed 306 packages in 1m
   ```

4. **验证版本**
   ```bash
   openclaw --version
   # OpenClaw 2026.7.1-2 (0790d9f)
   ```

5. **重启 watchdog**
   - 用 `terminal(background=true)` 启动（不能用 nohup/&）
   - 进程需要 ~20 秒完全就绪（高 CPU 启动阶段）

6. **验证就绪**
   ```bash
   curl -s http://127.0.0.1:18888/health
   # {"ok":true,"status":"live"}
   ```

### 关键观测点

- 升级后首次启动：CPU 110-130%，内存 ~500MB，持续约 20 秒
- 日志文件换新：`/tmp/openclaw/openclaw-2026-07-27.log` 被重新创建
- session 持久化：sessionId 不变（`84f87b23-acd4-4435-86a1-5febc2edbaae`）
- 正常退出码：exit=0 表示 QQ WebSocket 正常关闭，不是崩溃

### 潜在风险

- `@martian-engineering/lossless-claw` 要求 `>=2026.5.28`，目前 `invalid`（版本过高）
  - 实际运行未发现问题，但需留意
- `@tencent-connect/openclaw-qqbot@1.7.2` 的 openclaw 版本约束也需观察
