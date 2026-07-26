# OWASP RAG — Air-Gapped AI Security Assistant

A fully local Retrieval-Augmented Generation pipeline over the OWASP corpus.  
Hybrid retrieval (BM25 + FAISS) with cross-encoder reranking, powered by Llama 3.2 via Ollama.  
**No third-party API calls** — designed for regulated and sensitive environments.

---

## Why this exists

OWASP publishes thousands of pages of security guidance across 29 repositories — the Top 10s, ASVS, the Web Security Testing Guide, 100+ Cheat Sheets, the LLM Top 10, and the AI Security & Privacy Guide. Finding the right answer is painful: a general LLM hallucinates, and a cloud RAG service ships your queries off-premises, which is a non-starter for security teams handling sensitive findings.

This project demonstrates a security knowledge assistant that:
- Runs **entirely on local hardware** (no API keys, no external calls)
- Uses **production retrieval patterns** (hybrid search, RRF, cross-encoder reranking)
- Indexes the **full OWASP corpus** including AI/LLM security guidance
- Cites sources for every answer

---

## Architecture

| Component | Technology |
|-----------|-----------|
| Embeddings | `BAAI/bge-small-en-v1.5` (local, 130 MB, runs on Metal/MPS on Apple Silicon) |
| Vector store | FAISS (CPU — no Metal/GPU backend exists for FAISS) |
| Keyword search | BM25 (`rank-bm25`) |
| Rank fusion | Reciprocal Rank Fusion (k=60) |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` (Metal/MPS on Apple Silicon) |
| LLM | Llama 3.2 3B via Ollama |
| Orchestration | LangChain 0.3 |

---

## What's indexed

29 OWASP repositories (see `scripts/cloneOwaspDocs.sh` for the full list), covering:

- **Web app security** — Top 10, WSTG, ASVS, CheatSheetSeries
- **API security** — API Security Top 10
- **AI/ML/LLM security** — LLM Top 10, AISVS, LLM Security Verification Standard, MLSecOps Verification Standard, AI Security & Privacy Guide, ML Security Top 10, AI Testing Guide, LLM Prompt Hacking, Data Security Top 10, GenAI Agent Security Initiative, GenAI Data Security Initiative, GenAI Red Team Lab
- **Cloud-native** — Cloud-Native Top 10, Kubernetes Top 10, CI/CD Top 10
- **Reference & process** — DevGuide, Secure Coding Practices, Code Review Guide, Proactive Controls, Threat Modeling Playbook, www-community wiki
- **Specialized** — Mobile Top 10

Only English, substantive content is indexed — `scripts/filter_markdown.py` strips translations and repo boilerplate (CONTRIBUTING.md, LICENSE.md, issue templates, etc.) from the raw clones before anything reaches `docs/`. One repo (GenAI Top 10 Governance) currently contributes no content since its source is LaTeX/PDF rather than markdown.

---

## Quick start

### Prerequisites

- macOS (Apple Silicon — embeddings and reranking use Metal/MPS automatically)
  or Linux/WSL2
- Python 3.10+
- ~10 GB free disk space
- 8 GB+ RAM (16 GB recommended)

### Setup

```bash
# 1. Clone this repo
git clone https://github.com/nickcastaldi/lifeIsRag.git
cd lifeIsRag/rag-app

# 2. Clone the OWASP source documents
bash scripts/cloneOwaspDocs.sh

# 3. Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Install and start Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2:3b
ollama serve &

# 5. Build the index (one-time; minutes on Apple Silicon GPU, ~15-30 min on CPU)
python src/buildIndex.py

# 6. Start querying
python src/query.py
```

---

## Example queries

- `What is OWASP Top 10 A03:2021?`
- `How do I prevent prompt injection in LLM applications?`
- `Compare broken access control with broken authentication.`
- `What does ASVS Level 2 require for password storage?`
- `How should I threat model an AI agent?`

---

## Design decisions

**Why hybrid retrieval?**  
BM25 excels at exact terms (CWE-89, A03:2021, XSS). FAISS excels at semantic matches. Either alone leaves blind spots; combined via RRF, they cover both axes.

**Why two-stage retrieval (retrieve + rerank)?**  
Bi-encoder retrieval is fast but coarse. Cross-encoder reranking is slow but precise. Running cross-encoder over 8,000 chunks would take 7 minutes; running it over 20 takes 1 second. Standard "cheap recall, expensive precision" pattern.

**Why fully local?**  
Security teams reviewing findings shouldn't ship queries to external APIs. This demonstrates AI tooling that respects data residency, privacy, and supply chain constraints — directly relevant to defense, finance, and regulated industries.

**Why Llama 3.2 3B specifically?**  
Runs on commodity laptop hardware with no GPU. Larger models would be slightly more accurate but unusable on low-resource environments. Demonstrates the cost-quality trade-off explicitly.

**Why does `import faiss` come first in `buildIndex.py`/`owaspRag.py`?**  
On macOS, if PyTorch touches the Metal (MPS) backend before `faiss`'s native library is loaded, an actual FAISS similarity search segfaults the process — a native OpenMP/library init conflict, not a Python exception. Importing `faiss` before any `torch`/`transformers` import avoids it. Don't reorder those imports.

---

## Project structure

```
rag-app/
├── docs/              # OWASP corpus — fetched by scripts/cloneOwaspDocs.sh (gitignored)
├── owasp_index/       # Built FAISS + BM25 index — generated by src/buildIndex.py (gitignored)
├── venv/              # Python virtual environment (gitignored)
├── requirements.txt
├── scripts/
│   ├── cloneOwaspDocs.sh   # Fetches the OWASP repos, markdown-only, into docs/
│   └── filter_markdown.py # Drops translations/boilerplate, keeps English content
└── src/
    ├── deviceUtils.py  # Picks MPS (Apple Silicon) > CUDA > CPU
    ├── buildIndex.py   # Chunks docs/, builds the FAISS + BM25 indexes
    ├── owaspRag.py     # Hybrid retrieval, RRF, rerank, LLM answer generation
    └── query.py        # Interactive CLI
```

---

## What I'd change for production

- Replace FAISS flat index with HNSW for sub-linear search at scale
- Add semantic caching layer for repeated queries
- Streaming output from Llama (Ollama supports it)
- Structured logging with retrieval quality metrics
- Query-level rate limiting and prompt injection guardrails
- Auto-refresh of OWASP corpus on a cron schedule

---

## License

MIT

---

## About

Built by [Nicholas Castaldi](https://github.com/nickcastaldi) as part of an AI Security Engineering portfolio.
