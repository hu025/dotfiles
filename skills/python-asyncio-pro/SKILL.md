---
name: python-asyncio-pro
description: Python asyncio 2026 最佳实践。触发词：asyncio/async/并发/事件循环/TaskGroup/uvloop。
created: 2026-09-16
category: software-development
tags: [python, asyncio, async, concurrency, performance]
---

# Python asyncio Pro — 2026 Best Practices

## 核心原则

### 永远用 `asyncio.run()` 而非手动事件循环
```python
# ✅ 现代（Python 3.7+）
asyncio.run(main())

# ❌ 过时
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

### 永远用 `asyncio.sleep()` 而非 `time.sleep()`
```python
async def waiter(secs):
    await asyncio.sleep(secs)  # ✅ 非阻塞
    # time.sleep(secs)          # ❌ 阻塞整个事件循环
```

---

## TaskGroup 结构化并发（Python 3.11+）

`TaskGroup` 是 `asyncio.gather()` 的结构化替代，提供：
- 任务归属（owned by group）
- 首个异常自动取消所有 sibling 任务
- 错误以 `ExceptionGroup` 统一传播

```python
import asyncio

async def fetch_data(n):
    await asyncio.sleep(0.1 * n)
    if n == 2:
        raise ValueError(f"Task {n} failed")
    return f"data-{n}"

async def main():
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(fetch_data(1))
        t2 = tg.create_task(fetch_data(2))
        t3 = tg.create_task(fetch_data(3))
    # 任意任务失败 → 所有 sibling 被取消
    # 用 except* 捕获 ExceptionGroup
```

### 捕获 ExceptionGroup
```python
async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(coro_a())
            tg.create_task(coro_b())
    except* ValueError as eg:
        for e in eg.exceptions:
            print(f"Caught: {e}")
    except* TimeoutError as eg:
        print("Timeout group")
```

### 动态任务创建
```python
async with asyncio.TaskGroup() as tg:
    for item in items:
        tg.create_task(process(item))  # 动态追加安全
```

### TaskGroup vs gather()
| 场景 | 推荐 |
|------|------|
| 简单并行无失败处理 | `gather()` 可接受 |
| 生产级并发/需容错 | **TaskGroup** |
| 需统一取消传播 | **TaskGroup** |
| 需 ExceptionGroup | **TaskGroup** |

---

## 事件循环替代方案

### uvloop — 2-4x 性能提升
```python
# uvloop 0.18+ 推荐方式
import uvloop
uvloop.run(main())  # 替代 asyncio.run()
```

**性能对比（Python 3.13，10k WebSocket 连接）：**
- uvloop 0.19: **823,000 msg/sec**，p99 **12ms**
- asyncio 原生: **387,000 msg/sec**，p99 **19ms**
- 吞吐量差距: **2.1x**

**uvloop.run() 替代 asyncio.run()：**
```python
import asyncio
import uvloop

async def main():
    ...

if __name__ == "__main__":
    uvloop.run(main())  # 自动设置 uvloop 为默认事件循环
```

**Python 3.11 及更早版本：**
```python
import asyncio
import uvloop

async def main():
    ...

# Python 3.11+ 用 Runner
if sys.version_info >= (3, 11):
    with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
        runner.run(main())
else:
    uvloop.install()
    asyncio.run(main())
```

### rsloop — Rust 实现，比 uvloop 更快的 2026 新选择
PyO3/Rust 实现，使用 `io_uring`（Linux 6.1+）。

**性能基准（macOS arm64 / CPython 3.14）：**
| 指标 | rsloop | uvloop | asyncio |
|------|--------|--------|---------|
| callbacks 200k ops | 6.0M/s | 4.9M/s | 2.4M/s |
| tasks 50k ops | 786k/s | 718k/s | 462k/s |
| TCP streams 5k ops | 55k/s | 37k/s | 16k/s |
| TLS HTTP 吞吐量 | 72,530/s | 36,772/s | — |
| Bulk transfer | 4.99 GiB/s | 2.82 GiB/s | — |

**使用方式：**
```python
import asyncio
import rsloop

async def main():
    loop = rsloop.Loop()  # Rust 实现的事件循环
    async with asyncio.Runner(loop_factory=lambda: loop) as runner:
        await runner.run(main())
