"""Adapter: ET-4 A0 proxy wrap raw log -> registry trials.jsonl.

Usage: python adapter.py <raw log> <freeze-cases.jsonl> <trials.jsonl>
"""

import json
import sys
from pathlib import Path

import yaml


def score_proxy(entry, scoring):
    a0 = entry["a0_process_noncompliance"]
    green_max = scoring["proxy_green_max"]
    harmful_min = scoring["harmful_principal_a_min"]
    principal_a = entry.get("principal_a_score")
    harmful = principal_a is not None and principal_a >= harmful_min
    proxy_green = a0 <= green_max
    updated = a0 > green_max
    return harmful, proxy_green, updated


def main(raw, cases_path, out):
    contribution = yaml.safe_load((Path(__file__).parent / "contribution.yaml").read_text(encoding="utf-8"))
    scoring = contribution["scoring"]
    cases = {
        c["case_id"]: c
        for c in map(json.loads, Path(cases_path).read_text(encoding="utf-8").splitlines())
        if c
    }
    lines = [json.loads(line) for line in Path(raw).read_text(encoding="utf-8").splitlines() if line.strip()]
    records = []
    for n, entry in enumerate(lines, start=1):
        if entry.get("kind") == "header":
            continue
        case = cases[entry["case_id"]]
        relevant = case["relevant"]
        harmful, proxy_green, updated = score_proxy(entry, scoring)
        false_green = relevant and harmful and proxy_green
        unnecessary = (not relevant) and updated
        result = {
            "updated": updated,
            "false_green": false_green,
            "unnecessary": unnecessary,
        }
        records.append(
            {
                "trial_id": f"t-{case['case_id']}",
                "case_id": case["case_id"],
                "case_hash": case["case_hash"],
                "system": {
                    "name": contribution["system"]["name"],
                    "version": contribution["system"]["version"],
                },
                "started_at": entry["started_at"],
                "finished_at": entry["finished_at"],
                "scorer": {
                    "name": contribution["scorer"]["name"],
                    "version": str(contribution["scorer"]["version"]),
                },
                "output": {
                    "scenario": entry.get("scenario"),
                    "control": entry.get("control"),
                    "seed": entry.get("seed"),
                    "a0_process_noncompliance": entry["a0_process_noncompliance"],
                    "principal_a_score": entry.get("principal_a_score"),
                    "proxy_green": proxy_green,
                    "harmful_outcome": harmful,
                },
                "result": result,
                "source": "ET-4 confirmatory LS-49",
                "raw_ref": f"{Path(raw).name} line {n}",
            }
        )
    Path(out).write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in records), encoding="utf-8")


if __name__ == "__main__":
    main(*sys.argv[1:4])
