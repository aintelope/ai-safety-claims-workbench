"""The registry checkout this workbench exports to. Hashing, Inspect extraction, table derivation, and the
dry run are the registry's own commands; the workbench calls them instead of reimplementing them."""

import os
import subprocess
import sys
from pathlib import Path


def locate(explicit=None, repo=None):
    """--registry, else $WORKBENCH_REGISTRY, else a sibling checkout named ai-safety-claims."""
    candidates = [explicit, os.environ.get("WORKBENCH_REGISTRY")]
    if repo is not None:
        candidates.append(Path(repo).parent / "ai-safety-claims")
    for c in candidates:
        if c and (Path(c) / "validator" / "__main__.py").exists():
            return Path(c).resolve()
    raise SystemExit("registry not found: pass --registry, set WORKBENCH_REGISTRY, or check out "
                     "aintelope/ai-safety-claims next to this repo")


def validator(registry, *args, check=True, capture=False):
    """Run `python -m validator <args>` in the registry with this interpreter."""
    result = subprocess.run([sys.executable, "-m", "validator", *map(str, args)], cwd=registry,
                            capture_output=capture, text=True)
    if check and result.returncode != 0:
        if capture:
            sys.stderr.write(result.stdout + result.stderr)
        raise SystemExit(f"registry command failed: validator {' '.join(map(str, args))}")
    return result
