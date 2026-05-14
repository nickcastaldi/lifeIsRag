# AI Security Engineer — Action Checklist

**Goal:** Land an AI Security Engineer role within 12–18 months.  
**Estimated effort:** ~340 hours alongside day job.  
**Estimated cost:** ~€400.  
**Role focus:** Defender / builder. You design and ship controls, detection logic, evaluation harnesses, and guardrails for AI systems. Red-team practice exists to inform your defenses, not to position you as an offensive specialist.

---

## Phase 0: Land London Role First (Months 0–6)

- [x] Apply to current London targets in parallel — don't pause AI security prep waiting for a London move.
- [x] Use existing CV (or the role-tailored variants already produced) — don't optimize for AI security yet.
- [ ] Land role and settle in before adding new commitments.

---

## Phase 1: Foundation Reading (Weeks 1–4, ~36 hours)

### AI-specific

- [ ] OWASP LLM Top 10 (current version) — cover to cover
- [ ] OWASP Top 10 for LLM Applications (latest) — overlapping but more app-focused
- [ ] MITRE ATLAS — overview + 5 case studies
- [ ] Simon Willison's blog — every post tagged "prompt injection"
- [ ] OWASP Machine Learning Security Top 10 (skim level)
- [ ] NIST AI Risk Management Framework + Generative AI Profile

### Agentic AI security *(new)*

- [ ] OWASP Agentic Security Initiative materials (latest)
- [ ] Read 3+ published agent attack write-ups: tool-use escalation, planner manipulation, multi-turn jailbreaks
- [ ] MCP protocol overview — what tools, what trust boundaries, what auth model
- [ ] One MCP exploitation write-up (Embrace the Red blog or equivalent)
- [ ] Anthropic + OpenAI public agent safety / red team posts

### Application security & APIs

- [ ] OWASP API Security Top 10 (latest)
- [ ] PortSwigger auth modules (OAuth 2.0, JWT pitfalls)

### Adversarial ML

- [ ] NIST AI 100-2 "Adversarial Machine Learning" taxonomy paper
- [ ] One survey paper on membership inference attacks (Shokri et al. 2017)
- [ ] One survey paper on model inversion (Fredrikson et al. 2015)
- [ ] OWASP ML Top 10 case studies for evasion + extraction

### Supply chain & SBOM

- [ ] CISA "Securing the Software Supply Chain" overview
- [ ] SPDX vs CycloneDX overview
- [ ] One real-world supply chain incident write-up (XZ, SolarWinds, or PyPI typosquatting)
- [ ] One ML-specific supply chain incident (malicious HF model, pickle deserialization)

### Compliance — depth on EU AI Act *(updated)*

- [ ] EU AI Act in detail (NOT skim): high-risk system requirements, conformity assessments, technical documentation obligations, August 2 2026 enforcement deadline, penalties up to 7% of global revenue
- [ ] ISO 42001 (AI management systems) overview
- [ ] NIST AI RMF crosswalk to ISO 42001 and EU AI Act
- [ ] SOC 2 Trust Services Criteria (skim)
- [ ] ISO 27001 Annex A controls (skim)

---

## Phase 2: Local LLM Lab (Weeks 5–7, ~15 hours)

> **Artifact location:** `rag-app/`

- [ ] Install Ollama locally
- [ ] Pull a model (Llama 3.1 or Mistral)
- [ ] Build a basic RAG application with LangChain → see `rag-app/app.py`
- [ ] Add a vector database (Chroma or FAISS)
- [ ] Have it read from a folder of documents → see `rag-app/docs/`
- [ ] Stretch: wire up one tool call so you have a minimal agent to attack

---

## Phase 2.5: Threat Model Your RAG App (Week 8, ~6 hours)

> **Artifact location:** `threat-model/threat-model.md`

- [ ] Diagram trust boundaries: user → API → retriever → vector store → LLM → tool → response
- [ ] Apply STRIDE per boundary
- [ ] Enumerate AI threats: direct + indirect prompt injection, training/index poisoning, retrieval poisoning, citation laundering, embedding inversion, membership inference, tool misuse, planner manipulation, system prompt leakage, output exfiltration, model DoS
- [ ] Prioritize by impact × likelihood; document top 5
- [ ] Save threat model as markdown artifact → `threat-model/threat-model.md`

---

## Phase 3: Hands-On Practice — Attack & Defense (Weeks 9–14, ~46 hours)

### Track A: AI red team practice (to inform defenses)

