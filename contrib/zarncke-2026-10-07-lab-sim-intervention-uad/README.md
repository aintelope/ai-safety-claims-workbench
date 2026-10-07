# zarncke-2026-10-07-lab-sim-intervention-uad

Market 1 sketch: the lab simulation's intervention-supported unit discovery (book repo,
`experiments/lab-simulation`) on its own ecology scenarios, 7 scenarios × 8 seeds = 56 systems.

| File | Role | Reads the ground truth? |
|------|------|-------------------------|
| `build_systems.py` → `systems.yaml` | benchmark: scenarios, seeds, focal actor, frozen unit | yes (evaluator side) |
| `run.py` | method: rebuild each system, run UAD (a guard stops method code from reading `units`), log the cut and certificate | no |
| `adapter.py` | scorer: compare cuts with the frozen lists, write `trials.jsonl` | yes, after the run |
| `lab.py` | pins the book commit; `run.py` refuses any other or a modified `lab-simulation/` | |

```bash
python build_systems.py                      # only before the freeze; commit systems.yaml
workbench freeze zarncke-2026-10-07-lab-sim-intervention-uad --commit
workbench run zarncke-2026-10-07-lab-sim-intervention-uad
workbench export zarncke-2026-10-07-lab-sim-intervention-uad
```

Needs the book repo next to the workbench (or `LAB_SIM_ROOT`). Why it is a sketch and not an attempt:
simulated systems on the mock backend (toy-only), built by the method's author (not independently
constructed), not hidden (no challenge run), no adversarial subset built after the freeze, and no serious
adversarial route. The response statistic, minimum change, and no-effect range are declared, not yet
checked by intervention on the frozen units.
