# RAG Security Lab — Phase 2 Artifact

A minimal RAG application built as the attack surface for Phases 2.5, 3, and 3.5 of the AI Security Engineer checklist.

## Setup

```bash
# 1. Install Ollama and pull models
ollama pull llama3.1
ollama pull nomic-embed-text

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Ingest sample documents
curl -s -X POST http://localhost:8000/ingest -H "Content-Type: application/json" \
  -d '{"path": "docs/"}'

# 4. Query
curl -s -X POST http://localhost:8000/query -H "Content-Type: application/json" \
  -d '{"question": "What is the data classification policy?"}'
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/query` | Ask a question; returns answer + source files |
| POST | `/ingest` | Load documents from a directory into Chroma |
| GET | `/health` | Liveness check |

## Attack Surface (Phase 2.5 target)

| Boundary | Threat vectors |
|----------|---------------|
| User → `/query` | Direct prompt injection, jailbreak strings, DAN-style attacks |
| `docs/` → ingestion | Indirect prompt injection via poisoned documents |
| Retriever → LLM | Retrieval poisoning, citation laundering |
| LLM → response | System prompt leakage, output exfiltration |
| `/ingest` endpoint | Path traversal, SSRF if path is user-controlled |

Add your own documents to `docs/` and re-ingest. The eval harness in `../eval-harness/` targets this app's `/query` endpoint.
