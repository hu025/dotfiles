---
name: pc-disk-maintenance
description: PC 磁盘状态检查与安全清理 — 分析磁盘占用、识别可清理目标、清理不常用项目。触发词：检查磁盘、清理磁盘、磁盘满了、哪些不常用、磁盘占用、检查电脑磁盘
triggers:
  - 检查磁盘
  - 清理磁盘
  - 磁盘满了
  - 哪些不常用
  - 磁盘占用
  - 检查电脑磁盘
  - 清理不安全的
---

# PC 磁盘维护

## 一句话结论优先

用户只问磁盘状态或问"哪些不常用" → 先给总览表格，再给可清理项列表。

## 磁盘占用总览

```bash
df -h / && echo "---" && du -sh /home/saber/* /home/saber/.* 2>/dev/null | sort -rh | head -20
```

## 大目录深度分析

识别出大目录后，深度查看内容：
```bash
# .gradle 构建缓存
du -sh /home/saber/.gradle/* 2>/dev/null | sort -rh

# venvs
du -sh /home/saber/.venvs/* 2>/dev/null | sort -rh

# .local/share (pnpm/uv/icons)
du -sh /home/saber/.local/share/* 2>/dev/null | sort -rh | head -10

# npm 全局包
ls /home/saber/.npm-global/lib/node_modules

# .cache 细项
du -sh /home/saber/.cache/* 2>/dev/null | sort -rh | head -10
```

## 安全清理清单

**可安全清理**（不影响运行）：

| 目标 | 大小参考 | 命令 |
|------|---------|------|
| npm 全局缓存 | ~1-3G | `rm -rf ~/.npm` |
| npm 全局已安装包 | ~300-500M | `rm -rf ~/.npm-global/lib/node_modules/openclaw` |
| uv 下载缓存 | **~4-9G** | `uv cache clean` |
| pip 下载缓存 | **常驻 1-3G** | `pip cache purge`（官方命令，比 rm 干净；输出 "Files removed: N (X MB)"） |
| pip 解包残留 | 一次安装可达 5.6G | `rm -rf ~/.hermes/cache/scratch/pip-unpack-*`（见「cache/scratch 全量清扫」） |
| `~/.local/share/uv/python` 旧版本 | ~130-150M/版本 | 删掉无人引用的 cpython-3.10/3.11（见下节） |
| yay（AUR）缓存 | ~50-300M | `rm -rf ~/.cache/yay` |
| openclaw cache | ~40M | `rm -rf ~/.cache/openclaw` |
| Espressif IDF 缓存 | ~300-800M | `rm -rf ~/.cache/Espressif` |
| pacman 包缓存 | ~200M | **先别删！** 见下方「pacman 缓存」专节 |
| hermes_workspace/downloads/ | ~146M | `rm -rf ~/hermes_workspace/downloads/`（旧portable工具备份） |
| hermes_workspace/hermes-python-portable/ | ~248M | `rm -rf`（venv已替代） |
| hermes_workspace/hermes-portable-venv/ | ~111M | `rm -rf`（venv已替代） |
| package/ | 可变 | OpenClaw源码（root安装，rm报错权限不够，只能忽略） |
| hermes sessions 旧文件 | >3天 | `find ~/.hermes/sessions/ -name "*.json" -mtime +3 -delete` |
| state.db 搜索索引 | 可回收大半 | `hermes sessions optimize-storage --yes`（见下节，**需先停 gateway**） |
| hermes-agent/.git 冗余 pack | 100-200M | `cd ~/.hermes/hermes-agent && rm -f .git/objects/pack/tmp_pack_* && git gc --prune=now` |
| state-snapshots 旧快照 | 每个 ~1.3M | 保留最新一个，其余 `rm -rf` |
| cron output 旧产物 | >14天 | `find ~/.hermes/cron/output -type f -mtime +14 -delete` |
| /tmp 构建产物 | 不固定 | `rm -f /tmp/xiaoclaw_build*.log /tmp/idf-build*.log` |

## Hermes 升级残留：每次升级都可能留下一整个废弃运行时

Hermes 升级不只是换代码，还会**重新 pin 整套运行时**。旧的不会自动删，
一次升级就能留下 1.5G+ 残留。这是磁盘持续增长的隐蔽原因。

