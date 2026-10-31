from tally import core


def test_totals_are_empty_for_fresh_store():
    assert core.totals() == {}


def test_recording_same_name_twice_sums_counts():
    core.record("pushups", 10, when="2026-01-01")
    core.record("pushups", 5, when="2026-01-02")
    core.record("squats", 20, when="2026-01-02")
    assert core.totals() == {"pushups": 15, "squats": 20}
    assert [e["date"] for e in core.entries()] == ["2026-01-01", "2026-01-02", "2026-01-02"]
