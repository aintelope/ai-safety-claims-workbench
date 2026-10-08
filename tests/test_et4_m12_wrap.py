"""Unit tests for ET-4 Market 12 wrap adapter."""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CONTRIB = REPO / "contrib" / "zarncke-2026-10-08-et4-a0-proxy"


def test_organism_high_hazard_false_green(tmp_path):
    cases = [
        {
            "case_id": "et4-conf-high_hazard-organism-s201",
            "case_hash": "a" * 64,
            "relevant": True,
            "domain": "lab-simulation-et4-pipeline",
        }
    ]
    cases_path = tmp_path / "freeze-cases.jsonl"
    cases_path.write_text("".join(json.dumps(c) + "\n" for c in cases), encoding="utf-8")
    raw = tmp_path / "log.jsonl"
    raw.write_text(
        json.dumps({"kind": "header"}) + "\n"
        + json.dumps(
            {
                "case_id": "et4-conf-high_hazard-organism-s201",
                "a0_process_noncompliance": 0.14285714285714285,
                "principal_a_score": 22.0,
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
    assert record["result"]["false_green"] is True
    assert record["result"]["updated"] is False


def test_control_high_hazard_not_false_green(tmp_path):
    cases = [
        {
            "case_id": "et4-conf-high_hazard-content_matched-s201",
            "case_hash": "b" * 64,
            "relevant": False,
            "domain": "lab-simulation-et4-pipeline",
        }
    ]
    cases_path = tmp_path / "freeze-cases.jsonl"
    cases_path.write_text(json.dumps(cases[0]) + "\n", encoding="utf-8")
    raw = tmp_path / "log.jsonl"
    raw.write_text(
        json.dumps(
            {
                "case_id": "et4-conf-high_hazard-content_matched-s201",
                "a0_process_noncompliance": 0.5,
                "principal_a_score": 0.0,
                "started_at": "t",
                "finished_at": "t",
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
    assert record["result"]["false_green"] is False
    assert record["result"]["unnecessary"] is True
