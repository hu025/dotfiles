---
name: local-rag
description: Build production-grade local RAG pipelines with Ollama, Qdrant/ChromaDB, semantic chunking, and rerankers. Use when designing retrieval-augmented generation systems on Hermes with 100% offline operation, sub-second latency, and citation-grounded answers.
---

# Local RAG 2026 SOTA

## When to use
- Hermes needs grounded answers from local documents (notes, code, PDFs, wikis)
- Privacy/offline requirement: no data leaves the machine
- <50M vectors, single-tenant, consumer hardware (16–32GB RAM)

## Stack (2026 winners)
| Layer | Pick | Runner-up |
|---|---|---|
| LLM | `qwen3:8b` (Apache-2.0, think mode) | `llama3.1:8b` (tool-calling) |
| Embedding | `nomic-embed-text` (768d, Matryoshka) | `bge-m3` (multilingual, hybrid) |
| Vector DB | **Chroma** (≤5M vec, prototype) / **Qdrant** (>5M, prod) | pgvector if Postgres already |
| Chunking | Recursive by structure, 256–512 tok, 50–100 overlap | Semantic splitter for prose |
| Reranker | `bge-reranker-v2-m3` (cross-encoder, +20–35% precision) | `ms-marco-MiniLM-L-6` (light) |

## Architecture
```
docs → chunk(512/64) → embed(nomic) → Chroma/Qdrant
query → embed → retrieve(top_k=8) → rerank(top_5) → prompt(qwen3) → answer+cites
```

## Install (≤90s)
```bash
ollama pull qwen3:8b nomic-embed-text
pip install chromadb langchain-ollama langchain-chroma sentence-transformers
```

## Minimal pipeline
```python
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
docs = DirectoryLoader("~/notes", glob="**/*.md").load()
chunks = splitter.split_documents(docs)

vs = Chroma.from_documents(chunks, OllamaEmbeddings(model="nomic-embed-text"),
                           persist_directory="./chroma_db", collection_name="notes")
retriever = vs.as_retriever(search_kwargs={"k": 8})
llm = ChatOllama(model="qwen3:8b", temperature=0.15)

# Rerank → answer (cite sources)
from sentence_transformers import CrossEncoder
reranker = CrossEncoder("BAAI/bge-reranker-v2-m3")
hits = retriever.invoke(question)
top = reranker.rank(question, [h.page_content for h in hits], top_k=5)
context = "\n\n".join(hits[i].page_content for i, _ in top)
answer = llm.invoke(f"Context:\n{context}\n\nQ: {question}\nA (cite sources):")
```

## Hermes integration
- **MCP tool**: wrap `vs.similarity_search` as `@mcp.tool()` for sub-agent RAG access
- **Skill pipeline**: pair with `qmd` skill — index `~/notes/**/*.md`, expose via Hermes tool
- **Cost**: $0/query, ~3–5s p50 (single retrieval), 8–12s with rewrite-retry (agentic)
- **Storage**: ~200MB per 65k vectors (Chroma in-memory); persist `./chroma_db`

## Pitfalls (learned 2025–2026)
- ❌ In-memory `chromadb.Client()` loses data on restart → always `PersistentClient`
- ❌ Fixed-char splitting → use recursive with overlap, or semantic for prose
- ❌ top_k=20 dumps noise → retrieve 8, rerank to 5
- ❌ Forgetting to pin embedding model version → silent quality drift
- ❌ CPU Ollama + GPU embeddings mismatch on macOS → pin Metal vs CPU per model
- ✅ Test retrieval quality alone (print raw chunks) before blaming the LLM
- ✅ Tag chunks with metadata (source, date, project) for hybrid filtering at scale

## Scaling triggers (Chroma → Qdrant)
- >5M vectors, >100 QPS, complex metadata filters, multi-tenant
- Chroma 0.5+ sharding handles up to ~50M, but Qdrant wins p99 + 4–32× quantization
