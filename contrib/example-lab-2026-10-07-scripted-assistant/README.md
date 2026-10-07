# example-lab-2026-10-07-scripted-assistant

Example (fictional): the same episodes as example-jam-2026-10-07-email-approval, run by a self-contained script against a scripted assistant with persistent memory. Shows a custom contribution: own entrypoint, own raw-log format, and an adapter. A toy system: never sole evidence.

Self-contained Market 4 contribution: `run.py` is the whole evaluation (no Inspect), with its own raw-log
format; `adapter.py` turns a raw log into the registry's `trials.jsonl`. Replace the scripted assistant
with your system; keep the two contracts (frozen cases in, raw log out; raw log in, trials out).

```bash
workbench freeze example-lab-2026-10-07-scripted-assistant --commit
workbench run example-lab-2026-10-07-scripted-assistant       # runs `run` from contribution.yaml
workbench export example-lab-2026-10-07-scripted-assistant    # runs the adapter, then the registry's checks
```
