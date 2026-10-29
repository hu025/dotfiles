# 语义记忆 trust_score 根因修复与 SQL 校准

## 根因

`plugins/memory/holographic/store.py` 的 `add_fact()` 方法**不接受** `trust_score` 参数，始终用 `self.default_trust = 0.5` 写入数据库，导致所有新 fact 初始 trust_score 全为 0.5。

```python
# store.py add_fact() — 第142行
def add_fact(self, content, entity_type=None, category=None, tags=None, ...):
    ...
    cur.execute(
        "INSERT INTO facts (...) VALUES (...)",
        (content, entity_type, category, tags, self.default_trust, now)  # ← 硬编码 0.5
    )
```

## 修复路径（两条并行）

### 1. 代码 patch（永久）

`plugins/memory/multilayer/provider.py` 的 `_handle_semantic()` 在 `add_fact()` 后追加 `update_fact()` 同步 trust_score：

```python
# provider.py _handle_semantic() — 第505-509行区域
fid = self.store.add_fact(...)  # 写入 default_trust=0.5
if trust is not None:
    self.store.update_fact(fid, trust_score=trust)  # 立即覆盖为正确值
```

验证语法：`cd /home/saber/.hermes/hermes-agent && python3 -c "import ast; ast.parse(open('plugins/memory/multilayer/provider.py').read()); print('lint OK')"`

**需 gateway 重启生效**（重启后新 fact 自动正确，旧 fact 仍需 SQL 修复）。

### 2. SQL 校准（立即生效，无需重启）

```python
import sqlite3
conn = sqlite3.connect('/home/saber/.hermes/memory/semantic.db')

trusts = {
    9: 0.95,   # finance
    10: 0.98,  # identity
    11: 0.98,  # config
    12: 0.95,  # config
    13: 0.95,  # creative
    14: 0.95,  # config
    15: 0.95,  # config
    16: 0.9,   # tech
}

for fid, trust in trusts.items():
    conn.execute("UPDATE facts SET trust_score = ? WHERE fact_id = ?", (trust, fid))
conn.commit()
print(conn.execute("SELECT fact_id, category, trust_score FROM facts").fetchall())
print(f"avg={conn.execute('SELECT AVG(trust_score) FROM facts').fetchone()[0]}")
conn.close()
```

## 验证

```bash
cd /home/saber/.hermes/hermes-agent
python3 -c "
import sqlite3, sys
conn = sqlite3.connect('/home/saber/.hermes/memory/semantic.db')
stats = conn.execute('SELECT COUNT(*), AVG(trust_score), MIN(trust_score), MAX(trust_score) FROM facts').fetchone()
print(f'facts={stats[0]} avg={stats[1]:.3f} min={stats[2]} max={stats[3]}')
# avg > 0.7 且 max >= 0.9 才算正常
sys.exit(0 if stats[0] > 0 and stats[1] > 0.7 else 1)
"
```

## 背景数据

- `semantic_memory` 工具的 `add` action 最终调用 `HolographicStore.add_fact()`（第142行）
- `default_trust = 0.5` 在 `store.py` 第35行初始化
- 修复后 `avg_trust` 从 0.5 升至 0.95（8条fact）