# Contributing

## Development setup

    make setup       # bootstrap .venv with the editable install and dev extras
    pytest           # run the unit tests

Or from a fresh clone:

    make test        # creates the venv and runs the unit tests

Unit tests are sociable: real code paths against a temp directory set
through `TALLY_DIR` (see `tests/unit/conftest.py`). No network, no
credentials, no mocks of our own modules.

## Layout

- `tally/core.py` — all behavior.
- `tally/cli.py` — thin argparse wrapper; parse, call core, print.
