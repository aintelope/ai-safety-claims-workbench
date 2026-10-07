# example-jam-2026-10-07-email-approval

Example (fictional, mock model): does an office assistant take up authorized corrections about sending email, keep them after a context reset, and ignore unsigned, unauthorized, and rerouted ones? One episode per required case and sham type.

Inspect contribution for Market 4. Edit `episodes.yaml` and `contribution.yaml`, commit, then:

```bash
workbench freeze example-jam-2026-10-07-email-approval --commit    # freeze-cases.jsonl + freeze.yaml, committed and tagged
workbench run example-jam-2026-10-07-email-approval                # Inspect log under runs/
workbench export example-jam-2026-10-07-email-approval             # registry sketches/example-jam-2026-10-07-email-approval/ and its dry run
```
