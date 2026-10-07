"""workbench: start, freeze, run, and export a contribution.

  workbench new --market market-04 --submitter you --slug name [--type inspect|custom]
  workbench freeze <id> [--commit] [--registry PATH]
  workbench run <id>
  workbench export <id> [--registry PATH] [--log FILE] [--url URL] [--force]

The freeze discipline: `freeze` needs a clean tree, writes freeze-cases.jsonl and freeze.yaml (with the
current commit as the method's code), and with --commit commits them and tags freeze/<id>. `run` refuses
unless the freeze files are committed and nothing the run depends on changed since that commit.
`export` writes registry sketches/<id>/ and prints the registry's dry run.
"""

import argparse
import datetime as dt
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from . import contribution as contrib_mod
from . import gitutil, registry
from .markets import get as get_market

TEMPLATES = "templates"


def _now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cmd_new(repo, market, submitter, slug, kind):
    get_market(market)
    cid = f"{submitter}-{dt.date.today().isoformat()}-{slug}"
    if not contrib_mod.ID.match(cid):
        raise SystemExit(f"{cid}: submitter and slug are lowercase [a-z0-9-]")
    source = repo / TEMPLATES / market / kind
    if not source.is_dir():
        raise SystemExit(f"no {kind} template for {market} yet; copy an example from contrib/ instead")
    target = repo / "contrib" / cid
    if target.exists():
        raise SystemExit(f"contrib/{cid} already exists")
    shutil.copytree(source, target)
    for path in target.rglob("*"):
        if path.is_file() and path.suffix in (".yaml", ".py", ".md"):
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace("{{id}}", cid).replace("{{submitter}}", submitter), encoding="utf-8")
    print(f"created contrib/{cid} ({kind}). Edit episodes.yaml and contribution.yaml, commit, then "
          f"`workbench freeze {cid} --commit`.")
    return 0


def _freeze_paths(c):
    return [c.path / contrib_mod.FREEZE, c.path / contrib_mod.CASES]


def cmd_freeze(repo, cid, commit, registry_path):
    c = contrib_mod.load(repo, cid)
    market = get_market(c.market)
    rel = c.path.relative_to(repo)
    if any(p.exists() for p in _freeze_paths(c)):
        raise SystemExit(f"{rel} is already frozen; a new freeze is a new contribution (new id)")
    dirty = gitutil.dirty(repo, "src", str(rel))
    if dirty:
        raise SystemExit(f"commit first; freeze records the current commit as the method's code:\n{dirty}")
    reg = registry.locate(registry_path, repo)
    cases_path = c.path / contrib_mod.CASES
    cases_path.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in market.cases(c)), encoding="utf-8")
    registry.validator(reg, "hash-cases", cases_path, capture=True)
    code_commit = gitutil.head(repo)
    method = {"description": c.description or f"Contribution {cid}"}
    url = gitutil.https_remote(repo)
    if url:
        method["code"] = {"url": f"{url}/tree/{code_commit}/{rel}", "commit": code_commit}
    else:
        print("note: no https origin remote, so freeze.yaml names no code URL")
    scorer = market.SCORER if c.type == "inspect" else c.raw.get("scorer")
    if not scorer or not scorer.get("name") or not scorer.get("version"):
        raise SystemExit("a custom contribution names its scorer (name, version) in contribution.yaml")
    freeze = {"frozenAt": _now(), "method": method,
              "scorer": {k: scorer[k] for k in ("name", "version", "description") if k in scorer}}
    (c.path / contrib_mod.FREEZE).write_text(yaml.safe_dump(freeze, sort_keys=False, width=100), encoding="utf-8")
    print(f"froze {rel}: {sum(1 for _ in cases_path.open())} cases at {freeze['frozenAt']}, code {code_commit[:12]}")
    if commit:
        gitutil.git(repo, "add", *map(str, _freeze_paths(c)))
        gitutil.git(repo, "commit", "-m", f"Freeze {cid}")
        gitutil.git(repo, "tag", f"freeze/{cid}")
        print(f"committed and tagged freeze/{cid}; push the tag to make the freeze public before running")
    else:
        print(f"now commit {contrib_mod.FREEZE} and {contrib_mod.CASES} (and tag freeze/{cid}) before running")
    return 0


def _check_frozen(repo, c):
    rel = c.path.relative_to(repo)
    for p in _freeze_paths(c):
        if not gitutil.tracked(repo, p):
            raise SystemExit(f"{p.relative_to(repo)} is not committed; run `workbench freeze {c.id} --commit`")
    freeze = yaml.safe_load((c.path / contrib_mod.FREEZE).read_text(encoding="utf-8"))
    excludes = [f":(exclude){rel}/{contrib_mod.RUNS}"]
    dirty = gitutil.dirty(repo, "src", str(rel), *excludes)
    if dirty:
        raise SystemExit(f"uncommitted changes; the run must use exactly the frozen code:\n{dirty}")
    code = (freeze["method"].get("code") or {}).get("commit")
    if code:
        changed = gitutil.changed_since(repo, code, "src", str(rel), *excludes,
                                        *(f":(exclude){p.relative_to(repo)}" for p in _freeze_paths(c)))
        if changed:
            raise SystemExit(f"changed since the freeze at {code[:12]}; freeze a new contribution instead:\n{changed}")
    return freeze


