"""Chạy golden eval cho guardrail, câu mơ hồ và câu hỏi học tập."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.services.guardrails import evaluate_learning_request  # noqa: E402


CASES_PATH = ROOT / "eval" / "golden_cases.json"
RESULTS_DIR = ROOT / "eval" / "results"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("offline", "live"),
        default="offline",
        help="offline không gọi API; live gọi backend và có thể gọi model.",
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Base URL FastAPI khi chạy --mode live.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Chỉ in kết quả, không ghi eval/results.",
    )
    return parser.parse_args()


def load_cases() -> list[dict]:
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    if len(cases) != 25:
        raise ValueError(f"Golden set phải có đúng 25 case, hiện có {len(cases)}.")
    ids = [case["id"] for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("Golden set có ID trùng.")
    return cases


def classify_payload(payload: dict) -> tuple[str, str | None]:
    if payload.get("needs_clarification"):
        return "clarify", payload.get("guardrail_code")
    if payload.get("blocked"):
        return "block", payload.get("guardrail_code")
    return "allow", payload.get("guardrail_code")


def score_result(
    case: dict,
    actual: dict,
    *,
    check_citations: bool,
) -> tuple[bool, list[str]]:
    expected = case["expected"]
    errors: list[str] = []
    if actual.get("action") != expected["action"]:
        errors.append(
            f"action={actual.get('action')!r}, cần {expected['action']!r}"
        )
    expected_code = expected.get("code")
    if expected_code and actual.get("code") != expected_code:
        errors.append(
            f"code={actual.get('code')!r}, cần {expected_code!r}"
        )
    min_citations = expected.get("min_citations", 0)
    if check_citations and actual.get("citation_count", 0) < min_citations:
        errors.append(
            f"citations={actual.get('citation_count', 0)}, cần >= {min_citations}"
        )
    return not errors, errors


def run_offline(case: dict) -> dict:
    decision = evaluate_learning_request(case["input"])
    if decision.allowed:
        action = "allow"
    elif decision.code == "ambiguous":
        action = "clarify"
    else:
        action = "block"
    return {
        "action": action,
        "code": decision.code,
        "answer": decision.message,
        "citation_count": 0,
    }


def live_request(case: dict, base_url: str) -> dict:
    if case["endpoint"] == "study":
        path = "/api/v1/agents/study/review"
        body = {
            "message": case["input"],
            "day": case.get("day"),
            "history": [],
        }
    else:
        path = "/api/v1/agents/direct-qa/chat"
        body = {"message": case["input"], "history": []}

    request = urllib.request.Request(
        f"{base_url.rstrip('/')}{path}",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return {
            "action": "error",
            "code": f"http_{exc.code}",
            "answer": detail,
            "citation_count": 0,
        }
    except (OSError, TimeoutError) as exc:
        return {
            "action": "error",
            "code": "connection_error",
            "answer": str(exc),
            "citation_count": 0,
        }

    action, code = classify_payload(payload)
    return {
        "action": action,
        "code": code,
        "answer": payload.get("answer", ""),
        "citation_count": len(payload.get("citations", [])),
    }


def build_markdown(report: dict) -> str:
    lines = [
        "# VLearn Eval Report",
        "",
        f"- Mode: `{report['mode']}`",
        f"- Generated: `{report['generated_at']}`",
        f"- Score: **{report['passed']}/{report['total']} "
        f"({report['pass_rate']:.1%})**",
        "",
        "| ID | Category | Expected | Actual | Code | Result |",
        "|---|---|---|---|---|---|",
    ]
    for result in report["results"]:
        lines.append(
            "| {id} | {category} | {expected} | {actual} | {code} | {status} |".format(
                id=result["id"],
                category=result["category"],
                expected=result["expected"]["action"],
                actual=result["actual"]["action"],
                code=result["actual"].get("code") or "-",
                status="PASS" if result["passed"] else "FAIL",
            )
        )
    lines.extend(["", "## Breakdown", ""])
    for category, counts in report["breakdown"].items():
        lines.append(
            f"- `{category}`: {counts['passed']}/{counts['total']} passed"
        )
    failures = [result for result in report["results"] if not result["passed"]]
    if failures:
        lines.extend(["", "## Failures", ""])
        for failure in failures:
            lines.append(
                f"- `{failure['id']}`: {'; '.join(failure['errors'])}"
            )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    cases = load_cases()
    results: list[dict] = []
    category_totals = Counter()
    category_passed = Counter()

    for case in cases:
        actual = (
            run_offline(case)
            if args.mode == "offline"
            else live_request(case, args.base_url)
        )
        passed, errors = score_result(
            case,
            actual,
            check_citations=args.mode == "live",
        )
        category_totals[case["category"]] += 1
        category_passed[case["category"]] += int(passed)
        results.append(
            {
                "id": case["id"],
                "category": case["category"],
                "input": case["input"],
                "reason": case["reason"],
                "expected": case["expected"],
                "actual": actual,
                "passed": passed,
                "errors": errors,
            }
        )

    passed_count = sum(result["passed"] for result in results)
    report = {
        "mode": args.mode,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(results),
        "passed": passed_count,
        "failed": len(results) - passed_count,
        "pass_rate": passed_count / len(results),
        "breakdown": {
            category: {
                "passed": category_passed[category],
                "total": total,
            }
            for category, total in sorted(category_totals.items())
        },
        "results": results,
    }

    if not args.no_write:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        (RESULTS_DIR / "latest.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (RESULTS_DIR / "latest.md").write_text(
            build_markdown(report),
            encoding="utf-8",
        )

    print(
        json.dumps(
            {
                "mode": report["mode"],
                "passed": report["passed"],
                "failed": report["failed"],
                "total": report["total"],
                "pass_rate": report["pass_rate"],
                "breakdown": report["breakdown"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