**① 废弃的 managed environment（单个 ~805M，最容易被忽略）**

```bash
ls ~/.hermes/installs/*/environments/     # 升级一次多一个目录
# 判断哪个是活跃的：facts.json 指向谁，谁就是当前的
grep -o 'environments/[a-f0-9]*' ~/.hermes/installs/*/facts.json
```
`facts.json` 里 `packages.venv.environment` 指向的环境**必须保留**，
其余按 mtime 全删。删前用 `lsof +D <路径>` 确认无进程占用。

**② 旧版 Python / Node / uv 运行时（427M + 227M + 54M）**

```bash
ls -d ~/.hermes/tools/{python,node,uv}-*        # 同类会有多个版本
ps -eo cmd | grep -oE 'tools/(python|node)-[0-9.]+[^/]*' | sort -u   # 进程实际用哪个
grep -rl 'python-3.14.7\|node-26.7' ~/.hermes/*.yaml ~/.hermes/scripts/ 2>/dev/null
```
**三条同时成立才可删**：config 无引用、无进程在用、同目录有更高版本。
实测删 python-3.14.7 + node-26.7.0 + uv-0.12.3 一次回收 708M，
gateway 照常运行（它用的是新 repin 的 3.14.9）。

**③ state.db 的临时备份会堆在 scratch**

每次 `sessions prune` / model 切换都会在 `~/.hermes/cache/scratch/` 留一个
`state.db.bak-*`（实测每个 322M，两个就 644M）。删之前必须验证主库：
```bash
sqlite3 ~/.hermes/state.db "PRAGMA integrity_check;"     # 期望 ok
sqlite3 ~/.hermes/state.db "SELECT COUNT(*) FROM messages;"
stat -c '%y %n' ~/.hermes/state.db ~/.hermes/cache/scratch/state.db.bak-*
```
主库完整性 ok **且** mtime 比备份更新 → 备份可删。

**④ 陈旧的 `.git/hermes-update.lock`**

升级中断会留下锁文件，**阻塞下次自动升级**（且脚本可能误报成功）。
```bash
head -1 ~/.hermes/hermes-agent/.git/hermes-update.lock   # 拿到 PID
ps -p <PID> >/dev/null 2>&1 && echo '进程还活着，不能删' || rm -f 该文件
```
PID 已死 = 陈旧锁，可安全清除。这是「版本一直升不上去」的常见根因之一。

## pacman 缓存：看着 200M，实测多半不该删

**先算再删，别无脑 `paccache`**。这台机器上 `paccache` 不存在，
`pacman -Sc --noconfirm` 也会卡在第二个交互询问（"打算删除无用的软件库？"），
`echo y |` 也喂不进去。

正确做法是自己算——**只删「未安装包」和「已安装包的旧版本」**：

```python
import os, re
from collections import defaultdict
CACHE, INST = '/var/cache/pacman/pkg', '/var/lib/pacman/local'
installed = defaultdict(list)
for d in os.listdir(INST):
    m = re.match(r'^(.+)-([^-]+-\d+)$', d)
    if m: installed[m.group(1)].append(m.group(2))
files = [f for f in os.listdir(CACHE) if re.search(r'\.pkg\.tar\.(zst|xz|gz)$', f)]
by_name = defaultdict(list)
for f in files:
    m = re.match(r'^(.+)-([0-9][^-]*-[0-9]+)-([a-z0-9_]+)\.pkg\.tar\.[^.]+$', f)
    if m: by_name[m.group(1)].append((m.group(2), f))   # 注意 arch 段不能漏，否则全判为未匹配
todel = [f for n,v in by_name.items() for x,f in v if x not in installed.get(n, [])]
print(f"缓存 {len(files)} 个，其中待删 {len(todel)} 个")
```

**实测结论（2026-10-29）**：37 个缓存包**全部是当前已安装版本**，
待删 0 个。`pacman -Sc` 保留它们是正确行为——删了会失去系统回滚能力。
**所以「pacman 缓存 200M 可清」在维护良好的机器上通常是伪命题**，
先跑上面的脚本看真实待删数量，别把 200M 算进预期收益。

