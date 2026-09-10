---
description: ANP (Agent Network Protocol) — 去中心化Agent通信协议，W3C DID身份层，HTTP of Agentic Web。适合开放互联网Agent互联，与MCP/A2A互补。
trigger: ANP agent network protocol decentralized DID W3C
---
# ANP — Agent Network Protocol

## 核心定位

**ANP = HTTP of the Agentic Web**。目标是让全球数十亿智能Agent能够像Web上的HTTP一样自由互联，无需中心化注册机构。

三层协议架构：
- **身份加密层** — W3C DID去中心化身份
- **元协议协商层** — 自动协议发现与版本协商
- **应用协议层** — Agent描述(ADP)+Agent发现协议

## 与MCP/A2A的关系

| 协议 | 层级 | 解决问题 | 主导方 |
|------|------|----------|--------|
| MCP | 工具访问层 | Agent→工具/数据 (垂直) | Anthropic |
| A2A | Agent协作层 | Agent→Agent企业互联 | Google |
| ANP | 开放网络层 | 开放互联网去中心化互联 | W3C社区 |

**三者互补**。MCP+A2A是主流企业架构，ANP面向开放去中心化场景。

## 核心技术栈

### W3C DID去中心化身份
- **did:wba** (Web-Based Agent) — ANP核心DID方法，基于普通HTTPS/DNS
- 无需区块链，继承成熟Web基础设施
- DID文档托管于标准HTTP GET路径
- 方案：`did:wba:example.com:user:alice` → `https://example.com/user/alice/did.json`

### DID身份认证流程
```
1. Agent在HTTP头附带DID+签名
2. 接收方通过DID文档解析公钥
3. 单次请求完成身份认证+权限验证
4. 可返回token，后续请求复用
```

### End-to-End加密通信
- ECDHE (Elliptic Curve Diffie-Hellman Ephemeral)
- 中间节点无法解密
- 支持Agent反向代理场景（托管在第三方平台的Agent）

## SDK生态

| 语言 | 包名 | 版本 | 安装 |
|------|------|------|------|
| Python | `anp` | 0.9.3 | `pip install "anp[api]"` |
| Rust | `anp` | 0.9.3 | `cargo add anp` |
| Go | `anp/golang` | 0.9.3 | `go get ...` |
| TypeScript | `@agent-network-protocol/anp` | 0.9.3 | npm |
| Dart | `anp` | 0.8.7 | `dart pub add anp` |
| Java | anp4j (预览) | — | Maven build |

## 快速开始 (Python)

```python
# 1. 安装
pip install "anp[api]"

# 2. 创建DID身份
from anp import OpenANP

app = FastANP(name="MyAgent", description="...")

# 3. 注册接口方法
@app.agent_method()
def search(query: str) -> dict:
    return {"results": [...]}

# 自动生成：
# GET  /agent/ad.json        — Agent描述文档
# GET  /agent/interface.json — OpenRPC接口
# POST /agent/rpc            — JSON-RPC调用端点
```

## 适用场景

- **开放Agent市场**：任何Agent可被发现和调用，无需预建信任
- **跨组织协作**：去中心化身份替代API Key管理
- **主权Agent网络**：不依赖单一厂商协议
- **W3C标准生态**：与Verifiable Credentials、JSON-LD无缝集成

## 局限性

- **成熟度较低**：346 stars，生态远小于MCP/A2A
- **企业采纳有限**：主要是W3C社区推动
- **无中心发现服务**：需要自己实现发现机制
- **与现有Hermes架构互补非替代**

## 链接

- 官网: https://agentnetworkprotocol.com/
- GitHub: https://github.com/agent-network-protocol/anp
- _stars: 346 (2026-09)
- License: MIT
