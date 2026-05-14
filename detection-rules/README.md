# AI Detection Rules — Phase 4.5 Artifact

LLM-specific detection rules in Sigma, Splunk SPL, and Datadog format. Each rule covers a distinct attack vector against AI/LLM applications.

**NATO SOC + Splunk + LLM threat surface is a combination very few candidates have. This directory makes it visible.**

---

## Rule Index

| Rule | Sigma | Splunk | Datadog | Severity |
|------|-------|--------|---------|----------|
| Direct prompt injection | `sigma/prompt_injection_direct.yml` | `splunk/prompt_injection_direct.spl` | `datadog/prompt_injection_direct.json` | High |
| Indirect injection (confirmed) | `sigma/prompt_injection_indirect.yml` | `splunk/indirect_injection_response.spl` | `datadog/indirect_injection_confirmed.json` | Critical |
| Jailbreak / role confusion | `sigma/jailbreak_role_confusion.yml` | — | — | Medium |
| System prompt leakage | `sigma/system_prompt_leakage.yml` | `splunk/system_prompt_leakage.spl` | — | High |
| Agent tool abuse | `sigma/agent_tool_abuse.yml` | — | — | High |

---

## Detection Signals Covered

| Signal type | Rules |
|-------------|-------|
| Input classifiers (string matching) | `prompt_injection_direct`, `jailbreak_role_confusion` |
| Output classifiers (response analysis) | `prompt_injection_indirect`, `system_prompt_leakage` |
| Canary tokens | `prompt_injection_indirect` (EXFIL_TOKEN pattern) |
| Behavioural telemetry (tool-call patterns) | `agent_tool_abuse` |

---

## Log Schema Requirements

Rules assume the following fields in your LLM application logs:

```json
{
  "source": "llm_app",
  "service": "rag-api",
  "log_type": "llm_query | llm_response | tool_call",
  "session_id": "uuid",
  "user_id": "string",
  "timestamp": "ISO8601",
  "model_id": "string",
  "endpoint": "/query | /ingest",
  "user_input": "string",
  "llm_response": "string",
  "retrieved_doc_ids": ["string"],
  "tool_name": "string",
  "tool_args": {},
  "call_sequence_position": 0,
  "latency_ms": 0
}
```

Wire this up in your RAG app's FastAPI middleware before deploying the detection rules.

---

## How to Deploy

**Sigma → generic SIEM:**
```bash
sigmac -t splunk -c splunk-windows detection-rules/sigma/prompt_injection_direct.yml
```

**Splunk:** Import `.spl` files as saved searches. Schedule at intervals noted in each file's comments.

**Datadog:** POST the JSON files to the Datadog Security Rules API or import via the UI.

---

## False Positive Expectations

| Rule | Expected FP rate | Tuning |
|------|-----------------|--------|
| Direct injection | ~5% on broad user base | Allowlist security team session IDs |
| Indirect injection | <0.1% | Suppress CI/eval-harness runs |
| Jailbreak/role confusion | ~10–15% | Correlate with session frequency |
| System prompt leakage | ~2% | Update string if system prompt changes |
| Agent tool abuse | Varies by app | Tune scope-creep threshold per workflow |
