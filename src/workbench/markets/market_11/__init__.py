"""Market 11 (coordination without communication), registry contract version 1.

Custom wraps list hidden-coordination cases in cases.yaml (label_positive, concealed, mechanism).
"""

import yaml

CONTRACT_VERSION = 1
CASE_FIELDS = ("label_positive", "concealed", "mechanism")


def cases(contribution):
    spec = yaml.safe_load((contribution.path / "cases.yaml").read_text(encoding="utf-8")) or {}
    out, seen = [], set()
    for case in spec.get("cases") or []:
        cid = case["id"]
        if cid in seen:
            raise SystemExit(f"cases.yaml: case id {cid} repeats")
        seen.add(cid)
        row = {"case_id": cid}
        for key in ("label_positive", "concealed"):
            if key not in case:
                raise SystemExit(f"cases.yaml {cid}: missing {key}")
            row[key] = case[key]
        row["mechanism"] = case.get("mechanism") or ""
        out.append(row)
    if not out:
        raise SystemExit("cases.yaml has no cases")
    return out