- [ ] Lakera Gandalf — all main levels
- [ ] HackAPrompt 2.0 challenges
- [ ] Direct prompt injection on your local RAG
- [ ] Indirect prompt injection (inject via documents)
- [ ] Tool/agent abuse on your local agent
- [ ] Build at least one defensive guardrail you tested
- [ ] Document which Phase 2.5 threats your testing confirmed, missed, or invalidated

### Track A+: Modern AI red team tooling *(new)*

- [ ] Run Garak (NVIDIA) against your local RAG — full vuln scan, document findings
- [ ] Run PyRIT (Microsoft) — at least one orchestrator scenario
- [ ] Run Promptfoo — build a 20-prompt eval set with red-team plugins
- [ ] Try Rebuff (or similar) for prompt injection detection
- [ ] Add tool names to CV under "AI security tooling"

### Track B: AppSec tooling

- [ ] Run Semgrep against your RAG codebase
- [ ] Run Bandit (Python-specific SAST)
- [ ] Run OWASP ZAP in spider/active mode against your running RAG API
- [ ] Run gitleaks against your repo history
- [ ] Run pip-audit or safety for Python dependency scanning
- [ ] Write up: what these tools missed about AI-specific attack surface

### Track C: Software supply chain & SBOM

- [ ] Generate an SBOM using Syft (output as both SPDX and CycloneDX)
- [ ] Scan it with Grype
- [ ] Scan a Hugging Face model directory with Trivy
- [ ] Run ModelScan (Protect AI) on a HF model *(new)*
- [ ] Document one real ML supply chain risk (malicious HF model, dependency confusion, pickle deserialization)

### Track D: Adversarial ML hands-on

- [ ] Run a basic evasion attack on a small image classifier using CleverHans or Foolbox
- [ ] Read through a membership inference attack tutorial (Privacy Meter)
- [ ] Document the difference between attacks on traditional ML vs LLMs

---

## Phase 3.5: Build an Adversarial Evaluation Harness (Weeks 15–16, ~12 hours) *(new)*

> **Artifact location:** `eval-harness/`  
> Modern AI security engineering job descriptions list "adversarial evaluation harness" as an expected deliverable, not a stretch goal. This is one of your most differentiating artifacts.

- [ ] Build a Python harness that runs a fixed prompt set (50+ adversarial prompts) against your RAG → `eval-harness/harness.py`
- [ ] Score responses using rules + LLM-as-judge → `eval-harness/scorers/`
- [ ] Output a CSV/JSON report with severity tagging → `eval-harness/reports/`
- [ ] Support regression mode (run after every code change, fail CI on regressions)
- [ ] Publish as a public GitHub repo with README, sample output, and a demo gif/video
- [ ] Reference it in your blog post and CV under "Open source"

---

## Phase 4: Public Artifacts (Weeks 17–21, ~30 hours)

### Artifact 1: Blog post

> **Artifact location:** `blog/`

- [ ] Title: "Building, Threat Modeling, and Breaking a RAG System: A Security Engineer's Walkthrough"
- [ ] Outline: what I built (Phase 2) → what I was worried about (Phase 2.5 threat model) → what standard AppSec tooling caught and missed (Phase 3 Track B) → what broke under AI-specific testing (Phase 3 Tracks A and A+) → what I added to defend it (guardrails, detection rules) → what I'd do differently in production (SDLC integration)
- [ ] Draft 2,500–4,000 words
- [ ] Include threat model diagram + tool output screenshots + harness output
- [ ] Publish on Medium, Substack, or personal site
- [ ] Cross-post on LinkedIn with brief intro
- [ ] Update CV to include "AI Security writing" with link

### Artifact 2: AI Incident Response playbook

> **Artifact location:** `playbooks/prompt-injection-ir.md`

- [ ] One-page IR playbook for "Suspected prompt injection in production LLM application"
- [ ] Cover: detection signals, triage steps, containment options, eradication, post-incident review
- [ ] Reference your detection rules from Phase 4.5
- [ ] Publish as public Gist or in blog repo

### Artifact 3: Eval harness repo *(new)*

- [ ] See Phase 3.5 — once polished with README and a demo, this counts as a third public artifact and is genuinely rare in the market

---

## Phase 4.5: Detection Engineering for AI (Weeks 22–24, ~18 hours) *(new)*

> **Artifact location:** `detection-rules/`  
> Your strongest differentiator. NATO SOC + Splunk + LLM threat surface is a combination very few candidates have.

