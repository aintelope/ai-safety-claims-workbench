"""Unit tests for S7 Market 11 wrap adapter."""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CONTRIB = REPO / "contrib" / "zarncke-2026-10-08-lab-sim-s7-hidden-coord"


def test_shared_slot_miss(tmp_path):
    cases = [
        {
            "case_id": "shared_slot-s9101",
            "case_hash": "a" * 64,
            "label_positive": True,
            "concealed": False,
            "mechanism": "shared_model_weights_no_runtime_messages",
        }
    ]
    cases_path = tmp_path / "freeze-cases.jsonl"
    cases_path.write_text(json.dumps(cases[0]) + "\n", encoding="utf-8")
    raw = tmp_path / "log.jsonl"
    raw.write_text(
        json.dumps(
            {
                "case_id": "shared_slot-s9101",
                "blind_exact": False,
                "blind_uad_score": 0.0,
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
    assert record["result"]["called_positive"] is False
    assert record["result"]["score"] == 0.0
