"""Adapter: Dietz wrap raw log -> registry trials.jsonl.

Usage: python adapter.py <raw log> <freeze-cases.jsonl> <trials.jsonl>
Copies published responses. Scores uptake and persistence false when the log says no
later-behavior probe and no context reset were published. Does not use evaluator_rating.
"""

import json
import sys
from pathlib import Path

import yaml


def main(raw, cases_path, out):
    contribution = yaml.safe_load((Path(__file__).parent / "contribution.yaml").read_text(encoding="utf-8"))
    cases = {c["case_id"]: c for c in map(json.loads, Path(cases_path).read_text(encoding="utf-8").splitlines()) if c}
    lines = [json.loads(line) for line in Path(raw).read_text(encoding="utf-8").splitlines() if line.strip()]
    records = []
    for n, entry in enumerate(lines, start=1):
        if entry.get("kind") == "header":
            continue
        case = cases[entry["case_id"]]
        if case["kind"] != "genuine":
            raise SystemExit(f"{entry['case_id']}: wrap only files genuine verbal-agreement episodes")
        if entry.get("later_behavior_probe_published") or entry.get("context_reset_published"):
            raise SystemExit(f"{entry['case_id']}: published later-behavior fields; this wrap does not score them")
        result = {"uptake": False, "persisted_after_reset": False}
        records.append({
            "trial_id": f"t-{case['case_id']}",
            "case_id": case["case_id"],
            "case_hash": case["case_hash"],
            "system": {
                "name": entry["examinee_model"],
                "version": str(contribution["dietz"]["commit"])[:12],
            },
            "started_at": entry["started_at"],
            "finished_at": entry["finished_at"],
            "scorer": {"name": contribution["scorer"]["name"], "version": str(contribution["scorer"]["version"])},
            "output": {
                "n_responses": len(entry.get("examinee_responses") or []),
                "evaluator_rating": entry.get("evaluator_rating"),
            },
            "result": result,
            "source": f"{entry.get('evaluation_id')} {entry['examinee_model']}",
            "raw_ref": f"{Path(raw).name} line {n}",
        })
    Path(out).write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in records), encoding="utf-8")


if __name__ == "__main__":
    main(*sys.argv[1:4])
