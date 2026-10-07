"""Git checks behind the freeze discipline: freeze on a clean tree, run only code that matches the freeze."""

import subprocess
from pathlib import Path


def git(repo, *args, check=True):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=check).stdout.strip()


def toplevel(start="."):
    try:
        return Path(git(start, "rev-parse", "--show-toplevel"))
    except subprocess.CalledProcessError:
        raise SystemExit("run the workbench inside its git checkout")


def head(repo):
    return git(repo, "rev-parse", "HEAD")


def dirty(repo, *paths):
    """Uncommitted changes (including untracked files) under paths."""
    return git(repo, "status", "--porcelain", "--untracked-files=all", "--", *paths)


def changed_since(repo, commit, *paths):
    """Files under paths that differ between commit and HEAD."""
    return git(repo, "diff", "--name-only", commit, "HEAD", "--", *paths)


def tracked(repo, path):
    return subprocess.run(["git", "ls-files", "--error-unmatch", str(path)], cwd=repo,
                          capture_output=True).returncode == 0


def https_remote(repo):
    """origin as an https URL (git@github.com:org/x.git -> https://github.com/org/x), or None."""
    url = git(repo, "remote", "get-url", "origin", check=False)
    if not url:
        return None
    if url.startswith("git@"):
        host, path = url[4:].split(":", 1)
        url = f"https://{host}/{path}"
    return url.removesuffix(".git") if url.startswith("http") else None
