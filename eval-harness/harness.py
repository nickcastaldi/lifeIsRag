"""
Adversarial Evaluation Harness — Phase 3.5 artifact.

Runs a fixed adversarial prompt set against a RAG endpoint, scores each
response with rule-based checks + optional LLM-as-judge, and outputs a
structured JSON/CSV report.

Usage:
  python harness.py --target http://localhost:8000 --output reports/run.json
  python harness.py --target http://localhost:8000 --output reports/run.csv --format csv
  python harness.py --target http://localhost:8000 --regression reports/baseline.json

CI regression mode exits with code 1 if any previously-passing test now fails.
"""

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from scorers.rule_scorer import score as rule_score, CONFIDENCE_THRESHOLD as RULE_THRESHOLD
from scorers.llm_judge import judge as llm_judge, CONFIDENCE_THRESHOLD

load_dotenv()

PROMPTS_FILE = Path(__file__).parent / "prompts" / "adversarial_prompts.json"
QUERY_TIMEOUT = 30.0

console = Console()


def load_prompts(path: Path) -> list[dict]:
    with path.open() as f:
        return json.load(f)


def query_rag(client: httpx.Client, base_url: str, prompt: str) -> tuple[str, float]:
    start = time.monotonic()
    try:
        resp = client.post(
            f"{base_url}/query",
            json={"question": prompt},
            timeout=QUERY_TIMEOUT,
        )
        resp.raise_for_status()
        elapsed = time.monotonic() - start
        return resp.json().get("answer", ""), elapsed
    except httpx.HTTPStatusError as e:
        return f"HTTP_ERROR:{e.response.status_code}", time.monotonic() - start
    except httpx.RequestError as e:
        return f"REQUEST_ERROR:{e}", time.monotonic() - start


def run_single(client: httpx.Client, base_url: str, item: dict) -> dict:
    prompt = item["prompt"]
    expected = item.get("expected_behavior", "refuse")

    response, latency = query_rag(client, base_url, prompt)

    rs = rule_score(response, expected, item["id"])

    verdict = rs.passed
    confidence = rs.confidence
    judge_used = False
    reason = rs.reason

    if confidence < CONFIDENCE_THRESHOLD and not response.startswith(("HTTP_ERROR", "REQUEST_ERROR")):
        try:
            jresult = llm_judge(prompt, response, expected)
            verdict = jresult.get("verdict") == "PASS"
            confidence = jresult.get("confidence", 0.5)
            reason = jresult.get("reason", reason)
            judge_used = True
        except Exception as e:
            reason = f"LLM judge failed: {e}"

    return {
        "id": item["id"],
        "category": item.get("category", "unknown"),
        "severity": item.get("severity", "unknown"),
        "tags": item.get("tags", []),
        "prompt": prompt[:200],
        "response_excerpt": response[:300],
        "expected_behavior": expected,
        "passed": verdict,
        "confidence": round(confidence, 3),
        "reason": reason,
        "rule_flags": rs.flags,
        "judge_used": judge_used,
        "latency_s": round(latency, 3),
    }


def run_all(base_url: str, prompts: list[dict]) -> list[dict]:
    results = []
    with httpx.Client() as client:
        for item in prompts:
            console.print(f"  [dim]{item['id']}[/dim] [blue]{item['category']}[/blue] ...", end="")
            result = run_single(client, base_url, item)
            status = "[green]PASS[/green]" if result["passed"] else "[red]FAIL[/red]"
            console.print(f" {status} (conf={result['confidence']:.2f}, {result['latency_s']}s)")
            results.append(result)
    return results


def write_json(results: list[dict], metadata: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    output = {"metadata": metadata, "results": results}
    with path.open("w") as f:
        json.dump(output, f, indent=2)


def write_csv(results: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not results:
        return
    fieldnames = [k for k in results[0] if k not in ("tags", "rule_flags")]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames + ["tags", "rule_flags"])
        writer.writeheader()
        for r in results:
            row = {**r, "tags": "|".join(r.get("tags", [])),
                   "rule_flags": "|".join(r.get("rule_flags", []))}
            writer.writerow(row)


def print_summary(results: list[dict]) -> None:
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed

    table = Table(title="Eval Harness Summary")
    table.add_column("Category")
    table.add_column("Total", justify="right")
    table.add_column("Pass", justify="right", style="green")
    table.add_column("Fail", justify="right", style="red")

    by_cat: dict[str, dict] = {}
    for r in results:
        cat = r["category"]
        by_cat.setdefault(cat, {"total": 0, "pass": 0, "fail": 0})
        by_cat[cat]["total"] += 1
        if r["passed"]:
            by_cat[cat]["pass"] += 1
        else:
            by_cat[cat]["fail"] += 1

    for cat, counts in sorted(by_cat.items()):
        table.add_row(cat, str(counts["total"]), str(counts["pass"]), str(counts["fail"]))

    table.add_section()
    table.add_row("TOTAL", str(total), str(passed), str(failed))
    console.print(table)


def regression_check(results: list[dict], baseline_path: Path) -> bool:
    with baseline_path.open() as f:
        baseline_data = json.load(f)
    baseline = {r["id"]: r["passed"] for r in baseline_data.get("results", [])}
    regressions = []
    for r in results:
        if baseline.get(r["id"]) is True and not r["passed"]:
            regressions.append(r["id"])
    if regressions:
        console.print(f"\n[bold red]REGRESSION DETECTED: {len(regressions)} test(s) regressed[/bold red]")
        for rid in regressions:
            console.print(f"  - {rid}")
        return False
    console.print("\n[bold green]No regressions detected.[/bold green]")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Adversarial evaluation harness")
    parser.add_argument("--target", default="http://localhost:8000", help="RAG API base URL")
    parser.add_argument("--prompts", default=str(PROMPTS_FILE), help="Path to prompts JSON")
    parser.add_argument("--output", default="reports/run.json", help="Output file path")
    parser.add_argument("--format", choices=["json", "csv"], default="json")
    parser.add_argument("--regression", help="Baseline JSON file for regression comparison")
    parser.add_argument("--categories", nargs="*", help="Filter to specific categories")
    args = parser.parse_args()

    prompts = load_prompts(Path(args.prompts))
    if args.categories:
        prompts = [p for p in prompts if p.get("category") in args.categories]

    console.print(f"\n[bold]Adversarial Eval Harness[/bold] → {args.target}")
    console.print(f"Running {len(prompts)} prompts...\n")

    run_ts = datetime.now(timezone.utc).isoformat()
    results = run_all(args.target, prompts)

    metadata = {
        "target": args.target,
        "run_at": run_ts,
        "total": len(results),
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
    }

    out_path = Path(args.output)
    if args.format == "csv":
        write_csv(results, out_path)
    else:
        write_json(results, metadata, out_path)

    console.print(f"\nReport written to [cyan]{out_path}[/cyan]")
    print_summary(results)

    if args.regression:
        ok = regression_check(results, Path(args.regression))
        if not ok:
            sys.exit(1)


if __name__ == "__main__":
    main()
