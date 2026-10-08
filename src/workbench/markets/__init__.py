"""Market scaffolds. Each module turns a contribution's case file into frozen cases (`cases`), names the
registry contract version it targets, and, for Inspect contributions, provides the task pieces."""

from . import market_01, market_04, market_08, market_11, market_12

MARKETS = {
    "market-01": market_01,
    "market-04": market_04,
    "market-08": market_08,
    "market-11": market_11,
    "market-12": market_12,
}


def get(market):
    if market not in MARKETS:
        raise SystemExit(f"no scaffold for {market} yet (have: {', '.join(MARKETS)})")
    return MARKETS[market]
