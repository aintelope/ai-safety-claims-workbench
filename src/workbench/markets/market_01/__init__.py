"""Market 1 (discovering where control resides), registry contract version 2.

A contribution lists its benchmark systems in systems.yaml: one entry per system with the registry's
frozen fields (families, adversarial_subset, components, response_statistic, min_change,
no_effect_range) plus anything the method needs to rebuild the system without seeing its ground truth
(e.g. scenario name, parameters, seed). `cases` copies them into frozen cases; freeze_complete and
components_count are derived here so they cannot disagree with the list.

For a run attempt the registry wants a hidden suite from an independent challenge operator; a
contribution's own systems.yaml is fine for a sketch and for developing a method.
"""

import yaml

CONTRACT_VERSION = 2
FREEZE_FIELDS = ("components", "response_statistic", "min_change", "no_effect_range")


def cases(contribution):
    spec = yaml.safe_load((contribution.path / "systems.yaml").read_text(encoding="utf-8")) or {}
    out, seen = [], set()
    for system in spec.get("systems") or []:
        sid = system["id"]
        if sid in seen:
            raise SystemExit(f"systems.yaml: system id {sid} repeats")
        seen.add(sid)
        case = {"case_id": sid, **{k: v for k, v in system.items() if k != "id"}}
        complete = all(case.get(f) is not None for f in FREEZE_FIELDS) and len(case.get("components") or []) > 0
        case["freeze_complete"] = complete
        if complete:
            case["components_count"] = len(case["components"])
        out.append(case)
    if not out:
        raise SystemExit("systems.yaml has no systems")
    return out