**正则陷阱**：解析包名必须包含 `-<arch>` 段（`confuse-3.3-5-x86_64.pkg.tar.zst`），
漏掉 arch 会让 100% 的文件判为「未匹配」，脚本输出「待删 0」看着像没事，
实际是根本没解析成功。判断解析是否正常看「未匹配」计数。

## state.db 膨胀：重建搜索索引而不是删数据

`~/.hermes/state.db` 到了 GB 级时，膨胀的不是对话数据而是**搜索索引**。
旧版 FTS5 布局会把每条消息的正文存两份，再加一份独立的 contentless trigram
索引（中文全文检索用）。以 14 万条消息为例，索引层就吃掉近 500MB。

**先定位，再动手**：

```bash
# 按表看谁占的多（需要 dbstat，SQLite 自带）
sqlite3 ~/.hermes/state.db "
select name, sum(pgsize) as bytes from dbstat
group by name order by bytes desc limit 12;"

# 哪些索引是 trigram（中文检索依赖，不能直接删）
sqlite3 ~/.hermes/state.db "
select name, sum(pgsize) from dbstat where name like 'messages_fts%'
group by name order by sum(pgsize) desc;"
```

**正确解法是重建而不是删除**：`hermes sessions optimize-storage` 会把索引迁移到
紧凑的 v23 external-content 布局，**只重建索引，不动任何对话数据**，
并且可中断续跑。

```bash
# 前置：备份（VACUUM INTO 不锁库）
sqlite3 ~/.hermes/state.db "VACUUM INTO '$HOME/.hermes/backups/manual/state-$(date +%Y%m%d-%H%M%S).db';"

# 磁盘预检：重建 + VACUUM 需要约等于当前库大小的空闲空间
free_mb=$(( $(df -Pm ~/.hermes | awk 'NR==2{print $4}') ))
db_mb=$(( $(stat -c%s ~/.hermes/state.db) / 1024 / 1024 ))
[ "$free_mb" -lt "$db_mb" ] && echo "空间不足，先清理"

# 执行（需无其它进程持有 state.db）
hermes sessions optimize-storage --yes
```

**硬性前提：gateway / dashboard / cron worker 都不能在跑**。在活着的写入者身上
重写库，会让所有 agent 拒绝接收 turn。agent 自己做不到停 gateway（PPID 就是它），
必须请用户在平台内发 `/restart`，重启后再跑。

**不要手删 FTS 索引表**：Hermes 的会话恢复逻辑会检查 `messages_fts` 与
`messages_fts_trigram` **两个表同时存在**，缺一即判定索引损坏并触发修复流程。
trigram 索引是中文检索的活路径，只能通过官方命令重建。


**hermes_workspace 中 portable 工具判断规则**：`python-uv/`（含 cpython 二进制）和 `node-v*/`（含 node 二进制）是 hermes CLI 运行时依赖，**勿删**。`hermes-python-portable/` 和 `hermes-portable-venv/` 是旧版 venv 便携备份，已被 `~/.hermes/hermes-agent/venv/` 替代，可删。

## state.db 会话裁剪：批量删除而不是逐个 CLI

`hermes sessions prune` 只删 **ended** 的 session；开放态（`ended_at IS NULL`）
的必须逐个 `hermes sessions delete <id>`，每次一个进程，几百个要跑十几分钟。
更快的方式是直接写 SQL 批量删——**前提是先跑 prune 把大部分转成 ended 态**。

```bash
# ① 先看各 source 的会话存量与活跃情况
sqlite3 ~/.hermes/state.db "
select source,
       sum(case when ended_at is null then 1 else 0 end) as open,
       sum(case when ended_at is not null then 1 else 0 end) as ended,
       count(*) as total
from sessions group by source order by total desc;"

# ② 批量删除 ended 态（PROTECT 里放当前活跃 session）
python3 - <<'EOF'
import sqlite3
c = sqlite3.connect('/home/saber/.hermes/state.db')
c.execute("PRAGMA foreign_keys=OFF")
PROTECT = ("<当前活跃 session id>",)
rows = c.execute("""select id from sessions
 where source in ('qqbot','weixin','feishu') and ended_at is not null""").fetchall()
todo = [(sid,) for sid, in rows if sid not in PROTECT]
c.executemany("delete from messages where session_id=?", todo)
c.execute("delete from messages_fts where rowid not in (select id from messages)")
c.execute("delete from messages_fts_trigram where rowid not in (select id from messages)")
c.executemany("delete from sessions where id=?", todo)
c.commit()
print("deleted", len(todo))
EOF
```

