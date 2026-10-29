# Semantic DB 路径与损坏修复参考

## 实际路径（2026-05-16 实测）

| 项目 | 路径 |
|------|------|
| **实际 DB** | `~/.hermes/memory/semantic.db` |
| 代码注释路径 | `plugins/memory/multilayer/semantic/*.db` （已过时） |

## 损坏症状

调用 `semantic_memory(action='get_stats')` 返回：
```
file is not a database
sqlite3.DatabaseError
```

## 修复步骤

```bash
# 1. 备份损坏文件（带时间戳，避免覆盖之前的备份）
mv ~/.hermes/memory/semantic.db ~/.hermes/memory/semantic.db.corrupted.$(date +%Y%m%d%H%M%S)

# 2. 验证其他记忆层正常（可选）
flash_memory(action='list')
working_memory(action='get_stats')

# 3. Gateway 进程会在后台自动创建新的 semantic.db
#    无需手动创建，重启 gateway 也无需
#    五层记忆中只有这一层需要用户手动触发重建

# 4. 验证修复
python3 -c "
from hermes_tools import terminal
r = terminal('python3 -c \"
from plugins.memory.multilayer.semantic import SemanticMemory
sm = SemanticMemory()
print(sm.get_stats())
\"')
print(r)
"
```

## 预防

代码路径 `plugins/memory/multilayer/semantic.py` 的 `__init__` 中 `db_path` 已被硬编码为 `~/.hermes/memory/semantic.db`。如果未来升级后路径再次变化，搜索 `db_path = os.path.join` 定位。