- [ ] Catalogue LLM-specific detection signals: input classifiers, output classifiers, canary tokens, semantic anomaly detection, embedding drift, behavioural telemetry (token distribution, latency outliers, tool-call patterns)
- [ ] Write 5+ detection rules in Sigma format covering prompt injection variants → `detection-rules/sigma/`
- [ ] Translate at least 3 to Splunk SPL → `detection-rules/splunk/`
- [ ] Translate at least 2 to Datadog log queries → `detection-rules/datadog/`
- [ ] Publish rules in a public GitHub repo with a README explaining each detection's logic, false-positive expectations, and tuning notes
- [ ] Reference this repo on CV as "AI Detection Rules — open source"
- [ ] Stretch: 2 rules for agent abuse signals (unexpected tool sequences, scope creep, planner divergence)

---

## Phase 5: Cloud Security Depth (Weeks 25–40, ~150 hours)

- [ ] Stéphane Maarek AWS Security Specialty course (Udemy)
- [ ] Tutorials Dojo practice exam set
- [ ] Course content (~20 hours of video)
- [ ] AWS documentation: IAM, KMS, GuardDuty, Security Hub, Macie, CloudTrail, Detective, Bedrock Guardrails *(Bedrock added)*
- [ ] Tutorials Dojo practice exams (target 80%+)
- [ ] Schedule and pass AWS Security Specialty exam
- [ ] Add cert to LinkedIn and CV

---

## Phase 6: ML Platform & Container Familiarity (Weeks 33–40, ~32 hours)

- [ ] Build an end-to-end SageMaker project
- [ ] Understand SageMaker IAM, VPC, KMS for model encryption
- [ ] Read AWS "Security Best Practices for SageMaker"
- [ ] Spin up MLflow locally + run one experiment tracking workflow
- [ ] Spin up Kubeflow locally OR work through Kubeflow security documentation
- [ ] Run through a Hugging Face Transformers tutorial
- [ ] Skim Azure ML and Vertex AI overviews
- [ ] Read CIS Kubernetes Benchmark + one container security intro
- [ ] Read on Kubernetes admission controllers + Pod Security Standards
- [ ] Bedrock Guardrails + Azure AI Content Safety overview *(new)*

---

## Phase 7: Application Operations (Weeks 36–52, ongoing)

### Job boards — weekly cadence

- [ ] LinkedIn jobs (saved searches: AI security, LLM security, AI/ML security, prompt injection, agent security, AI red team)
- [ ] Otta / Welcome to the Jungle
- [ ] CyberSecurityJobsite (UK-specific)
- [ ] eFinancialCareers (UK financial AI security)
- [ ] Wellfound (formerly AngelList) for startups
- [ ] YC Work at a Startup
- [ ] Greenhouse / Lever direct careers pages of target companies (Lakera, Anthropic, DeepMind, etc.)
- [ ] Set saved searches + email alerts on each
- [ ] 30 minutes Sunday evening: scan + queue applications for the week

### UK sponsorship filtering

- [ ] Cross-reference any UK target against UK Home Office Register of Licensed Sponsors before applying
- [ ] Maintain tagged list: confirmed sponsor / unknown / no sponsor
- [ ] Don't burn energy on unconfirmed-sponsor companies unless they're frontier labs or US defense contractor London offices

### Recruiter outreach

- [ ] Identify 5 specialist cyber recruiters with UK AI/cyber focus (e.g. Hamilton Barnes, Stott and May, Bridgewater, IDPP)
- [ ] Reach out to each with a short intro + tailored CV
- [ ] Follow up every 6 weeks

### LinkedIn outreach

- [ ] Identify 2–3 hiring managers per target company via LinkedIn
- [ ] Send a short, personalised connection note referencing one of their public posts and your published artifacts
- [ ] Cadence: 5 outreach messages per week. NOT a sales pitch — a curious-peer note

### Application tracker

- [ ] Spreadsheet or Notion DB. Columns: company, role, link, applied date, CV version used, sponsor status, recruiter contact, status, last activity, notes
- [ ] Review weekly. Pause anything stalled >4 weeks unless you have a live conversation

### Target companies

**Frontier labs (highest leverage)**
- [ ] Anthropic London
- [ ] Google DeepMind London
- [ ] OpenAI London
- [ ] Cohere

**UK Government**
- [ ] AI Security Institute (AISI), London — defender lane fit