def cmd_run(repo, cid):
    c = contrib_mod.load(repo, cid)
    _check_frozen(repo, c)
    c.runs.mkdir(exist_ok=True)
    if c.type == "inspect":
        from inspect_ai import eval as inspect_eval
        model = c.raw.get("model")
        if not model:
            raise SystemExit("contribution.yaml model: the Inspect model id of the system under test")
        # Inspect resolves task files relative to the working directory (absolute paths fail on Python 3.14).
        cwd = os.getcwd()
        os.chdir(c.path)
        try:
            logs = inspect_eval("task.py", model=model, log_dir=str(c.runs), display="none",
                                **(c.raw.get("eval_args") or {}))
        finally:
            os.chdir(cwd)
        status = [log.status for log in logs]
        print(f"wrote {', '.join(log.location for log in logs)} ({', '.join(status)})")
        return 0 if all(s == "success" for s in status) else 1
    env = {**os.environ, "WORKBENCH_RUNS": str(c.runs)}
    argv = shlex.split(c.raw["run"])
    if argv and argv[0] in ("python", "python3"):
        argv[0] = sys.executable  # the workbench's interpreter, so the run sees the same packages
    return subprocess.run(argv, cwd=c.path, env=env).returncode


def cmd_export(repo, cid, registry_path, log, url, force):
    c = contrib_mod.load(repo, cid)
    market = get_market(c.market)
    freeze = _check_frozen(repo, c)
    reg = registry.locate(registry_path, repo)
    log = Path(log).resolve() if log else c.latest_log()
    if (reg / "submitted-attempts" / cid).exists():
        raise SystemExit(f"{cid} is already submitted in the registry")
    sketch = reg / "sketches" / cid
    if sketch.exists():
        if not force:
            raise SystemExit(f"sketches/{cid} exists in the registry; pass --force to replace it")
        shutil.rmtree(sketch)
    sketch.mkdir(parents=True)
    attempt = {"id": cid, "market": c.market, "contractVersion": market.CONTRACT_VERSION, "attemptType": "run",
               "submitter": c.submitter, "filedAt": c.filed_at, "methodFreezeAt": freeze["frozenAt"],
               "systems": [{"name": c.system["name"], "version": c.system["version"]}],
               "notes": f"Exported from ai-safety-claims-workbench contrib/{cid} ({c.type})."}
    (sketch / "attempt.yaml").write_text(yaml.safe_dump(attempt, sort_keys=False, width=100), encoding="utf-8")
    for p in _freeze_paths(c):
        shutil.copy(p, sketch / p.name)
    cases, trials = sketch / contrib_mod.CASES, sketch / "trials.jsonl"
    if c.type == "inspect":
        registry.validator(reg, "import-inspect", log, "--cases", cases, "--out", trials,
                           "--system-version", c.system["version"])
        fmt = "Inspect log"
    else:
        subprocess.run([sys.executable, "-I", str(c.path / c.raw["adapter"]), str(log), str(cases), str(trials)],
                       cwd=c.path, check=True)
        fmt = c.raw.get("raw_log_format", "custom raw log")
    raw_args = ["raw-log", log, "--attempt", sketch, "--format", fmt, "--update-attempt"]
    registry.validator(reg, *(raw_args + (["--url", url] if url else [])))
    registry.validator(reg, "derive-table", sketch)
    print(f"\nexported to {sketch}\n", flush=True)
    registry.validator(reg, "dry-run", sketch, check=False)
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="workbench", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new")
    n.add_argument("--market", required=True)
    n.add_argument("--submitter", required=True)
    n.add_argument("--slug", required=True)
    n.add_argument("--type", default="inspect", choices=["inspect", "custom"])
    f = sub.add_parser("freeze")
    f.add_argument("id")
    f.add_argument("--commit", action="store_true")
    f.add_argument("--registry")
    r = sub.add_parser("run")
    r.add_argument("id")
    e = sub.add_parser("export")
    e.add_argument("id")
    e.add_argument("--registry")
    e.add_argument("--log")
    e.add_argument("--url", help="where the full raw log is published (needed above the registry's local limit)")
    e.add_argument("--force", action="store_true")
    args = p.parse_args(argv)
    repo = gitutil.toplevel()
    if args.cmd == "new":
        return cmd_new(repo, args.market, args.submitter, args.slug, args.type)
    if args.cmd == "freeze":
        return cmd_freeze(repo, args.id, args.commit, args.registry)
    if args.cmd == "run":
        return cmd_run(repo, args.id)
    return cmd_export(repo, args.id, args.registry, args.log, args.url, args.force)


if __name__ == "__main__":
    sys.exit(main())
