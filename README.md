# A detection engineers perspective on how to defend against adversarial ML.

---

## Repository Layout

```
├── CHECKLIST.md              ← Master progress tracker
│
├── rag-app/                  ← Phase 2 & 2.5 — Local LLM lab + threat model target
│   ├── app.py                ← RAG application (LangChain + Chroma)
│   ├── requirements.txt
│   └── docs/                 ← Document corpus for retrieval
│
├── threat-model/             ← Phase 2.5 — STRIDE threat model artifact
│   └── threat-model.md
│
├── eval-harness/             ← Phase 3.5 — Adversarial evaluation harness ★
│   ├── harness.py            ← Main runner
│   ├── prompts/              ← 50+ adversarial prompt sets
│   ├── scorers/              ← Rule-based + LLM-as-judge scoring
│   └── reports/              ← Generated CSV/JSON output
│
├── detection-rules/          ← Phase 4.5 — AI-specific detection rules ★
│   ├── sigma/                ← Sigma YAML rules
│   ├── splunk/               ← Translated SPL queries
│   └── datadog/              ← Datadog log query JSON
│
├── playbooks/                ← Phase 4 — Incident response playbooks
│   └── prompt-injection-ir.md
│
└── blog/                     ← Phase 4 — Blog post drafts and diagrams
    └── threat-model-diagram.md
```

## Quick Start

```bash
# Clone and set up the RAG lab
cd rag-app
pip install -r requirements.txt
python app.py

# Run the adversarial eval harness against your RAG
cd eval-harness
pip install -r requirements.txt
python harness.py --target http://localhost:8000 --output reports/run-$(date +%Y%m%d).json
```
