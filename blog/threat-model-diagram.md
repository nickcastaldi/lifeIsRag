# Blog Post: Threat Model Diagram + Outline

## Draft title
"Building, Threat Modeling, and Breaking a RAG System: A Security Engineer's Walkthrough"

---

## Architecture Diagram (ASCII — embed in blog post)

```
                        ┌────────────────────────────────────────┐
                        │           Production RAG System         │
  ┌─────────┐  HTTPS    │  ┌──────────┐   embed   ┌───────────┐  │
  │  User   │──────────►│  │ FastAPI  │──────────►│  Chroma   │  │
  │ Browser │◄──────────│  │  /query  │◄──────────│ Vector DB │  │
  └─────────┘  JSON     │  └────┬─────┘  top-k   └───────────┘  │
                        │       │                       ▲          │
               B1 ──────┼───────┤                       │ B6       │
                        │       │ prompt                │          │
               B2 ──────┼───────┼───────────►  ┌───────────────┐ │
                        │       │            │  │  /ingest      │ │
               B3 ──────┼───────┼───────────►│  │  endpoint     │ │
                        │  ┌────▼─────┐      │  └───────┬───────┘ │
                        │  │  Ollama  │      │          │ B5       │
                        │  │ LLM      │      │          ▼          │
               B4 ──────┼──►  tool    │      │  ┌───────────────┐ │
                        │  │  calls   │      │  │  docs/        │ │
                        │  └──────────┘      │  │  corpus       │ │
                        │       │            │  └───────────────┘ │
                        │       ▼            │                     │
                        │  ┌──────────┐      │                     │
                        │  │  Tool /  │◄─────┘                     │
                        │  │  MCP     │                            │
                        │  └──────────┘                            │
                        └────────────────────────────────────────┘

  Trust Boundaries:
  B1: User ↔ API (direct injection surface)
  B2: API ↔ Vector DB (retrieval manipulation)
  B3: Vector DB chunks ↔ LLM prompt (indirect injection surface)
  B4: LLM ↔ Tools (tool abuse / scope creep)
  B5: Ingest ↔ Filesystem (path traversal)
  B6: Filesystem ↔ Vector DB (index poisoning)
```

---

## Blog Post Outline (2,500–4,000 words)

### 1. Introduction (~200 words)
- What this post covers: a complete security walkthrough of a RAG application
- Who it's for: security engineers, AI engineers who want to understand the attack surface
- Brief summary of findings

### 2. What I Built (Phase 2) (~400 words)
- Architecture: LangChain + Chroma + Ollama
- Trust boundary diagram (embed above)
- Why each component matters from a security perspective

### 3. What I Was Worried About — Threat Model (Phase 2.5) (~600 words)
- STRIDE methodology applied to each boundary
- AI-specific threat enumeration (direct injection, indirect injection, retrieval poisoning, etc.)
- Top 5 risks by impact × likelihood
- Link to `threat-model/threat-model.md`

### 4. What Standard AppSec Tooling Caught and Missed (Phase 3 Track B) (~500 words)
- Semgrep: caught hardcoded strings, missed injection vectors
- Bandit: caught subprocess calls, completely blind to LLM risks
- OWASP ZAP: found standard web vulns, no concept of prompt injection
- gitleaks / pip-audit: useful but AI-agnostic
- Key gap: **none of these tools understand semantic attack surfaces**

### 5. What Actually Broke — AI-Specific Testing (Phase 3 Tracks A + A+) (~700 words)
- Direct injection: results from Gandalf, HackAPrompt, local testing
- Indirect injection: document poisoning in action
- Garak scan findings
- PyRIT orchestrator scenario
- Promptfoo eval set results
- Link to eval harness results in `eval-harness/reports/`

### 6. What I Added to Defend It (~400 words)
- Input classifier for known injection patterns
- Canary token in system prompt
- Output classifier
- Detection rules (link to `detection-rules/`)
- Rate limiting and input length cap

### 7. What I'd Do Differently in Production (~400 words)
- SDLC integration: eval harness in CI, Sigma rules in SIEM from day one
- Least-privilege on ingest endpoint
- Structured logging schema from the start
- Human-in-the-loop for destructive tool calls
- Regular red-team exercises with updated eval prompt sets

### 8. Conclusion + Resources
- Links to all artifacts in this repo
- Key reading: OWASP LLM Top 10, MITRE ATLAS, Simon Willison's blog

---

## Screenshots to capture

- [ ] Garak scan output (terminal)
- [ ] Promptfoo report (web UI)
- [ ] Eval harness summary table
- [ ] Splunk dashboard with detection rule hits (mock data OK)
- [ ] Threat model diagram (render from above ASCII)
