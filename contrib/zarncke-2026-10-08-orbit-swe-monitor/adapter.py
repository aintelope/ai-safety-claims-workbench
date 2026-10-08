"""Adapter: Orbit Table 13 wrap raw log -> registry trials.jsonl.

Usage: python adapter.py <raw log> <freeze-cases.jsonl> <trials.jsonl>
Attack success is copied into output only. Market 8 booleans stay false: the paper does not report
detected_or_refused or certified_sufficient.
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
        if case["family"] == "complete" or not case["incomplete"]:
            raise SystemExit(f"{entry['case_id']}: wrap only scores incomplete-interface cases")
        if "collusion_asr" not in entry:
            raise SystemExit(f"{entry['case_id']}: log missing published collusion_asr")
        result = {"detected_or_refused": False, "certified_sufficient": False}
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
                    "defense": entry.get("defense"),
                    "collusion_asr": entry["collusion_asr"],
                    "collusion_ci": entry.get("collusion_ci"),
                    "undefended_collusion_asr": entry.get("undefended_collusion_asr"),
                    "compromised_asr_same_defense": entry.get("compromised_asr_same_defense"),
                },
                "result": result,
                "source": "arXiv:2609.33102v1 Table 13",
                "raw_ref": f"{Path(raw).name} line {n}",
            }
        )
    Path(out).write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in records), encoding="utf-8")


if __name__ == "__main__":
    main(*sys.argv[1:4])
