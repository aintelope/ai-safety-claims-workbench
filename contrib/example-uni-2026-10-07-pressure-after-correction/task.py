"""Inspect task for this contribution: the Market 4 correction protocol over the frozen cases.

To change the protocol, pass your own pieces: correction_task(HERE, solver=..., scorer=...). Whatever
scorer you use, its Score.metadata must hold the result fields (genuine: uptake, persisted_after_reset;
sham: sham_succeeded), because that is what the registry's import-inspect reads.
"""

from pathlib import Path

from inspect_ai import task

from workbench.markets.market_04.task import correction_task

HERE = Path(__file__).parent


@task
def episodes():
    return correction_task(HERE)
