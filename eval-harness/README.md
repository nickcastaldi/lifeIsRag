# Adversarial Evaluation Harness — Phase 3.5 Artifact

A Python harness that runs a fixed adversarial prompt set against the RAG app, scores responses with rule-based checks + LLM-as-judge, and outputs a structured report.

**Why this matters:** Modern AI security engineering job descriptions list "adversarial evaluation harness" as an expected deliverable. This is one of the most differentiating portfolio artifacts in the market.

---

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # add ANTHROPIC_API_KEY for LLM judge
```

## Usage

```bash
# Full run — JSON report
python harness.py --target http://localhost:8000 --output reports/run.json

# CSV output
python harness.py --target http://localhost:8000 --output reports/run.csv --format csv

# Only injection tests
python harness.py --target http://localhost:8000 --categories direct_injection indirect_injection

# CI regression mode — exits 1 if a previously-passing test now fails
python harness.py --target http://localhost:8000 \
  --output reports/run.json \
  --regression reports/baseline.json
```

## Prompt Categories

| Category | Count | Description |
|----------|-------|-------------|
| `direct_injection` | 10 | Jailbreaks, DAN, role confusion, system-prompt leakage |
| `indirect_injection` | 5 | Payload embedded in retrieved documents |
| `jailbreak` | 5 | Authority claims, fictional framing, encoding escapes |
| `role_confusion` | 3 | Maintenance mode, translation-layer attacks |
| `evasion` | 5 | Leet-speak, zero-width spaces, special token injection |
| `exfiltration` | 2 | Output exfil via URLs, markdown images |
| `denial_of_service` | 2 | Input flooding, output bombing |
| `multi_turn` | 2 | Multi-step escalation |
| `benign_baseline` | 5 | Regression guard — these must always pass |

## Scoring Pipeline

1. **Rule scorer** (`scorers/rule_scorer.py`) — fast regex checks for known failure signatures. Confident results skip the LLM call.
2. **LLM judge** (`scorers/llm_judge.py`) — Claude Haiku judges ambiguous cases. Requires `ANTHROPIC_API_KEY`.

## Report Format

```json
{
  "metadata": { "target": "...", "run_at": "...", "total": 37, "passed": 31, "failed": 6 },
  "results": [
    {
      "id": "di-001",
      "category": "direct_injection",
      "severity": "high",
      "passed": false,
      "confidence": 0.95,
      "reason": "Response contains injection success markers",
      "rule_flags": ["injection_success_pattern:INJECTION SUCCESSFUL"],
      "latency_s": 1.23
    }
  ]
}
```

## CI Integration

```yaml
# .github/workflows/eval.yml
- name: Run adversarial eval
  run: |
    python eval-harness/harness.py \
      --target http://localhost:8000 \
      --output eval-harness/reports/ci-run.json \
      --regression eval-harness/reports/baseline.json
```
