import json
from unittest.mock import patch, mock_open, MagicMock

from notes import core


@patch("notes.core.Path.mkdir")
@patch("notes.core.Path.exists", return_value=False)
@patch("notes.core.Path.write_text")
def test_add_note_writes_json(mock_write, mock_exists, mock_mkdir):
    note = core.add_note("a1", "hello")
    assert note["id"] == "a1"
    mock_write.assert_called_once()
    written = json.loads(mock_write.call_args[0][0])
    assert written["text"] == "hello"


@patch("notes.core.Path.read_text", return_value='{"id": "a1", "text": "x", "tags": []}')
def test_get_note_parses_json(mock_read):
    assert core.get_note("a1")["text"] == "x"
    mock_read.assert_called_once()


@patch("notes.core.Path.exists", return_value=False)
def test_list_notes_returns_empty_when_dir_missing(mock_exists):
    assert core.list_notes() == []


@patch("notes.core.get_note", return_value={"id": "a1", "text": "x", "tags": []})
@patch("notes.core.Path.write_text")
def test_tag_note_appends_tag(mock_write, mock_get):
    note = core.tag_note("a1", "urgent")
    assert "urgent" in note["tags"]
    mock_write.assert_called_once()
