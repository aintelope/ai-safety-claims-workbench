"""The method run: intervention-supported UAD on every frozen system. No scoring here.

For each frozen case the system is rebuilt from its scenario name, parameters, and seed only. In the lab
simulation, `LabConfig.units` is both the oracle ground truth and part of the world's wiring (who chairs
a committee, who a DM or file handoff goes to), and the method intervenes by rerunning the system, so the
config has to carry it. What must not happen is the method reading it: `GuardedConfig` raises if any
module under lab_sim.oracle_only (the method's code) reads `units` or `resolved_units`; the world
(world_visible, agent_visible) still can. A tripwire, not a proof: a copy made inside the method would
escape it, which a grep of the method modules for `units` rules out at the pinned commit.

The method's output for a system is the discovered unit containing the focal actor (the cut), with a
certificate:
  complete  the cut, and no actor outside the established candidate graph shows unexplained compensation
  partial   the cut, but some actor shows intrinsic compensation the method cannot attribute (LS-28
            diagnostics), so the boundary is not claimed complete
  abstain   the episode or the discovery failed
Raw log: JSON lines under $WORKBENCH_RUNS; a header line, then one line per system.
"""

import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

from lab import check_pinned, lab_sim_path, pin

HERE = Path(__file__).parent
LAB = lab_sim_path()
sys.path.insert(0, str(LAB))
from lab_sim.harness import ecology  # noqa: E402
from lab_sim.harness.isolate import MockIsolate  # noqa: E402
from lab_sim.oracle_only import uad_intervention  # noqa: E402
from lab_sim.world_visible.config import CODE_VERSION, LabConfig  # noqa: E402
from lab_sim.world_visible.world import run_episode  # noqa: E402

FACTORIES = {
    "dm_pair": ecology.dm_pair_config,
    "build_loop": ecology.build_loop_config,
    "committee_informal_chatter": ecology.committee_with_informal_chatter_config,
    "committee_file": ecology.committee_config,
    "covert_file_handoff": ecology.covert_file_handoff_config,
    "shared_slot": ecology.shared_slot_config,
    "serial_pipeline_no_unit": ecology.serial_pipeline_no_unit_config,
}
FROZEN_INPUTS = ("case_id", "scenario", "params", "seed", "focal")  # all the method may read from a case


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="microseconds")


class GuardedConfig(LabConfig):
    """LabConfig that refuses to show the ground truth to the method's modules."""

    def __getattribute__(self, name):
        if name in ("units", "resolved_units"):
            caller = sys._getframe(1).f_globals.get("__name__", "")
            if caller.startswith("lab_sim.oracle_only"):
                raise RuntimeError(f"the method ({caller}) read LabConfig.{name}")
        return object.__getattribute__(self, name)


def discover(case):
    cfg = GuardedConfig(**vars(FACTORIES[case["scenario"]](**case["params"])))
    result = run_episode(cfg, seed=case["seed"], backend=MockIsolate())
    diagnostics = {}
    units = uad_intervention.discovered_units_intervention(result, cfg, case["seed"], ablation_diagnostics=diagnostics)
    cut = sorted(next((m for m in units.values() if case["focal"] in m), (case["focal"],)))
    unexplained = sorted({a for labels in diagnostics.values() for a, label in labels.items()
                          if label == "intrinsic_unexplained"})
    return {"partition": {k: sorted(v) for k, v in sorted(units.items())}, "diagnostics": diagnostics,
            "unexplained": unexplained, "cut": cut, "certificate": "partial" if unexplained else "complete"}


def main():
    commit = check_pinned(LAB)
    if CODE_VERSION != pin()["code_version"]:
        raise SystemExit(f"lab_sim CODE_VERSION {CODE_VERSION} is not the pinned {pin()['code_version']}")
    runs = Path(os.environ.get("WORKBENCH_RUNS", HERE / "runs"))
    runs.mkdir(parents=True, exist_ok=True)
    cases = [json.loads(line) for line in (HERE / "freeze-cases.jsonl").read_text(encoding="utf-8").splitlines() if line]
    out = runs / f"uad-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}.jsonl"
    with open(out, "w", encoding="utf-8") as log:
        log.write(json.dumps({"header": True, "lab_sim_commit": commit, "code_version": CODE_VERSION,
                              "method": "uad_intervention.discovered_units_intervention",
                              "defaults": {"min_compensation": uad_intervention.DEFAULT_MIN_COMPENSATION,
                                           "intervention_tick": uad_intervention.DEFAULT_INTERVENTION_TICK,
                                           "probe_budget": uad_intervention.DEFAULT_PROBE_BUDGET}}) + "\n")
        for i, case in enumerate(cases, start=1):
            visible = {k: case[k] for k in FROZEN_INPUTS}
            started, t0 = now(), time.time()
            try:
                out_fields = discover(visible)
            except Exception as e:  # a failed episode is an abstention, recorded as such
                out_fields = {"cut": [], "certificate": "abstain", "error": repr(e)}
            log.write(json.dumps({"case_id": case["case_id"], "started_at": started, "finished_at": now(),
                                  "seconds": round(time.time() - t0, 3), **out_fields}) + "\n")
            print(f"[{i}/{len(cases)}] {case['case_id']}: {out_fields['certificate']} {out_fields['cut']}", flush=True)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
