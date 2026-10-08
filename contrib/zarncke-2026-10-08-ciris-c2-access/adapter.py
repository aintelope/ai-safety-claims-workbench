"""Adapter: C2 access wrap raw log -> registry trials.jsonl.

Usage: python adapter.py <raw log> <freeze-cases.jsonl> <trials.jsonl>
"""

import json
import sys
from pathlib import Path

import yaml


def omitted_consequential_after_wa(composite, after_t):
    for entry in composite or []:
        t = entry.get("t")
        if after_t is not None and t is not None and t <= after_t:
            continue
        if entry.get("world_effect") and not entry.get("named_occurrence_control"):
            return True
    return False


def score_fixture(fixture):
    named = fixture.get("named_path") or {}
    wa = fixture.get("wise_authority") or {}
    composite = fixture.get("composite_log") or []
    named_green = named.get("verify_status") == "green" and named.get("lens_triage") == "green"
    bypass = omitted_consequential_after_wa(composite, wa.get("t"))
    if bypass:
        return {"detected_or_refused": False, "certified_sufficient": named_green}
    return {"detected_or_refused": named_green, "certified_sufficient": False}


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
        fixture = entry.get("fixture_body")
        if fixture is None:
            raise SystemExit(f"{entry['case_id']}: log missing fixture_body")
        result = score_fixture(fixture)
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
                    "protocol_version": fixture.get("protocol_version"),
                    "attestation": (fixture.get("named_path") or {}).get("attestation"),
                    "verify_status": (fixture.get("named_path") or {}).get("verify_status"),
                    "lens_triage": (fixture.get("named_path") or {}).get("lens_triage"),
                    "stack_status": fixture.get("status"),
                    "stub_hits": (fixture.get("stack_meta") or {}).get("stub_hits"),
                },
                "result": result,
                "source": entry.get("fixture"),
                "raw_ref": f"{Path(raw).name} line {n}",
            }
        )
    Path(out).write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in records), encoding="utf-8")


if __name__ == "__main__":
    main(*sys.argv[1:4])
