"""Copy Dietz's published gold-example responses into a raw log. Does not call any model.

Reads freeze-cases.jsonl. Each case names source (a JSON file under this folder) and
examinee_model. Writes JSON lines under $WORKBENCH_RUNS: a header, then one record per case.
The scorer lives in adapter.py: no later-behavior probe => uptake and persistence are false.
"""

import datetime as dt
import json
import os
from pathlib import Path

HERE = Path(__file__).parent


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="microseconds")


def main():
    runs = Path(os.environ.get("WORKBENCH_RUNS", HERE / "runs"))
    runs.mkdir(parents=True, exist_ok=True)
    cases = [json.loads(line) for line in (HERE / "freeze-cases.jsonl").read_text(encoding="utf-8").splitlines()
             if line.strip()]
    out = runs / f"dietz-wrap-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}.jsonl"
    header = {
        "kind": "header",
        "source": "FlorianDietz/EdgeCasesInAiAlignment gold_examples",
        "wrap": "published responses only; no model calls",
        "started_at": now(),
    }
    with open(out, "w", encoding="utf-8") as f:
        f.write(json.dumps(header, ensure_ascii=False) + "\n")
        for case in cases:
            cid = case["case_id"]
            src = HERE / case["source"]
            published = json.loads(src.read_text(encoding="utf-8"))
            exam = next(e for e in published["examinations"] if e["examinee_model"] == case["examinee_model"])
            started, finished = now(), now()
            rec = {
                "case_id": cid,
                "evaluation_id": published["evaluation_id"],
                "examinee_model": case["examinee_model"],
                "prompt": published["prompt"],
                "examinee_responses": exam["examinee_responses"],
                "evaluator_rating": exam.get("evaluator_rating"),
                "evaluator_summary": exam.get("evaluator_summary"),
                "later_behavior_probe_published": False,
                "context_reset_published": False,
                "started_at": started,
                "finished_at": finished,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
