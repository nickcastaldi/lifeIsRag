# AI Security Engineer — Career Roadmap

A structured 12–18 month plan to land an AI Security Engineer role. This repo is the operational home for every artifact the checklist calls for — the RAG lab, eval harness, detection rules, IR playbook, and threat model all live here.

**Role focus:** Defender / builder. You design and ship controls, detection logic, evaluation harnesses, and guardrails for AI systems. Red-team practice in this plan exists to sharpen your defenses, not to position you as an offensive specialist.

**Estimated effort:** ~340 hours alongside a day job  
**Estimated cost:** ~€400  
**Last updated:** May 2026 (v4)

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

★ = highest-signal artifacts for interviews and job applications

---

## Phases at a Glance

| Phase | Focus | Weeks | Hours |
|-------|-------|-------|-------|
| 0 | Land London role first | 0–6 months | — |
| 1 | Foundation reading | 1–4 | ~36 |
| 2 | Local LLM lab (RAG app) | 5–7 | ~15 |
| 2.5 | Threat model your RAG app | 8 | ~6 |
| 3 | Hands-on attack & defense | 9–14 | ~46 |
| 3.5 | Adversarial evaluation harness | 15–16 | ~12 |
| 4 | Public artifacts (blog, playbook) | 17–21 | ~30 |
| 4.5 | Detection engineering for AI | 22–24 | ~18 |
| 5 | AWS Security Specialty | 25–40 | ~150 |
| 6 | ML platform & container familiarity | 33–40 | ~32 |
| 7 | Job application operations | 36–52 | ongoing |
| 8 | Interview preparation | Week 30+ | ongoing |

---

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

---

## Success Markers (Month 12)

- [ ] Working local LLM lab built and broken
- [ ] Threat model artifact (markdown in this repo)
- [ ] Published blog post
- [ ] AI incident response playbook
- [ ] Adversarial evaluation harness repo (public, README, CI)
- [ ] AI detection rules repo (Sigma + Splunk SPL + Datadog, public)
- [ ] AWS Security Specialty certification
- [ ] Hands-on familiarity with SageMaker + MLflow + Kubeflow + Bedrock Guardrails
- [ ] 25+ active applications submitted

---

## Key Tools by Phase

**Phase 3 — Attack practice:** Garak, PyRIT, Promptfoo, Rebuff, Lakera Gandalf  
**Phase 3 — AppSec:** Semgrep, Bandit, OWASP ZAP, gitleaks, pip-audit  
**Phase 3 — Supply chain:** Syft, Grype, Trivy, ModelScan  
**Phase 4.5 — Detection:** Sigma, Splunk SPL, Datadog  
**Phase 5 — Cloud:** AWS Security Specialty (IAM, KMS, GuardDuty, Bedrock Guardrails)
