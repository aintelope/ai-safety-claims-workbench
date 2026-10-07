"""A contribution is one folder under contrib/, named like the registry sketch it exports to:
{submitter}-{date}-{slug}. contribution.yaml says which market and which type:

  inspect  (default) an Inspect task built on the market scaffold. Its log is the standard: samples carry
           metadata.case_id and the scorer's metadata holds the market's result fields, so the registry's
           import-inspect is the whole adapter.
  custom   a self-contained directory with its own entrypoint (`run`) and raw-log format, plus `adapter`,
           a script that turns its raw log into trials.jsonl.
"""

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

ID = re.compile(r"^([a-z0-9][a-z0-9-]{1,31})-(\d{4}-\d{2}-\d{2})-([a-z0-9][a-z0-9-]{1,47})$")
FREEZE = "freeze.yaml"
CASES = "freeze-cases.jsonl"
RUNS = "runs"


@dataclass
class Contribution:
    path: Path
    id: str
    market: str
    type: str
    submitter: str
    filed_at: str
    system: dict
    description: str
    raw: dict

    @property
    def runs(self):
        return self.path / RUNS

    def latest_log(self):
        logs = sorted((p for p in self.runs.glob("*") if p.is_file()), key=lambda p: p.stat().st_mtime)
        if not logs:
            raise SystemExit(f"no run log under {self.runs}; run `workbench run {self.id}` first")
        return logs[-1]


def load(repo, contribution_id):
    path = Path(repo) / "contrib" / contribution_id
    if not (path / "contribution.yaml").exists():
        raise SystemExit(f"no contribution contrib/{contribution_id}/contribution.yaml")
    raw = yaml.safe_load((path / "contribution.yaml").read_text(encoding="utf-8")) or {}
    m = ID.match(contribution_id)
    if not m:
        raise SystemExit(f"{contribution_id}: folder name must be {{submitter}}-{{YYYY-MM-DD}}-{{slug}}")
    if raw.get("id") != contribution_id or raw.get("submitter") != m.group(1):
        raise SystemExit(f"contribution.yaml id and submitter must match the folder name {contribution_id}")
    kind = raw.get("type", "inspect")
    if kind not in ("inspect", "custom"):
        raise SystemExit("contribution.yaml type must be inspect or custom")
    if kind == "custom" and not (raw.get("run") and raw.get("adapter")):
        raise SystemExit("a custom contribution names `run` (its entrypoint) and `adapter` (raw log -> trials.jsonl)")
    system = raw.get("system") or {}
    if not system.get("name") or not system.get("version"):
        raise SystemExit("contribution.yaml system needs name and version (the system under test, frozen)")
    return Contribution(path=path, id=contribution_id, market=raw.get("market", ""), type=kind,
                        submitter=m.group(1), filed_at=m.group(2), system=system,
                        description=raw.get("description", ""), raw=raw)
