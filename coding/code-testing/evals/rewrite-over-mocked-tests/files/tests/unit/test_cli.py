from unittest.mock import patch

from notes import cli


@patch("notes.cli.core.add_note", return_value={"id": "a1", "text": "hello", "tags": []})
def test_add_calls_core(mock_add):
    assert cli.main(["add", "a1", "hello"]) == 0
    mock_add.assert_called_once_with("a1", "hello")


@patch("notes.cli.core.tag_note", return_value={"id": "a1", "text": "hello", "tags": ["urgent"]})
def test_tag_calls_core(mock_tag):
    assert cli.main(["tag", "a1", "urgent"]) == 0
    mock_tag.assert_called_once()


@patch("notes.cli.core.list_notes", return_value=[])
def test_list_calls_core(mock_list, capsys):
    assert cli.main(["list"]) == 0
    mock_list.assert_called_once()
