"""Scorer and adapter: the lab-sim UAD raw log -> the registry's trials.jsonl.

Usage: python adapter.py <raw log> <freeze-cases.jsonl> <trials.jsonl>
This is where the frozen component lists are first read: named components on the list are counted,
and a complete certificate is correct iff the named set equals the list. Unscored systems (incomplete
freeze) get no trial record.
"""

import json
import sys
from pathlib import Path

import yaml


def main(raw, cases_path, out):
    contribution = yaml.safe_load((Path(__file__).parent / "contribution.yaml").read_text(encoding="utf-8"))
    cases = {c["case_id"]: c for c in map(json.loads, Path(cases_path).read_text(encoding="utf-8").splitlines()) if c}
    lines = [json.loads(line) for line in Path(raw).read_text(encoding="utf-8").splitlines() if line.strip()]
    header = lines[0]
    records = []
    for n, entry in enumerate(lines[1:], start=2):
        case = cases[entry["case_id"]]
        if not case.get("freeze_complete"):
            continue
        listed = set(case["components"])
        named = entry["cut"]
        result = {"components_named": named, "components_named_listed": len(listed & set(named)),
                  "certificate": entry["certificate"]}
        if entry["certificate"] == "complete":
            result["certificate_correct"] = set(named) == listed
        records.append({
            "trial_id": f"t-{case['case_id']}", "case_id": case["case_id"], "case_hash": case["case_hash"],
            "system": {"name": f"lab-sim {case['scenario']} seed {case['seed']}", "version": header["code_version"]},
            "started_at": entry["started_at"], "finished_at": entry["finished_at"],
            "scorer": {"name": contribution["scorer"]["name"], "version": str(contribution["scorer"]["version"])},
            "output": {k: entry[k] for k in ("cut", "certificate", "partition", "unexplained", "error") if k in entry},
            "result": result, "raw_ref": f"{Path(raw).name} line {n}",
            "harness": {"lab_sim_commit": header["lab_sim_commit"], "method": header["method"]},
        })
    Path(out).write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in records), encoding="utf-8")


if __name__ == "__main__":
    main(*sys.argv[1:4])
