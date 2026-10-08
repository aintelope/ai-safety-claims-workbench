"""Copy pinned ET-4 confirmatory records into a raw log. Does not re-run the simulation."""

import datetime as dt
import hashlib
import json
import os
from pathlib import Path

HERE = Path(__file__).parent
SOURCE = HERE / "source" / "confirmatory-records.json"


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="microseconds")


def source_sha256():
    return hashlib.sha256(SOURCE.read_bytes()).hexdigest()


def case_id(record):
    return f"et4-conf-{record['scenario']}-{record['control']}-s{record['seed']}"


def main():
    runs = Path(os.environ.get("WORKBENCH_RUNS", HERE / "runs"))
    runs.mkdir(parents=True, exist_ok=True)
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    by_id = {case_id(r): r for r in payload["records"]}
    cases = [
        json.loads(line)
        for line in (HERE / "freeze-cases.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    out = runs / f"et4-a0-wrap-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}.jsonl"
    header = {
        "kind": "header",
        "source_sha256": source_sha256(),
        "et4_protocol_version": payload["et4_protocol_version"],
        "code_version": payload["code_version"],
        "preregistration_source_commit": payload["preregistration_source_commit"],
        "started_at": now(),
    }
    with open(out, "w", encoding="utf-8") as f:
        f.write(json.dumps(header, ensure_ascii=False) + "\n")
        for case in cases:
            cid = case["case_id"]
            record = by_id.get(cid)
            if record is None:
                raise SystemExit(f"no confirmatory record for frozen case {cid}")
            started, finished = now(), now()
            a0 = record["affordances"]["A0"]["process_noncompliance"]
            principal_a = (record.get("scorecard") or {}).get("scores") or {}
            principal_a = principal_a.get("principal_a")
            f.write(
                json.dumps(
                    {
                        "case_id": cid,
                        "scenario": record["scenario"],
                        "control": record["control"],
                        "seed": record["seed"],
                        "eligible": record.get("eligible"),
                        "a0_process_noncompliance": a0,
                        "principal_a_score": principal_a,
                        "scorecard_status": (record.get("scorecard") or {}).get("status"),
                        "started_at": started,
                        "finished_at": finished,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
