# example-uni-2026-10-07-pressure-after-correction

Example (fictional, mock model): a coding agent receives a correction, then pressure to return to the old behavior before the probe. Shows the optional pressure turn.

Inspect contribution for Market 4. Edit `episodes.yaml` and `contribution.yaml`, commit, then:

```bash
workbench freeze example-uni-2026-10-07-pressure-after-correction --commit    # freeze-cases.jsonl + freeze.yaml, committed and tagged
workbench run example-uni-2026-10-07-pressure-after-correction                # Inspect log under runs/
workbench export example-uni-2026-10-07-pressure-after-correction             # registry sketches/example-uni-2026-10-07-pressure-after-correction/ and its dry run
```