**Pitfall — 保护活跃 session 的过滤条件必须写死**。用
`order by started_at desc limit 1` 取「最新的」会选到正在跑长任务的
session，删掉之后 gateway 会丢弃它的完成通知（「completion targets
permanently-gone session」），用户永远收不到那次任务的结果。保护名单
要么写死具体 id，要么加「最近 N 分钟内创建的跳过」条件。

**Pitfall — 开放态 session 直接 SQL 删会被拒**：
`IntegrityError: Refused to delete a session that has gateway runtime history`
是 Hermes 的守卫（认为当前 Hermes 版本比写入该库的版本旧）。开放态的
必须走 `hermes sessions delete`；ended 态的 SQL 直删通常放行。

**Pitfall — `hermes sessions prune` 有 90 天默认窗口**：任何带过滤条件的
调用都会匹配所有年龄，不带 `--older-than` 时才是 90 天。别以为 prune 只动
老数据。

## 回收磁盘：删行 ≠ 缩文件，必须 VACUUM

SQLite 删行只是把页标成空闲，文件大小不变。实测 14 万条消息的库删到 5 万条后
文件仍是 1.2GB。回收顺序：

```bash
# ① 重建紧凑索引（--no-vacuum 先只做索引；这步可带 gateway 跑）
hermes sessions optimize-storage --no-vacuum --yes --force

# ② VACUUM 归还空页（需要 --force 才能在 gateway 运行时做）
hermes sessions optimize --force
# 输出形如: Database size: 1172.0 MB -> 279.5 MB (reclaimed 892.5 MB)

# ③ 收缩 WAL（VACUUM 后文件仍大，因为 WAL 没收缩）
python3 -c "import sqlite3;c=sqlite3.connect('/home/saber/.hermes/state.db');print(c.execute('pragma wal_checkpoint(TRUNCATE)').fetchone())"

# ④ 验证
du -sh ~/.hermes/state.db
python3 -c "import sqlite3;c=sqlite3.connect('/home/saber/.hermes/state.db');print(c.execute('pragma integrity_check').fetchone()[0])"
```

**Pitfall — `--force` 覆盖 live-writer 保护是有代价的**。官方警告是
「rewriting the store under a live writer can leave every agent refusing
turns」。实测 `optimize --force` + 紧随其后的 `wal_checkpoint(TRUNCATE)`
没有造成拒绝，但**必须紧跟 integrity_check 和 /health 验证**，发现异常
立刻从备份恢复。网关正在跑长任务时更要谨慎。

**Pitfall — `system_prompts` 表会堆积人格快照**：每个 session 存一份
system prompt，几十万个 session 就是几百 MB（实测 172MB / 2161 份）。
裁剪会话后要单独清：

```bash
sqlite3 ~/.hermes/state.db "
select count(*) from system_prompts;
-- 只保留仍被存活 session 引用的
delete from system_prompts where hash not in (
  select distinct system_prompt_hash from sessions where system_prompt_hash is not null);"
```

## cache/scratch 全量清扫

`~/.hermes/cache/scratch` 会长到数 GB（一次装 PyTorch 就能留下 5.6GB 的
`pip-unpack-*` wheel 解包目录）。**手工 `rm -rf` 太慢**，用 Python 按
「跳过运行中 + 跳过近期修改」规则批量清：

```bash
python3 - <<'EOF'
import os, shutil, time
SCRATCH = os.path.expanduser("~/.hermes/cache/scratch")
now = time.time()
freed = removed = 0
skipped = []
protect_prefixes = ("hermes_kernel_", "hermes-snap-")
RECENT = 1800   # 30 分钟内修改过的跳过
for name in os.listdir(SCRATCH):
    p = os.path.join(SCRATCH, name)
    if name.startswith(protect_prefixes):
        skipped.append((name, "live")); continue
    try:
        st = os.stat(p)
    except OSError:
        continue
    if now - st.st_mtime < RECENT:
        skipped.append((name, "recent")); continue
    try:
        if os.path.isdir(p) and not os.path.islink(p):
            sz = sum(os.path.getsize(os.path.join(r, f))
                     for r, _, fs in os.walk(p) for f in fs
                     if os.path.exists(os.path.join(r, f)))
            shutil.rmtree(p)
        else:
            sz = os.path.getsize(p); os.remove(p)
        freed += sz; removed += 1
    except Exception as e:
        skipped.append((name, f"err:{e}"))
print(f"removed {removed} items, freed {freed/1024/1024:.1f} MB")
print("skipped:", skipped[:10])
EOF
```

