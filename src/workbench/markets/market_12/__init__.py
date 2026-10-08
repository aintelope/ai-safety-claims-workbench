"""Market 12 (safety proxy tracks the real thing), registry contract version 1.

Custom wraps list environmental shifts in cases.yaml (relevant, domain). Shift labels are frozen before
scoring the proxy.
"""

import yaml

CONTRACT_VERSION = 1
CASE_FIELDS = ("relevant", "domain")


def cases(contribution):
    spec = yaml.safe_load((contribution.path / "cases.yaml").read_text(encoding="utf-8")) or {}
    out, seen = [], set()
    for case in spec.get("cases") or []:
        cid = case["id"]
        if cid in seen:
            raise SystemExit(f"cases.yaml: case id {cid} repeats")
        seen.add(cid)
        row = {"case_id": cid}
        for key in CASE_FIELDS:
            if key not in case:
                raise SystemExit(f"cases.yaml {cid}: missing {key}")
            row[key] = case[key]
        out.append(row)
    if not out:
        raise SystemExit("cases.yaml has no cases")
    return out
