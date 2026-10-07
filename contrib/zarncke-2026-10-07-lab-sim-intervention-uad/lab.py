"""Locate and pin the lab simulation (book repo) the method runs from."""

import os
import subprocess
from pathlib import Path

import yaml

HERE = Path(__file__).parent


def pin():
    return yaml.safe_load((HERE / "contribution.yaml").read_text(encoding="utf-8"))["lab_sim"]


def lab_sim_path():
    """$LAB_SIM_ROOT, else the book repo checked out next to the workbench."""
    default = HERE.parents[2] / "towards-asi-alignment" / pin()["path"]
    path = Path(os.environ.get("LAB_SIM_ROOT") or default)
    if not (path / "lab_sim" / "__init__.py").exists():
        raise SystemExit(f"lab simulation not found at {path}; set LAB_SIM_ROOT")
    return path.resolve()


def check_pinned(path):
    """The run uses exactly the pinned commit, unmodified. Returns the commit."""
    p = pin()
    git = lambda *a: subprocess.run(["git", *a], cwd=path, capture_output=True, text=True).stdout.strip()
    commit = git("rev-parse", "HEAD")
    changed = git("diff", "--name-only", p["commit"], "--", ".")
    dirty = git("status", "--porcelain", "--", ".")
    if changed or dirty:
        raise SystemExit(f"lab simulation differs from the pinned commit {p['commit'][:12]}:\n{changed}\n{dirty}")
    return commit
