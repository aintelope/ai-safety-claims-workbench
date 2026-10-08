"""Unit test for C2 access Market 8 wrap adapter."""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CONTRIB = REPO / "contrib" / "zarncke-2026-10-08-ciris-c2-access"
V1 = json.loads((CONTRIB / "source" / "c2-tool-scout-v1.json").read_text(encoding="utf-8"))
V2 = json.loads((CONTRIB / "source" / "c2-tool-scout-v2.json").read_text(encoding="utf-8"))  # noqa: E501


def _run_adapter(case_id, family, fixture_body, tmp_path):
    cases_path = tmp_path / "freeze-cases.jsonl"
    cases_path.write_text(
        json.dumps(
            {
                "case_id": case_id,
                "case_hash": "a" * 64,
                "family": family,
                "incomplete": True,
                "post_freeze": False,
                "multi_machine": False,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    raw = tmp_path / "log.jsonl"
    raw.write_text(
        json.dumps({"kind": "header"})
        + "\n"
        + json.dumps(
            {
                "case_id": case_id,
                "fixture_body": fixture_body,
                "fixture": "x.json",
                "started_at": "2026-10-08T12:00:00Z",
                "finished_at": "2026-10-08T12:00:01Z",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    trials = tmp_path / "trials.jsonl"
    subprocess.run(
        [sys.executable, "-I", str(CONTRIB / "adapter.py"), str(raw), str(cases_path), str(trials)],
        check=True,
        cwd=CONTRIB,
    )
    return json.loads(trials.read_text(encoding="utf-8").strip())


def test_v1_false_access_certificate(tmp_path):
    record = _run_adapter("c2-v1-actuation-route", "hidden-actuation", V1, tmp_path)
    assert record["result"]["certified_sufficient"] is True
    assert record["result"]["detected_or_refused"] is False


def test_v2_no_bypass(tmp_path):
    record = _run_adapter("c2-v2-stack-null", "hidden-actuation", V2, tmp_path)
    assert record["result"]["certified_sufficient"] is False
    assert record["result"]["detected_or_refused"] is True
