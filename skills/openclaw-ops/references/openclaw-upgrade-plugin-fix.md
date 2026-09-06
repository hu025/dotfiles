# OpenClaw 升级插件修复参考

## 2026-09-02 更新：2026.7.1-2 → 2026.8.1

### 问题链
1. 升级 core 后 crash-loop breaker 触发 → `openclaw doctor --fix` 迁移数据库
2. 仍有 breaker → SQLite 修复：`UPDATE gateway_boot_lifecycle SET outcome="clean_stop" WHERE outcome="startup_failed"`
3. sessions.json 未迁移 → 重命名为 `.bak`
4. qqbot 报 `ERR_PACKAGE_PATH_NOT_EXPORTED: Package subpath './plugin-sdk'` → 升级插件：`openclaw plugins update @tencent-connect/openclaw-qqbot@latest`
5. feishu 版本漂移（2026.7.1） → `openclaw plugins update feishu`

### 完整升级后启动命令
```bash
pkill -f openclaw-watchdog && sleep 2
npm install -g openclaw@latest
openclaw plugins update @tencent-connect/openclaw-qqbot@latest
openclaw plugins update feishu
openclaw doctor --fix
bash /home/saber/.hermes/openclaw-watchdog.sh &
sleep 40
curl -s http://127.0.0.1:18888/health
openclaw gateway call health --json
```

### ERR_PACKAGE_PATH_NOT_EXPORTED 临时补丁
若 `plugins update` 无效，手动修复 bundled openclaw package.json：
```python
import json, glob
for path in glob.glob('/home/saber/.openclaw/npm/projects/tencent-connect-openclaw-qqbot-*/node_modules/@tencent-connect/openclaw-qqbot/node_modules/openclaw/package.json'):
    with open(path) as f:
        d = json.load(f)
    if './plugin-sdk' not in d.get('exports', {}):
        d['exports']['./plugin-sdk'] = d['exports'].get('./plugin-sdk/core', './plugin-sdk/core')
        with open(path, 'w') as f:
            json.dump(d, f, indent=2)
        print('Fixed:', path)
```

### 验证命令
```bash
# 查看插件加载状态
openclaw gateway call health --json | python3 -c "
import sys, json
d = json.load(sys.stdin)
loaded = d.get('plugins', {}).get('loaded', [])
errs = d.get('plugins', {}).get('errors', [])
print('Loaded:', loaded)
for e in errs:
    print('ERROR:', e.get('id'), str(e.get('error',''))[:200])
"

# 验证 QQ WebSocket 连接
strings /home/saber/.hermes/openclaw-watchdog.log | grep -E 'WebSocket connected|Gateway ready|qqbot.*ready'

# 检查 crash-loop breaker
tail /home/saber/.hermes/openclaw-watchdog.log | grep breaker
```
