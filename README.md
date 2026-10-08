# ai-safety-claims-workbench

**Do you have an idea, concept, or prototype for solving part of an alignment problem?** Sketch it here,
run it, and see exactly how far it is from a result that counts.

The [ai-safety-claims](https://github.com/aintelope/ai-safety-claims) registry holds frozen **market
contracts** for catalog Markets 1–13 and 15–18 ([full contract table](https://github.com/aintelope/ai-safety-claims#where-the-contracts-come-from)).
Each states the bar a published method must meet by its evidence cutoff. The registry is not yet a
resolution source until an independent host tags `snapshot-0`. Market 14 and draft Markets 19–21 are
outside this catalog.

This workbench exports registry **sketches** for any frozen catalog contract. **Workbench scaffolds**
(case lists and validators wired in `src/workbench/markets/`) exist for five markets today; the rest use
`workbench new --market market-NN --type custom` against the contract YAML in your registry checkout:

**Scaffolded markets (examples in `contrib/`):**

- **[Market 1](https://github.com/aintelope/ai-safety-claims/blob/main/market-contracts/market-01/contract-v2.yaml): where does control reside?**
  Given an AI system you have never seen, can your method name the components that jointly control its
  behavior: the model, its memory, planner, tools, or other agents?
- **[Market 4](https://github.com/aintelope/ai-safety-claims/blob/main/market-contracts/market-04/contract-v3.yaml): do corrections change the
  system?** When an authorized person corrects an AI system, does its later behavior change, and does
  the change survive a context reset, while fake or unauthorized corrections fail?
- **[Market 8](https://github.com/aintelope/ai-safety-claims/blob/main/market-contracts/market-08/contract-v2.yaml): can an audit detect missing control routes?**
  Custom wraps only (no Inspect template); see `contrib/zarncke-2026-10-08-orbit-swe-monitor`.
- **[Market 11](https://github.com/aintelope/ai-safety-claims/blob/main/market-contracts/market-11/contract-v1.yaml): coordination without communication?**
  Custom wraps; see `contrib/zarncke-2026-10-08-lab-sim-s7-hidden-coord`.
- **[Market 12](https://github.com/aintelope/ai-safety-claims/blob/main/market-contracts/market-12/contract-v1.yaml): do safety proxies track the real thing?**
  Custom wraps; see `contrib/zarncke-2026-10-08-et4-a0-proxy`.

What you get from building toward any catalog market here:

- **Start small, without penalty.** A sketch can be a ten-episode pilot on a mock model. Sketches never count toward a NO; only a complete, qualifying attempt can resolve a question.
- **A precise gap list.** Every export runs the registry's checks and lists what is still missing (sample sizes, coverage, freeze order, adversarial testing), with your current values against the thresholds.
- **A dated, checkable record.** Use a proper scientific pre-registration process by default. Freezing commits and tags your method and cases before you see any result, so your claim is on record and others can check it was not tuned afterwards.
- **Evidence for the forecasts.** Sketches show where a question stands; a qualifying attempt is what a market resolves on.

**Try it in 15 minutes, no API key:** copy a Market 4 example, run it on Inspect's mock model, and read the gap list ([Workflow](#workflow)). For another catalog contract, pick it from the [registry table](https://github.com/aintelope/ai-safety-claims#where-the-contracts-come-from) and use `--type custom`, or open a [registry issue](https://github.com/aintelope/ai-safety-claims/issues) if the contract needs a change.

> Status: scaffold. Market 4 has an Inspect scaffold; Market 1 has a systems.yaml scaffold; Markets 8, 11,
> and 12 have cases.yaml scaffolds for custom wraps. Other frozen catalog contracts have no template yet (`workbench new`
> still defaults to Market 4). Everything under `contrib/example-*` is fictional and runs on Inspect's mock
> model or a scripted toy. The registry is not yet a resolution source.

## How it fits together

Write an evaluation here, freeze it, run it, and export it as a registry **sketch** with its evidence:
frozen cases, per-trial records, the raw log, and the score table derived from them. The registry stays
data-only and never runs code from here; it checks what you export.

## Two kinds of contribution

Each contribution is one folder, `contrib/{submitter}-{YYYY-MM-DD}-{slug}/`, named like the registry
sketch it becomes.

- **Inspect (the default).** An [Inspect](https://inspect.aisi.org.uk/) task built on the market
  scaffold: `episodes.yaml` (the cases), `contribution.yaml` (system, model), and a two-line `task.py`.
  The adapter is the standard itself: samples carry `metadata.case_id` and the scorer's metadata holds the
  market's result fields, so the registry's `validator import-inspect` turns the Inspect log into
  `trials.jsonl` with nothing contribution-specific. Swap in your own solver or scorer in `task.py` if the
  protocol doesn't fit. Examples: `example-jam-2026-10-07-email-approval`,
  `example-uni-2026-10-07-pressure-after-correction`.
- **Custom (self-contained).** Any entrypoint (`run` in `contribution.yaml`: a script, an agent, a
  container) that reads the frozen cases and writes a raw log in its own format, plus `adapter`, a script
  that turns one raw log into `trials.jsonl`. Examples: `example-lab-2026-10-07-scripted-assistant`
  (Market 4), `zarncke-2026-10-07-lab-sim-intervention-uad` (Market 1: lab-simulation UAD; needs the book
  repo), `zarncke-2026-10-08-orbit-swe-monitor` (Market 8: published Orbit Table 13, no model calls),
  `zarncke-2026-10-08-lab-sim-s7-hidden-coord` (Market 11: S7 blind battery excerpt), and
  `zarncke-2026-10-08-et4-a0-proxy` (Market 12: ET-4 A0 proxy inversion).

### External sources (wraps)

Many custom contributions **wrap published work** instead of calling a model. Two patterns both work; pick by size and who must reconstruct the run.

**Self-contained (default for small sketches).** Pin upstream in `contribution.yaml` (`repo`, `commit`, optional `source_sha256`) and vendor the bytes the wrap reads under `source/` (or build them in `run.py` from a pinned excerpt). `run` writes a raw log; `export` copies that log into the registry sketch. The validator never fetches GitHub — it checks the exported `raw-log/`, `trials.jsonl`, and score table. Offline replay and CI stay simple; Dietz gold JSON, Orbit table excerpts, and ET-4/S7 JSON slices use this pattern.

**External URL + content hash (preferred when logs are large).** Keep only the pin in the contribution: stable URL or `git` commit + paths, plus SHA-256 (or a manifest hash) of the artifact the adapter scores. `run` may fetch at run time; **`export` must still ship whatever the registry needs to verify** — typically a raw log derived from that artifact, with the hash recorded in `attempt.yaml` / `contribution.yaml` and echoed in the log header. Do not rely on “re-run our fetch script” as the only evidence unless that script and pin are part of the frozen method. For qualifying attempts, `freezeEvidence` in the registry should name the public source and hash.

Sketches may stay fully self-contained even when a qualifying attempt would use URL + hash only; moving from sketch to submit is a good time to drop vendored blobs if they are huge.

## Workflow

```bash
python3 -m venv .venv && .venv/bin/pip install -e '.[test]'
# the registry checkout next to this one (or --registry / WORKBENCH_REGISTRY)
git clone git@github.com:aintelope/ai-safety-claims.git ../ai-safety-claims

.venv/bin/workbench new --market market-04 --submitter you --slug short-name [--type custom]
# edit contrib/<id>/episodes.yaml and contribution.yaml, then commit
.venv/bin/workbench freeze <id> --commit   # freeze-cases.jsonl + freeze.yaml, committed, tagged freeze/<id>
git push origin freeze/<id>                # makes the freeze public before any result exists
.venv/bin/workbench run <id>               # Inspect log (or your raw log) under contrib/<id>/runs/
.venv/bin/workbench export <id>            # ../ai-safety-claims/sketches/<id>/ and the registry's dry run
```

Then open a pull request on the registry with the sketch. Its dry run lists what is still missing for a
qualifying attempt (sample sizes, adversarial route, publication).

## The freeze

- `freeze` needs a clean tree. It writes every case (setup, correction, probe, target, check rule) to
  `freeze-cases.jsonl` with its hash, and `freeze.yaml` with the time, the current commit as the method's
  code, and the scorer. A frozen contribution is never re-frozen: change it and you have a new one.
- `run` refuses if the freeze files are not committed, if anything under `src/` or the contribution
  changed since the frozen commit, or if there are uncommitted changes. Inspect tasks read the frozen
  cases, not `episodes.yaml`.
- Every trial starts after `frozenAt`; the registry checks that, and that each trial names a frozen case
  by its hash.

## Layout

```text
src/workbench/            CLI (new, freeze, run, export), git checks, registry calls
src/workbench/markets/    case/Inspect scaffolds (Markets 1, 4, 8, 11, 12 today)
templates/<market>/       what `workbench new` copies: inspect/ (default) and custom/
contrib/                  contributions, one folder each
tests/                    end to end against a scratch copy of the registry
```

## License

Apache-2.0. By opening a pull request you license your contribution under it and confirm you may.
