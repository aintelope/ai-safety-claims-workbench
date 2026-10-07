"""Inspect task over a contribution's frozen cases. A contribution's task.py usually just calls
`correction_task(Path(__file__).parent)`; it may pass its own solver or scorer instead."""

import json
from pathlib import Path

from inspect_ai import Task
from inspect_ai.dataset import Sample

from .protocol import correction_episode, correction_rules


def frozen_samples(contribution_dir):
    path = Path(contribution_dir) / "freeze-cases.jsonl"
    if not path.exists():
        raise FileNotFoundError(f"{path} missing: run `workbench freeze` first; tasks run frozen cases only")
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [Sample(id=c["case_id"], input=c["correction"], metadata=c) for c in cases]


def correction_task(contribution_dir, solver=None, scorer=None):
    return Task(dataset=frozen_samples(contribution_dir), solver=solver or correction_episode(),
                scorer=scorer or correction_rules())