**必须保护 `hermes_kernel_*`**：agent 自己的 execute_code kernel 正跑在
`~/.hermes/cache/scratch/hermes_kernel_*/` 里，删掉会当场杀掉当前会话。
`hermes-snap-*.sh` 是 shell 快照脚本，同理。

**Chromium 的 scoped_dir 通常在 `/tmp/` 而不是 scratch**，但要确认：
`ps -eo cmd | grep user-data-dir` 看实际路径，别按目录名猜。

## 删 uv 装的 Python 版本：先确认真的没人用

`~/.local/share/uv/python/` 下每个 cpython 版本占 130-200M。删之前确认两件事：

```bash
# ① Hermes 自己用的是它 venv 里的解释器，不是 uv 装的
ls -d ~/.hermes/hermes-agent/{venv,.venv}/bin/python* 2>/dev/null
~/.hermes/hermes-agent/.venv/bin/python --version

# ② 确认没有项目引用那个版本
grep -rn 'share/uv/python' ~/.hermes/*.yaml ~/.hermes/scripts/ 2>/dev/null
```

**坑：`~/.local/share/uv/python/` 里同时存在真实目录和符号链接**。删掉真实目录后，
剩下的 `cpython-3.10-linux-x86_64-gnu` → `cpython-3.10.20-...` 变成悬空链接，
`shutil.rmtree` 会对它抛 `FileNotFoundError`。删完必须清一遍悬空链接：

```python
import os
base = os.path.expanduser("~/.local/share/uv/python")
for name in os.listdir(base):
    p = os.path.join(base, name)
    if os.path.islink(p):
        if not os.path.exists(os.path.join(base, os.readlink(p))):
            os.unlink(p)
```

**不要删 `~/.local/lib/python3.14/site-packages/`**：那里面是 playwright、pymupdf、
fontTools 等 Hermes 实际调用的库（Hermes 的浏览器工具、PDF 处理、字体）。它与
`~/.hermes/hermes-agent/.venv/` 是两套，删了会让这些功能直接失效。
验证方式：`python3 -c "import pymupdf"`（注意新版本入口是 `pymupdf` 而非 `fitz`，
`fitz` 只是残留子目录）。

## 清理 Chromium 进程：杀进程没用，要重启 service

CDP 浏览器由 systemd user service 管着（`hermes-browser-cdp.service`）。
直接 `kill` 掉子进程会被立即拉起，白费功夫；正确做法是重启 service：

```bash
systemctl --user restart hermes-browser-cdp.service
sleep 3
systemctl --user is-active hermes-browser-cdp.service   # 期望 active
```

**一个浏览器实例有 6+ 个子进程**（主进程 + 2 zygote + gpu + network + renderer）。
看 `ps` 时不要把同一实例的 renderer 当成多个浏览器实例再错杀。
确认有几个实例看 `user-data-dir` 的去重数量：

```bash
ps -eo args | grep -o 'user-data-dir=[^ ]*' | sort | uniq -c
```

## 清理 Python 虚拟环境前：先确定「谁拥有它」

同一台机器上常有多个职责不同的 venv。**删之前必须先查清每个 venv 的使用者**，
因为「看起来没人用」和「真的没人用」在有多个 venv 时极易判断错。

```bash
# 列出所有 venv 及其体积
du -sh ~/.hermes/hermes-agent/venv* ~/.hermes/venv ~/.venvs/* 2>/dev/null | sort -rh

# 逐个查「谁引用它」——scripts、skills、cron 三处都要查
grep -rn "<venv 路径>" ~/.hermes/scripts/ ~/.hermes/skills/ ~/.hermes/cron/jobs.json 2>/dev/null

# 查运行时是否真的在用（python 版本 + 关键包 import）
for v in ~/.hermes/hermes-agent/venv ~/.hermes/hermes-agent/.venv ~/.hermes/venv; do
  [ -x "$v/bin/python" ] && { echo -n "$v: "; "$v/bin/python" -V 2>&1; }
done
```

