from tinykv import store


def test_put_then_get_round_trips_and_reports_replacement():
    assert store.put("color", "red") == {"key": "color", "value": "red", "replaced": False}
    assert store.put("color", "blue")["replaced"] is True
    assert store.get("color") == "blue"


def test_remove_deletes_only_the_named_key():
    store.put("a", "1"); store.put("ab", "2")
    assert store.remove("a") is True
    assert store.list_keys() == ["ab"]
    assert store.remove("a") is False
