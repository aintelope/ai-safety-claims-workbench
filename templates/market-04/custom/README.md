# {{id}}

Self-contained Market 4 contribution: `run.py` is the whole evaluation (no Inspect), with its own raw-log
format; `adapter.py` turns a raw log into the registry's `trials.jsonl`. Replace the scripted assistant
with your system; keep the two contracts (frozen cases in, raw log out; raw log in, trials out).

```bash
workbench freeze {{id}} --commit
workbench run {{id}}       # runs `run` from contribution.yaml
workbench export {{id}}    # runs the adapter, then the registry's checks
```
