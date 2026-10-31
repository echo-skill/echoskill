"""Hits the live rates API. Requires LEDGER_RATES_TOKEN and network access."""
from ledger import core


def test_live_rate_is_positive():
    assert core.live_rate("EUR") > 0
