"""Market 8 (auditor can sufficiently inspect the system), registry contract version 2.

A contribution lists access-model cases in cases.yaml. `cases` turns them into frozen cases for
freeze-cases.jsonl. Custom wraps (published tables, no model) use type custom with run.py and adapter.py.
"""

import yaml

CONTRACT_VERSION = 2
CASE_FIELDS = ("family", "incomplete", "post_freeze", "multi_machine")
FAMILIES = frozenset(
    {
        "hidden-state",
        "hidden-communication",
        "hidden-actuation",
        "hidden-controller",
        "hidden-internal",
        "complete",
    }
)


def cases(contribution):
    spec = yaml.safe_load((contribution.path / "cases.yaml").read_text(encoding="utf-8")) or {}
    out, seen = [], set()
    for case in spec.get("cases") or []:
        cid = case["id"]
        if cid in seen:
            raise SystemExit(f"cases.yaml: case id {cid} repeats")
        seen.add(cid)
        family = case["family"]
        if family not in FAMILIES:
            raise SystemExit(f"cases.yaml {cid}: unknown family {family}")
        row = {"case_id": cid}
        for key in CASE_FIELDS:
            if key not in case:
                raise SystemExit(f"cases.yaml {cid}: missing {key}")
            row[key] = case[key]
        out.append(row)
    if not out:
        raise SystemExit("cases.yaml has no cases")
    return out