**判据（三条同时成立才可删）**：① 没有任何 script/skill/cron 引用它的路径；
② 运行中的进程没有加载它的 `site-packages`（`ps`/`/proc/<pid>/maps` 无痕迹）；
③ 它的独有功能已被别的环境覆盖。

**典型陷阱**：某个 venv 里装着「某个包没装成功但依赖装了一半」的残废环境
（如 kokoro 装不上 CUDA 依赖，留下 onnxruntime/numpy/espeakng_loader 占几百 MB）。
这种半成品既不工作也不被引用，是净亏空间——直接删，但要先 `import` 验证
它确实残缺，别凭包名猜。

**替代做法**：不要直接删掉一个被依赖的 venv，而是**建一个新的干净环境接管它的职责**，
再删旧的。典型流程：
1. 用干净解释器建新 venv（`python3 -m venv <新目录>`）
2. 只装职责所需的最小依赖集（`pip install <pkg>`，不带 `-q`，否则失败会被吞掉）
3. **验证新环境能完成真实任务**（真的 import 一次、真的跑一次脚本）
4. 把消费方的路径改成自动探测（探测多个候选 + PATH 兜底），不要写死
5. 旧环境**先改名**（`mv venv venv_old_bak`）保留回滚，确认无误后再删

### 消费方路径不要写死

任何脚本/配置里的 `PYTHON_BIN = "/abs/path/to/venv/bin/python"` 都是定时炸弹：
venv 目录改名或迁移后脚本会**静默失败**（FileNotFoundError 被 catch 吞掉，
或走到 fallback 分支，用户只看到「工具不可用」）。改成探测式：

```python
def _find_venv_bin(name: str) -> str:
    import shutil
    base = Path("/home/saber/.hermes/hermes-agent")
    for candidate in (base/"venv"/"bin"/name, base/"venv_new"/"bin"/name,
                      base/".venv"/"bin"/name):
        if candidate.exists():
            return str(candidate)
    found = shutil.which(name)
    if found:
        return found
    raise FileNotFoundError(f"{name} not found")
```

### pip 装完必清：scratch 里会堆出几个 GB

`TMPDIR` 指向 `~/.hermes/cache/scratch` 时，**pip 把大 wheel 解包到那里**，
装一个带 pandas/onnxruntime 之类依赖的包能留下数 GB 的 `pip-unpack-*` 临时目录，
加上 `~/.cache/pip/http-v2` 的下载缓存，一次安装能吃掉 5-8G。

```bash
# 安装结束后清理（确认没有 pip 在跑）
rm -rf ~/.cache/pip
rm -rf ~/.hermes/cache/scratch/pip-unpack-* ~/.hermes/cache/scratch/tmp* 2>/dev/null
```

**`pip install -q` 会吞掉失败**：出错时退出码非零但屏幕上一片安静，看起来像装成功了。
**不要用 `-q`**，尤其在后台任务里；装完必须**再验证一次 import**，
不能以「pip 没报错」当作装成功的证据。

**pip 装大依赖要放后台跑**：前台有 300s 上限，装 pandas 级别的依赖会超时并
杀掉整个 kernel。用 `terminal(background=True, notify_on_complete=True)` 起，
期间做别的事，收到完成通知再验证。

**需确认后再删**：

| 目标 | 风险 | 判断方法 |
|------|------|---------|
| `.gradle` | Android/Flutter 构建缓存 | 巨大时确认是否还用 Android/Flutter |
| `.espressif` | ESP-IDF 工具链 | ESP32 项目已清理则可删（~2.5G） |
| `.pub-cache` | Dart/Flutter 包缓存 | Flutter 不再使用则可删 |
| `.idf-venv` | ESP-IDF Python 环境 | esp-idf 删除后无用（~89M） |
| `.agent-reach-venv` | Agent Reach 虚拟环境 | 不再使用则可删（~83M） |
| `~/.cache/yay/` | Arch AUR yay 缓存 | Arch 用户特有，可删（~110M 实测） |
| `.cache/Espressif` | ESP 工具链缓存 | esp-idf 删除后无用（~260M） |
| 项目目录 | xiaoclaw/xiaozhi/esp-idf | ESP32 不再用则全删（~6G） |
| `~/package/` | OpenClaw 源码（root 安装） | 权限不够时 rm 报错"权限不够"——无法删除，只能忽略 |

