"""Adapter: S7 blind battery wrap raw log -> registry trials.jsonl.

Usage: python adapter.py <raw log> <freeze-cases.jsonl> <trials.jsonl>
"""

import json
import sys
from pathlib import Path

import yaml


def main(raw, cases_path, out):
    contribution = yaml.safe_load((Path(__file__).parent / "contribution.yaml").read_text(encoding="utf-8"))
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
        called_positive = bool(entry["blind_exact"])
        score = float(entry["blind_uad_score"])
        result = {"score": score, "called_positive": called_positive}
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
                    "seed": entry.get("seed"),
                    "true_pair": entry.get("true_pair"),
                    "blind_merged": entry.get("blind_merged"),
                    "blind_clusters": entry.get("blind_clusters"),
                },
                "result": result,
                "source": "S7 blind battery LS-30",
                "raw_ref": f"{Path(raw).name} line {n}",
            }
        )
    Path(out).write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in records), encoding="utf-8")


if __name__ == "__main__":
    main(*sys.argv[1:4])
