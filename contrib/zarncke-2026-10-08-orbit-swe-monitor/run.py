"""Copy published Orbit Table 13 collusion cells into a raw log. Does not call any model."""

import datetime as dt
import hashlib
import json
import os
from pathlib import Path

HERE = Path(__file__).parent
TABLE = HERE / "source" / "table-13.txt"

# Collusion attack success from arXiv:2609.33102v1 Table 13 (SWE-Bench multi-issue).
PUBLISHED = {
    "swe-mi-monitor-collusion": {
        "defense": "myopic_llm_monitor",
        "collusion_asr": 0.300,
        "collusion_ci_low": 0.191,
        "collusion_ci_high": 0.438,
        "compromised_asr": 0.120,
    },
    "swe-mi-guardian-collusion": {
        "defense": "guardian_agent",
        "collusion_asr": 0.340,
        "collusion_ci_low": 0.224,
        "collusion_ci_high": 0.478,
        "compromised_asr": 0.120,
    },
}
UNDEFENDED_COLLUSION_ASR = 0.300
UNDEFENDED_COLLUSION_CI = (0.191, 0.438)
COMPROMISED_COLUMN = {"undefended": 0.720, "myopic_llm_monitor": 0.120, "guardian_agent": 0.120}


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="microseconds")


def table_sha256():
    return hashlib.sha256(TABLE.read_bytes()).hexdigest()


def main():
    runs = Path(os.environ.get("WORKBENCH_RUNS", HERE / "runs"))
    runs.mkdir(parents=True, exist_ok=True)
    cases = [
        json.loads(line)
        for line in (HERE / "freeze-cases.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    out = runs / f"orbit-swe-wrap-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}.jsonl"
    header = {
        "kind": "header",
        "source": "arXiv:2609.33102v1 Table 13 (SWE-Bench multi-issue)",
        "wrap": "published attack-success rates only; no model calls",
        "table_sha256": table_sha256(),
        "table_excerpt": TABLE.read_text(encoding="utf-8"),
        "compromised_agent_column_excluded_from_score_table": COMPROMISED_COLUMN,
        "started_at": now(),
    }
    with open(out, "w", encoding="utf-8") as f:
        f.write(json.dumps(header, ensure_ascii=False) + "\n")
        for case in cases:
            cid = case["case_id"]
            pub = PUBLISHED.get(cid)
            if pub is None:
                raise SystemExit(f"no published collusion cell for {cid}")
            started, finished = now(), now()
            rec = {
                "case_id": cid,
                "defense": pub["defense"],
                "collusion_asr": pub["collusion_asr"],
                "collusion_ci": [pub["collusion_ci_low"], pub["collusion_ci_high"]],
                "undefended_collusion_asr": UNDEFENDED_COLLUSION_ASR,
                "undefended_collusion_ci": list(UNDEFENDED_COLLUSION_CI),
                "compromised_asr_same_defense": pub["compromised_asr"],
                "started_at": started,
                "finished_at": finished,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
