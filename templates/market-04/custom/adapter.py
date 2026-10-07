"""Adapter: this contribution's raw CSV event log -> the registry's trials.jsonl.

Usage: python adapter.py <raw log> <freeze-cases.jsonl> <trials.jsonl>
It copies what the log says (times, answers, verdicts) and the frozen case hashes. It decides nothing.
"""

import csv
import json
import sys
from pathlib import Path

import yaml


def main(raw, cases_path, out):
    contribution = yaml.safe_load((Path(__file__).parent / "contribution.yaml").read_text(encoding="utf-8"))
    cases = {c["case_id"]: c for c in map(json.loads, Path(cases_path).read_text(encoding="utf-8").splitlines()) if c}
    events = {}
    with open(raw, newline="", encoding="utf-8") as f:
        for n, row in enumerate(csv.DictReader(f), start=2):
            events.setdefault(row["case_id"], []).append((n, row))
    records = []
    for cid, rows in events.items():
        by_event = {row["event"]: row for _, row in rows}
        records.append({
            "trial_id": f"t-{cid}", "case_id": cid, "case_hash": cases[cid]["case_hash"],
            "system": {"name": contribution["system"]["name"], "version": str(contribution["system"]["version"])},
            "started_at": by_event["start"]["time"], "finished_at": by_event["end"]["time"],
            "scorer": {"name": contribution["scorer"]["name"], "version": str(contribution["scorer"]["version"])},
            "output": {"answer": by_event["answer"]["text"], "answer_after_reset": by_event["answer_after_reset"]["text"]},
            "result": json.loads(by_event["verdict"]["text"]),
            "raw_ref": f"{Path(raw).name} rows {rows[0][0]}-{rows[-1][0]}",
        })
    Path(out).write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in records), encoding="utf-8")


if __name__ == "__main__":
    main(*sys.argv[1:4])
