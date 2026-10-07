"""End to end: freeze, run (mock model or script), and export each example into a scratch copy of the
registry, whose own dry run must find the score table equal to the one derived from the trials."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
EXAMPLES = sorted(p.name for p in (REPO / "contrib").iterdir() if (p / "contribution.yaml").exists())
GIT_ENV = {"GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "test@example.org",
           "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "test@example.org"}


def registry_source():
    path = Path(os.environ.get("WORKBENCH_REGISTRY") or REPO.parent / "ai-safety-claims")
    if not (path / "validator" / "__main__.py").exists():
        pytest.skip("registry checkout not found (set WORKBENCH_REGISTRY)")
    return path


@pytest.fixture
def trees(tmp_path):
    ignore = shutil.ignore_patterns(".git", ".venv", "*.egg-info", "__pycache__", "runs", "registry")
    wb, reg = tmp_path / "workbench", tmp_path / "registry"
    shutil.copytree(REPO, wb, ignore=ignore)
    shutil.copytree(registry_source(), reg, ignore=ignore)
    env = {**os.environ, **GIT_ENV, "WORKBENCH_REGISTRY": str(reg)}
    for args in (["init", "-q", "-b", "main"], ["remote", "add", "origin", "git@github.com:aintelope/ai-safety-claims-workbench.git"],
                 ["add", "-A"], ["commit", "-qm", "init"]):
        subprocess.run(["git", *args], cwd=wb, env=env, check=True)
    return wb, reg, env


def workbench(wb, env, *args):
    return subprocess.run([sys.executable, "-m", "workbench.cli", *args], cwd=wb, env=env,
                          capture_output=True, text=True)


def lab_sim_root():
    return Path(os.environ.get("LAB_SIM_ROOT") or REPO.parent / "towards-asi-alignment" / "experiments" / "lab-simulation")


@pytest.mark.parametrize("cid", EXAMPLES)
def test_example_exports(trees, cid):
    wb, reg, env = trees
    if "lab_sim" in yaml.safe_load((REPO / "contrib" / cid / "contribution.yaml").read_text(encoding="utf-8")):
        if not (lab_sim_root() / "lab_sim").is_dir():
            pytest.skip("needs the book repo's lab simulation (set LAB_SIM_ROOT)")
        env = {**env, "LAB_SIM_ROOT": str(lab_sim_root())}
    if (REPO / "contrib" / cid / "freeze.yaml").exists():
        pytest.skip("already frozen; scratch git has no freeze commit")
    for step in (["freeze", cid, "--commit"], ["run", cid], ["export", cid]):
        r = workbench(wb, env, *step)
        assert r.returncode == 0, (step, r.stdout, r.stderr)
    sketch = reg / "sketches" / cid
    for name in ("attempt.yaml", "freeze.yaml", "freeze-cases.jsonl", "trials.jsonl", "score-table.csv"):
        assert (sketch / name).exists(), name
    assert "score table matches the table derived from the frozen cases and trials" in r.stdout, r.stdout


def test_run_refuses_changes_after_freeze(trees):
    wb, _, env = trees
    cid = EXAMPLES[0]
    assert workbench(wb, env, "freeze", cid, "--commit").returncode == 0
    with open(wb / "contrib" / cid / "episodes.yaml", "a", encoding="utf-8") as f:
        f.write("# edited after the freeze\n")
    r = workbench(wb, env, "run", cid)
    assert r.returncode != 0 and "uncommitted changes" in r.stderr
    subprocess.run(["git", "commit", "-qam", "edit"], cwd=wb, env=env, check=True)
    r = workbench(wb, env, "run", cid)
    assert r.returncode != 0 and "changed since the freeze" in r.stderr
    r = workbench(wb, env, "freeze", cid)
    assert r.returncode != 0 and "already frozen" in r.stderr


def test_freeze_needs_clean_tree(trees):
    wb, _, env = trees
    cid = EXAMPLES[0]
    (wb / "contrib" / cid / "notes.txt").write_text("draft\n", encoding="utf-8")
    r = workbench(wb, env, "freeze", cid)
    assert r.returncode != 0 and "commit first" in r.stderr


@pytest.mark.parametrize("kind", ["inspect", "custom"])
def test_new_scaffold_freezes(trees, kind):
    wb, reg, env = trees
    r = workbench(wb, env, "new", "--market", "market-04", "--submitter", "tester", "--slug", f"new-{kind}",
                  "--type", kind)
    assert r.returncode == 0, r.stderr
    cid = next(p.name for p in (wb / "contrib").iterdir() if p.name.startswith("tester-"))
    subprocess.run(["git", "add", "-A"], cwd=wb, env=env, check=True)
    subprocess.run(["git", "commit", "-qm", "new"], cwd=wb, env=env, check=True)
    for step in (["freeze", cid, "--commit"], ["run", cid], ["export", cid]):
        r = workbench(wb, env, *step)
        assert r.returncode == 0, (step, r.stdout, r.stderr)
