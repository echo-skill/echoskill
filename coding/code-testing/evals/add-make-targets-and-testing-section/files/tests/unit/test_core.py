from ledger import core


def test_balance_is_zero_for_fresh_ledger():
    assert core.balance() == 0.0


def test_recorded_entries_sum_to_balance():
    core.record("groceries", 42.10)
    core.record("refund", -2.10)
    assert [e["label"] for e in core.entries()] == ["groceries", "refund"]
    assert core.balance() == 40.0
