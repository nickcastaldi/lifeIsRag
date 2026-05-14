# Incident Response Playbook: Suspected Prompt Injection in Production LLM Application

**Classification:** Confidential — Internal Security Use  
**Version:** 1.0  
**Last updated:** May 2026  
**Applies to:** Any production system using an LLM API, RAG pipeline, or AI agent

---

## Detection Signals

Initiate this playbook when **any one** of the following is observed:

| Signal | Source | Severity |
|--------|--------|----------|
| Indirect injection marker in LLM response (e.g. "INJECTION SUCCESSFUL", "EXFIL_TOKEN_*") | SIEM / Datadog rule `indirect_injection_confirmed` | **P1 — page on-call immediately** |
| System prompt content visible in LLM response | SIEM rule `system_prompt_leakage` | P2 |
| Repeated injection-pattern strings in user input (>3 from same session) | SIEM rule `prompt_injection_direct` | P2 |
| Anomalous tool-call sequence from AI agent | SIEM rule `agent_tool_abuse` | P2 |
| User report: "the chatbot said something it shouldn't have" | Support ticket | P3 — investigate within 4 hours |
| Eval harness regression on CI indicating new injection vulnerability | GitHub Actions / CI | P3 — fix before merge |

---

## Triage (first 15 minutes)

### Step 1 — Confirm the alert is genuine

```splunk
index=llm_app_logs sourcetype=llm_response session_id="<SESSION_ID>"
| table _time, user_input, llm_response, retrieved_doc_ids
| sort _time
```

- Does the response contain injection success markers? → **confirmed P1**
- Does it show system prompt fragments? → **confirmed P2**
- Is it a benign false positive? → Document and close with tuning note

### Step 2 — Identify scope

```splunk
index=llm_app_logs sourcetype=llm_response earliest=-1h
| where match(llm_response, "INJECTION SUCCESSFUL|EXFIL_TOKEN|system prompt is|instructions are")
| stats count by session_id, user_id
| sort -count
```

- How many sessions affected?
- How many distinct users?
- Is this an isolated probe or a sustained campaign?

### Step 3 — Identify the injection vector

For RAG applications, pull the retrieved document IDs from the affected session:

```splunk
index=llm_app_logs session_id="<SESSION_ID>" log_type=llm_response
| table retrieved_doc_ids, llm_response
```

Check whether those documents contain injected instructions:

```bash
# Query Chroma for the flagged document content
python3 - <<'EOF'
import chromadb
client = chromadb.PersistentClient(path="./chroma_db")
coll = client.get_collection("default")
results = coll.get(ids=["<DOC_ID>"], include=["documents", "metadatas"])
print(results)
EOF
```

---

## Containment

### P1: Confirmed indirect injection via retrieved document

1. **Quarantine the session:** Invalidate session token / block session_id at API gateway
2. **Take retrieval offline (if safe to do so):** Temporarily disable the `/query` endpoint or switch to a fallback that skips retrieval
3. **Flag contaminated documents:** Mark retrieved_doc_ids as quarantine in vector store metadata
4. **Notify affected users** (if PII or sensitive data may have been extracted): engage Legal and DPO

### P2: Direct injection / system prompt leakage, no confirmed exfiltration

1. Rate-limit or block the source IP / user account pending investigation
2. Do **not** take the service offline unless there is evidence of data exfiltration
3. Enable enhanced logging for the affected endpoint (capture full responses)

### P3: CI regression / exploratory probe

1. No user-facing action required
2. Fix the vulnerability before merging the PR that caused the regression

---

## Eradication

### Remove poisoned documents from the vector store

```bash
# Remove by document ID
python3 - <<'EOF'
import chromadb
client = chromadb.PersistentClient(path="./chroma_db")
coll = client.get_collection("default")
coll.delete(ids=["<QUARANTINE_DOC_ID_1>", "<QUARANTINE_DOC_ID_2>"])
print("Done")
EOF
```

### Harden the ingestion pipeline

- [ ] Add content scanning at ingest time (check for injection keywords before embedding)
- [ ] Restrict write access to the `docs/` directory to the ingestion service account only
- [ ] Add canary tokens to the system prompt — if they appear in output, alert immediately
- [ ] Deploy an output classifier before returning responses to users

### Patch the application (if a code-level vulnerability was confirmed)

- [ ] Add input length cap (max 2,000 chars on `/query`)
- [ ] Add input classifier (Rebuff or custom regex) before passing to LLM
- [ ] Ensure the system prompt does not contain secrets or PII
- [ ] Run the full adversarial eval harness: `python eval-harness/harness.py --target ...`

---

## Post-Incident Review

Complete within 5 business days.

### Questions to answer

1. How did the injected content enter the vector store? (direct upload, automated ingestion, compromised pipeline?)
2. What did the attacker attempt to extract or achieve?
3. Was any sensitive data exfiltrated? (check response logs + any outbound network connections)
4. Which detection rule fired first? Was there a gap between the attack and detection?
5. Does the eval harness cover this attack variant? If not, add a new prompt to `eval-harness/prompts/adversarial_prompts.json`
6. Does this require a new or updated Sigma/Splunk/Datadog rule?

### Metrics to capture

- Time to detect (TTD)
- Time to contain (TTC)
- Number of affected sessions / users
- Data classification of any potentially exfiltrated content

### Artifacts to produce

- [ ] Incident timeline (Confluence / Notion page)
- [ ] Updated threat model (`threat-model/threat-model.md`) — mark confirmed threats
- [ ] New eval harness prompt covering this attack variant
- [ ] New or updated detection rule if coverage gap identified
- [ ] Lessons learned shared with the team

---

## References

- Detection rules: `../detection-rules/`
- Eval harness: `../eval-harness/`
- Threat model: `../threat-model/threat-model.md`
- OWASP LLM Top 10: LLM01 (Prompt Injection), LLM06 (Sensitive Information Disclosure)
- MITRE ATLAS: AML.T0051 (LLM Prompt Injection), AML.T0054 (LLM Jailbreak)