**AI security startups**
- [ ] Lakera (Zurich; UK presence)
- [ ] HiddenLayer
- [ ] Protect AI
- [ ] Mindgard
- [ ] CalypsoAI

**Defense AI (US contractor London offices)**
- [ ] Booz Allen Hamilton UK
- [ ] Leidos UK
- [ ] Frazer-Nash
- [ ] BAE Systems Digital Intelligence
- [ ] ManTech
- [ ] Northrop Grumman UK

**Financial services AI security**
- [ ] Goldman Sachs AI security team
- [ ] JP Morgan
- [ ] HSBC AI risk
- [ ] Standard Chartered
- [ ] Bloomberg AI Engineering security

**Hedge funds with ML**
- [ ] Citadel
- [ ] Millennium
- [ ] Two Sigma

**Big Tech AI security**
- [ ] Microsoft AI Security (London)
- [ ] Google Cloud AI Security
- [ ] Amazon AI Security
- [ ] Meta AI Security

---

## Phase 8: Interview Preparation (start Week 30, ongoing) *(new)*

### System design for AI security

- [ ] Practice 5+ scenarios out loud or in writing:
  - [ ] Design detection for an LLM gateway protecting a customer-support chatbot
  - [ ] Design auth and scope model for an agent platform with tool integrations (think MCP)
  - [ ] Design a RAG pipeline that resists indirect prompt injection
  - [ ] Design SBOM and integrity checks for ingested HF models
  - [ ] Design eval gates in a CI/CD pipeline for an LLM product

### Behavioural and stakeholder

- [ ] Prepare 8 STAR stories: NSPA SOC investigation, Tenable rollout, RAG threat model + breakage, a detection rule that caught X, mentoring, leadership trajectory, USMC Meritorious Promotion context
- [ ] Practice "explain prompt injection to a CISO in 90 seconds"
- [ ] Practice "explain MCP tool abuse to a frontend engineer in 2 minutes"

### Take-home prep

- [ ] Be ready to spend 6–10 hours on a take-home; portfolio repos already in good shape so you don't start cold
- [ ] Have a dev environment ready (Ollama + Python venv + Docker) so a take-home doesn't burn setup time

### Live coding

- [ ] Light LeetCode: Python parsing, regex, log analysis, simple data transformation — NOT algorithm grinding
- [ ] Be ready to write a simple prompt classifier or eval harness from scratch in 45 minutes

---

## What to Skip

- [ ] OSCP
- [ ] CRT/CREST
- [ ] Vendor AI security certs (CAISP, AAISM)
- [ ] Multiple blog posts before applying — one solid post + harness repo + detection rules repo > three mediocre posts
- [ ] Hack The Box subscription beyond what you've done — HTB AI Red Teamer Path is "finish if started, don't start now"
- [ ] Generic ML coursework outside OMSCS
- [ ] CKA/CKS Kubernetes admin certs
- [ ] Go programming language
- [ ] macOS security depth
- [ ] Custom security tool as separate deliverable — the eval harness IS your tool
- [ ] LeetCode algorithm grinding

---

## Success Markers (by Month 12)

- [ ] Working local LLM lab built and broken
- [ ] Threat model artifact (markdown in repo)
- [ ] Published blog post
- [ ] AI incident response playbook
- [ ] Adversarial evaluation harness repo (public, README, CI)
- [ ] AI detection rules repo (Sigma + Splunk SPL + Datadog, public)
- [ ] AWS Security Specialty certification
- [ ] Hands-on familiarity with SageMaker + MLflow + Kubeflow + Bedrock Guardrails
- [ ] Working knowledge of OWASP LLM Top 10, MITRE ATLAS, OWASP API Top 10, OWASP ML Top 10, OWASP Agentic Security
- [ ] Hands-on experience with Semgrep, ZAP, Bandit, gitleaks, Syft/Grype, pip-audit, Garak, PyRIT, Promptfoo, ModelScan
- [ ] Container/Kubernetes security vocabulary
- [ ] Adversarial ML vocabulary (evasion, poisoning, MIA, model inversion)
- [ ] Agentic AI vocabulary (tool-use escalation, planner manipulation, role confusion, citation laundering, system prompt leakage)
- [ ] OMSCS coursework progressing with one AI-security-relevant project
- [ ] 25+ active applications submitted
- [ ] LinkedIn updated to reflect AI security artifacts
- [ ] 5+ system-design-for-AI-security scenarios rehearsed

---

*Last updated: May 2026 (v4)*
