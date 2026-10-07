# AGENTS.md

Guidance for AI agents working in this repository. Read `README.md` first.

## Setup and checks

```bash
python3 -m venv .venv && .venv/bin/pip install -e '.[test]'
.venv/bin/pytest -q    # needs ../ai-safety-claims (or WORKBENCH_REGISTRY); the Market 1 sketch also
                       # needs ../towards-asi-alignment (or LAB_SIM_ROOT) and is skipped without it
```

Use the mock model (`mockllm/model`) unless the user asks for a real model and has provided keys.

## Rules

- **Never edit a frozen contribution.** Once `contrib/<id>/freeze.yaml` exists, nothing in that folder
  or under `src/` that it depends on may change for that contribution; a change is a new contribution
  with a new id. Do not re-freeze, rewrite, or delete `freeze.yaml`, `freeze-cases.jsonl`, or
  `freeze/<id>` tags.
- **Follow the freeze order:** commit the contribution, `workbench freeze <id> --commit`, push the tag,
  then `run` and `export`. Never run before the freeze is committed.
- **Method code never reads the ground truth.** Frozen component lists, targets, and checks are for the
  scorer; keep the method and the scorer in separate steps.
- **Report results as they come out.** Do not change a method, threshold, or case after seeing a
  result; misses and failures are findings, not bugs to tune away.
- **Do not reimplement registry logic.** Hashing, Inspect extraction, raw-log handling, table derivation,
  and the dry run are the registry's `python -m validator` commands; call them (`src/workbench/registry.py`).
- **Examples are fictional.** `contrib/example-*` runs on the mock model or a scripted toy; never present
  their numbers as evidence about a real system.
- Commit or push only when the user asks.
