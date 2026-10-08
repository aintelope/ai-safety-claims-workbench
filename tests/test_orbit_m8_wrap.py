"""Unit test for Orbit Market 8 wrap adapter (no network, no full export)."""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CONTRIB = REPO / "contrib" / "zarncke-2026-10-08-orbit-swe-monitor"


def test_adapter_sets_both_flags_false(tmp_path):
    cases = [
        {
            "case_id": "swe-mi-monitor-collusion",
            "case_hash": "a" * 64,
            "family": "hidden-communication",
            "incomplete": True,
            "post_freeze": False,
            "multi_machine": False,
        },
        {
            "case_id": "swe-mi-guardian-collusion",
            "case_hash": "b" * 64,
            "family": "hidden-communication",
            "incomplete": True,
            "post_freeze": False,
            "multi_machine": False,
        },
    ]
    cases_path = tmp_path / "freeze-cases.jsonl"
    cases_path.write_text("".join(json.dumps(c) + "\n" for c in cases), encoding="utf-8")
    raw = tmp_path / "log.jsonl"
    raw.write_text(
        json.dumps({"kind": "header"}) + "\n"
        + json.dumps(
            {
                "case_id": "swe-mi-monitor-collusion",
                "collusion_asr": 0.3,
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
    record = json.loads(trials.read_text(encoding="utf-8").strip())
    assert record["result"]["detected_or_refused"] is False
    assert record["result"]["certified_sufficient"] is False
    assert record["output"]["collusion_asr"] == 0.3


def test_adapter_rejects_complete_case(tmp_path):
    cases_path = tmp_path / "freeze-cases.jsonl"
    cases_path.write_text(
        json.dumps(
            {
                "case_id": "complete-1",
                "case_hash": "c" * 64,
                "family": "complete",
                "incomplete": False,
                "post_freeze": False,
                "multi_machine": False,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    raw = tmp_path / "log.jsonl"
    raw.write_text(
        json.dumps({"case_id": "complete-1", "collusion_asr": 0.0, "started_at": "t", "finished_at": "t"}) + "\n",
        encoding="utf-8",
    )
    trials = tmp_path / "trials.jsonl"
    r = subprocess.run(
        [sys.executable, "-I", str(CONTRIB / "adapter.py"), str(raw), str(cases_path), str(trials)],
        cwd=CONTRIB,
        capture_output=True,
        text=True,
    )
    assert r.returncode != 0
    assert "incomplete" in r.stderr or "complete" in r.stderr
