import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES_PATH = ROOT / "eval" / "golden_cases.json"

with CASES_PATH.open(encoding="utf-8") as handle:
    cases = json.load(handle)

results = []
for case in cases:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "chatbot.py"), case["input"]],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(ROOT),
    )
    results.append({
        "id": case["id"],
        "type": case["type"],
        "input": case["input"],
        "expected_behavior": case["expected_behavior"],
        "exit_code": proc.returncode,
        "output": proc.stdout.strip(),
    })

print(json.dumps(results, ensure_ascii=False, indent=2))
