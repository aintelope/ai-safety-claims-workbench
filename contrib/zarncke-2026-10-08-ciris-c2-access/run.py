"""Copy frozen C2 tool-scout fixtures into a raw log. Does not call CIRISAgent."""

import datetime as dt
import hashlib
import json
import os
from pathlib import Path

HERE = Path(__file__).parent
SOURCE = HERE / "source"

FIXTURE_FOR_CASE = {
    "c2-v1-actuation-route": "c2-tool-scout-v1.json",
    "c2-v1-state-route": "c2-tool-scout-v1.json",
    "c2-v2-stack-null": "c2-tool-scout-v2.json",
}


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="microseconds")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    runs = Path(os.environ.get("WORKBENCH_RUNS", HERE / "runs"))
    runs.mkdir(parents=True, exist_ok=True)
    cases = [
        json.loads(line)
        for line in (HERE / "freeze-cases.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    fixtures_meta = {name: sha256(SOURCE / name) for name in sorted({v for v in FIXTURE_FOR_CASE.values()})}
    out = runs / f"c2-access-wrap-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}.jsonl"
    header = {
        "kind": "header",
        "source": "towards-asi-alignment experiments/backtest/fixtures/c2-tool-scout-v*.json",
        "wrap": "fixture snapshots only; no live CIRIS stack",
        "fixture_sha256": fixtures_meta,
        "started_at": now(),
    }
    with open(out, "w", encoding="utf-8") as f:
        f.write(json.dumps(header, ensure_ascii=False) + "\n")
        for case in cases:
            cid = case["case_id"]
            fixture_name = FIXTURE_FOR_CASE.get(cid)
            if fixture_name is None:
                raise SystemExit(f"no fixture mapping for {cid}")
            fixture_path = SOURCE / fixture_name
            fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
            started, finished = now(), now()
            rec = {
                "case_id": cid,
                "family": case["family"],
                "fixture": fixture_name,
                "fixture_sha256": sha256(fixture_path),
                "fixture_body": fixture,
                "started_at": started,
                "finished_at": finished,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
