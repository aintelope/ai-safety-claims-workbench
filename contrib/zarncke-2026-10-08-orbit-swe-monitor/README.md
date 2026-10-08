# zarncke-2026-10-08-orbit-swe-monitor

Market 8 **wrap sketch** of Orbit Table 13 (SWE-Bench multi-issue): two published collusion cells
(myopic LLM monitor, guardian agent) from arXiv:2609.33102v1. The wrap copies attack-success rates.
It does not map them onto `detected_or_refused` or `certified_sufficient`.

| File | Role |
|------|------|
| `source/table-13.txt` | Pinned excerpt of Table 13 |
| `run.py` | Writes raw log from frozen cases (no API calls) |
| `adapter.py` | Sets both Market 8 result flags false |

```bash
workbench freeze zarncke-2026-10-08-orbit-swe-monitor --commit
workbench run zarncke-2026-10-08-orbit-swe-monitor
workbench export zarncke-2026-10-08-orbit-swe-monitor
```

Why it stays a sketch: 2 cases (floors need 20 per family and 20 complete controls), no post-freeze
adversarial incomplete subset, no `adversarial-route.yaml`, no hidden suite, published table not an
access-audit method.