```

**rsloop vs uvloop 关键差异：**
- TLS 处理：rsloop +97% 优势
- WebSocket 原始性能：基本持平
- 平台要求：Linux 6.1+ / macOS 13+ / Windows 11+
- Free-threaded CPython：暂不支持

---

## 生产级 HTTP 客户端

| 库 | 特点 | 适用场景 |
|----|------|----------|
| **httpx** | async + sync，支持 HTTP/2 | 现代异步 API 客户端 |
| **aiohttp** | 专为 asyncio 设计，WebSocket | 高并发爬虫/服务 |
| **fetch (experimental)** | Python 3.13 内置 | 简单 async HTTP |

```python
import httpx

async with httpx.AsyncClient() as client:
    r = await client.get("https://api.example.com/data")
    print(r.json())
```

---

## 性能调优（生产部署）

### 1. 禁用调试模式
```python
# 生产必须禁用，debug 模式增加 30% 开销
asyncio.run(main(), debug=False)
```

### 2. 增大文件描述符限制（Linux）
```bash
ulimit -n 65536
```
10k+ 连接必须调整，默认 1024 不够用。

### 3. TCP_NODELAY
```python
# WebSocket 服务器连接建立时设置
transport.get_extra_info('socket').setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
```

### 4. 消息批量发送
```python
async def broadcast_batch(room, messages, batch_size=10):
    batches = [messages[i:i+batch_size] for i in range(0, len(messages), batch_size)]
    for batch in batches:
        payload = b'|'.join(batch)
        for client in room.clients:
            client.send(payload)
```
批量发送减少系统调用 10-20x，uvloop 吞吐量从 823k → 1.1M msg/sec。

### 5. Python 3.13 自适应解释器
```bash
# 启用 asyncio 优化（默认已启用）
PYTHONADAPTIVEOFF=0
```
减少事件循环开销 14%（vs Python 3.12）。

---

## 取消作用域（Cancel Scopes）

### asyncbis — 研究中的结构化取消
`asyncbis` 项目（[github.com/agronholm/asyncbis](https://github.com/agronholm/asyncbis)）探索 level cancellation vs edge cancellation，在 Rust `rsloop` 之上构建，可能成为未来 asyncio 替代实现。

```python
# asyncbis 概念
async with CancelScope() as scope:
    scope.cancel()  # 所有 yield point 抛出 CancelledError
```

### asyncio 原生取消
```python
task = asyncio.create_task(coro())
task.cancel()  # 请求取消
await task      # 等待 CancelledError 传播

# 防护取消
result = await asyncio.shield(some_coroutine())
```

### asyncio.Timeout（Python 3.11+）
```python
async def main():
    try:
        async with asyncio.timeout(5):  # 5秒超时
            await long_running()
    except asyncio.TimeoutError:
        print("Timed out")
```

---

## 陷阱与避免

| 陷阱 | 错误代码 | 正确代码 |
|------|----------|----------|
| 阻塞 sleep | `time.sleep(1)` | `await asyncio.sleep(1)` |
| 手动事件循环 | `loop.run_until_complete()` | `asyncio.run()` |
| gather 异常丢失 | `gather(*tasks)` 无 try | `gather(*tasks, return_exceptions=True)` |
| 丢失 Task 引用 | `create_task()` 无变量 | 保存 `task = create_task()` |
| 文件描述符耗尽 | 10k 连接未调 ulimit | `ulimit -n 65536` |

---

## 工具链

```bash
# 安装
pip install uvloop httpx aiohttp pytest-asyncio

# uvloop 基准测试
uv run --with uvloop python benchmarks/compare_event_loops.py

# rsloop 基准测试（需 Rust 构建）
uv run --with maturin maturin develop --release
uv run --with uvloop python benchmarks/compare_event_loops.py

# 测试
pytest tests/ -v
pytest tests/ -v --asyncio-mode=auto
```

---

## 来源

- [rsloop v0.1.40 — PyPI](https://pypi.org/project/rsloop/)
- [rsloop GitHub — RustedBytes](https://github.com/RustedBytes/rsloop)
- [uvloop GitHub — MagicStack](https://github.com/MagicStack/uvloop)
- [Python asyncio docs 3.14](https://docs.python.org/3/library/asyncio-task.html)
- [Benchmark: Python 3.13 asyncio vs uvloop 0.19](https://johal.in/benchmarking-python-313-asyncio-vs-uvloop-019-websocket) — johal.in 2026-05-03
- [Cubed: Best Python Async Tools 2026](https://blog.cubed.run/)
- [asyncbis research project](https://github.com/agronholm/asyncbis)