## OpenClaw 彻底清理（含 npm 全局包 + systemd）

**核心原则：npm uninstall ≠ 彻底卸载。必须同时清理全局已安装包和 systemd。**

```bash
# 1. npm uninstall（清理包）
npm uninstall -g openclaw openclaw-qqbot @tencent-connect/openclaw-qqbot @martian-engineering/lossless-claw 2>&1 | tail -3

# 2. 清理 OpenClaw 主目录（1-2GB，容易漏！）
du -sh ~/.openclaw/ ~/openclaw.log ~/openclaw-*.tgz 2>/dev/null
rm -rf ~/.openclaw ~/openclaw.log ~/openclaw-*.tgz

# 3. 清理 npm 全局 node_modules（仅 uninstall 不够）
du -sh ~/.npm-global/lib/node_modules/openclaw 2>/dev/null
rm -rf ~/.npm-global/lib/node_modules/openclaw \
       ~/.npm-global/lib/node_modules/openclaw-qqbot \
       ~/.npm-global/lib/node_modules/.openclaw-update-stage-* \
       ~/.npm-global/node_modules/.bin/openclaw

# 4. 清理 watchdog 脚本和配置
rm -f ~/.hermes/openclaw-watchdog.sh \
       ~/.hermes/openclaw-watchdog.log \
       ~/.config/fix-openclaw-config.sh

# 5. 清理 hermes_workspace 里的 openclaw 残留
rm -rf ~/hermes_workspace/openclaw-portable \
       ~/hermes_workspace/downloads/oc

# 6. 清理 systemd user service（关键！）
systemctl --user stop openclaw 2>/dev/null
systemctl --user disable openclaw 2>/dev/null
rm -f ~/.config/systemd/user/openclaw.service
rm -rf ~/.config/systemd/user/openclaw.service.d
systemctl --user daemon-reload

# 7. 验证：确认 not-found（unit文件不存在=干净）
systemctl --user list-units --type=service 2>/dev/null | grep openclaw
# 期望输出: "not-found" 而非 "loaded failed failed"
```

**清理完成后最终验证**：
```bash
ps aux | grep openclaw | grep -v grep          # 期望: 0行
ss -tlnp | grep 18888                          # 期望: 无输出
find ~/.npm-global/lib/node_modules/ -iname "*openclaw*" 2>/dev/null | wc -l  # 期望: 0
systemctl --user list-units --type=service 2>/dev/null | grep openclaw | grep "not-found"  # 期望: 匹配
```

## 项目级完整清理

ESP32/语音AI项目彻底清理（示例：xiaozhi）：
```bash
# 1. 先查 Docker 容器（skill删除后容器往往还在跑！）
docker ps -a --format "table {{.ID}}\t{{.Image}}\t{{.Status}}" | grep -i xiaozhi

# 2. 停止并删除容器
docker stop $(docker ps -a -q --filter "ancestor=*xiaozhi*") 2>/dev/null
docker rm $(docker ps -a -q --filter "ancestor=*xiaozhi*") 2>/dev/null

# 3. 删除镜像（释放磁盘空间）
docker rmi $(docker images -q --filter "reference=*xiaozhi*") 2>/dev/null

# 4. 删除所有未使用的悬空镜像
docker image prune -a -f

# 5. 清理源代码目录
rm -rf /home/saber/xiaoclaw \
       /home/saber/xiaozhi-esp32-server \
       /home/saber/xiaozhi-esp32-server-golang \
       /home/saber/xiaozhi-server \
       /home/saber/py-xiaozhi \
       /home/saber/esp-idf
```

**关键原则：skill/代码删除 ≠ Docker容器停止。检查 `docker ps -a` 是项目清理的第一步。**

## 清理后验证

```bash
df -h /
```
