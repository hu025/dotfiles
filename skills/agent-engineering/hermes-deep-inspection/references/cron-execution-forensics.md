# Cron 执行取证手册

自检时需要回答的具体问题：某个 job 是否还在跑？失败原因是什么？
哪些 job 在白烧 token？这个文件给出完整的取证命令与判据。

---

## 数据库 schema

`~/.hermes/cron/executions.db` → 表 `executions`

| 列 | 说明 |
|---|---|
| `id` | 执行记录主键 |
| `job_id` | **对应 jobs.json 的 job id**（不是 name！） |
| `status` | `claimed` / `running` / `completed` / `failed` / `unknown` |
| `claimed_at` | ISO8601 带时区，如 `2026-10-23T12:00:49.895285+08:00` |
| `started_at` / `finished_at` | 可能为 NULL |
| `error` | 失败原因全文 |
| `delivery_outcome` | 投递结果 |
| `scheduled_instant` | 计划触发时刻，用于去重 |

`~/.hermes/cron/jobs.json` → 每个 job 含 `id` / `name` / `schedule` / `enabled` /
`payload.script` / `no_agent` / `failure_streak` / `next_run_at`。

---

## 幽灵 job：定义没了，执行记录还在

**`executions.db` 永久累积**，删 job 只影响 `jobs.json`，历史执行记录不会消失。
所以「executions.db 里有、jobs.json 里没有」是**常态**，不等于它还在跑。

**判据：最后执行时间。** 仍在持续产生新记录 = 真幽灵；停在几天前 = 历史残留。

### 一步到位：近 N 天聚合 + 错误分类

```python
import json,sqlite3,os,collections
jobs=json.load(open(os.path.expanduser('~/.hermes/cron/jobs.json')))
if isinstance(jobs,dict): jobs=jobs.get('jobs',jobs)
if isinstance(jobs,dict): jobs=list(jobs.values())
name={j.get('id'):j.get('name') for j in jobs}
db=sqlite3.connect(os.path.expanduser('~/.hermes/cron/executions.db'))
cnt=collections.Counter(); errs=collections.Counter()
for jid,st,ca,err in db.execute(
    "select job_id,status,claimed_at,error from executions where claimed_at > '2026-10-21'"):
    cnt[(name.get(jid,jid),st)]+=1
    if st!='completed' and err: errs[(name.get(jid,jid),str(err)[:130])]+=1
for k,v in sorted(cnt.items()): print(f"{k[0]:<22}{k[1]:<11}{v}")
print('--- err samples ---')
for k,v in list(errs.items())[:15]: print(v,'|',k[0],'|',k[1])
```

`jobs.json` 的顶层可能是 list、`{'jobs': [...]}` 或 `{id: {...}}` 三种形态之一，
上面的代码三种都兼容——**不要假设结构不变**，cron 组件升级过多次。

### 查出幽灵 job 当年是什么

`state-snapshots/` 里有历次升级前的 jobs.json 快照：

```bash
ls ~/.hermes/state-snapshots/
python3 - <<'EOF'
import json,glob,os
for f in sorted(glob.glob(os.path.expanduser('~/.hermes/state-snapshots/*/cron/jobs.json'))):
    d=json.load(open(f))
    jobs = d if isinstance(d,list) else d.get('jobs',d)
    if isinstance(jobs,dict): jobs=list(jobs.values())
    for j in jobs:
        if j.get('id')=='要查的ID':
            print(os.path.basename(os.path.dirname(os.path.dirname(f))),
                  j.get('name'), '| enabled=', j.get('enabled'))
EOF
```

快照目录命名格式：`YYYYMMDD-HHMMSS-pre-update/`。

---

## 错误分类速查

| 错误特征 | 含义 | 是否故障 |
|---|---|---|
| `GatewayUnavailableError: Gateway incompatible: runtime_protocol` | 升级期间旧 gateway 进程占用 profile，job 抢不到运行时 | 升级期正常现象，重启后自愈 |
| `HTTP 429: 已达到 Token Plan 用量上限 ... (2056)` | MiniMax 配额耗尽 | 配额问题，非代码 bug；额度会按周期刷新 |
| `RuntimeError: Cron job 'X' lost its durable fire claim ownership` | fire claim 被抢占/失效 | 偶发，重跑一般自愈 |
| `Script exited with code 1` + traceback | 脚本自身报错 | 真故障，看 traceback |
| `no such column: job_name` | 用了不存在的列名 | **探针写错**，列名是 `job_id` |

**`base_resp.status_code == 2056` 是 MiniMax 配额耗尽的标志**，
HTTP 仍然是 200，只看状态码会把耗尽误判成成功。

---

## 升级期失败的时间分布

同一 job 的历史失败可能集中在某几天——那通常是升级窗口，不是持续故障。
**判断「现在是否坏了」必须按日期收窄**，不要把历史错误和当前状态混在一起：

```bash
sqlite3 ~/.hermes/cron/executions.db \
  "select job_id,claimed_at from executions where error like '%Token Plan%' order by claimed_at;"
```

看到大量记录集中在一两个月前 → 旧账，当前无碍。

---

## 版本检测类 job 的双份定义

历史上存在两代「版本检测」job：

- **LLM 版**：prompt 式任务，每次运行烧 token，且 prompt 里硬编码的版本号
  （如 `v2026.4.30`）会过期。**纯查询任务必须用 `no_agent: true` 的脚本版**
- **脚本版**：`~/.hermes/scripts/version_check.py`，零 token

检查是否有两代并存：

```bash
python3 -c "
import json,os
d=json.load(open(os.path.expanduser('~/.hermes/cron/jobs.json')))
jobs = d if isinstance(d,list) else d.get('jobs',d)
if isinstance(jobs,dict): jobs=list(jobs.values())
for j in jobs:
    nm=(j.get('name') or '')
    if '版本' in nm or 'version' in nm.lower():
        print(j.get('id'), '|', nm, '| script=', (j.get('payload') or {}).get('script'), '| no_agent=', j.get('no_agent'))
"
```
