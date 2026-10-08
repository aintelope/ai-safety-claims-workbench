"""Copy pinned S7 blind-battery rows into a raw log. Does not re-run the simulation."""

import datetime as dt
import hashlib
import json
import os
from pathlib import Path

HERE = Path(__file__).parent
SOURCE = HERE / "source" / "s7-blind-battery-excerpt.json"


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="microseconds")


def source_sha256():
    return hashlib.sha256(SOURCE.read_bytes()).hexdigest()


def case_id(row):
    return f"{row['scenario']}-s{row['seed']}"


def main():
    runs = Path(os.environ.get("WORKBENCH_RUNS", HERE / "runs"))
    runs.mkdir(parents=True, exist_ok=True)
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    by_id = {case_id(r): r for r in payload["rows"]}
    cases = [
        json.loads(line)
        for line in (HERE / "freeze-cases.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    out = runs / f"s7-blind-wrap-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}.jsonl"
    header = {
        "kind": "header",
        "source_sha256": source_sha256(),
        "code_version": payload["code_version"],
        "backend": payload["backend"],
        "detector": "blind",
        "started_at": now(),
    }
    with open(out, "w", encoding="utf-8") as f:
        f.write(json.dumps(header, ensure_ascii=False) + "\n")
        for case in cases:
            cid = case["case_id"]
            row = by_id.get(cid)
            if row is None:
                raise SystemExit(f"no S7 row for frozen case {cid}")
            blind = row["detectors"]["blind"]
            started, finished = now(), now()
            f.write(
                json.dumps(
                    {
                        "case_id": cid,
                        "scenario": row["scenario"],
                        "seed": row["seed"],
                        "true_pair": row.get("true_pair"),
                        "blind_exact": blind["exact"],
                        "blind_merged": blind["merged"],
                        "blind_uad_score": blind["uad_score"],
                        "blind_clusters": blind.get("nonsingleton_clusters"),
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
