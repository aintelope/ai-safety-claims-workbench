# {{id}}

Inspect contribution for Market 4. Edit `episodes.yaml` and `contribution.yaml`, commit, then:

```bash
workbench freeze {{id}} --commit    # freeze-cases.jsonl + freeze.yaml, committed and tagged
workbench run {{id}}                # Inspect log under runs/
workbench export {{id}}             # registry sketches/{{id}}/ and its dry run
```
