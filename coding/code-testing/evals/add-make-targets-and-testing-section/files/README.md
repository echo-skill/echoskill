# ledger

A tiny personal ledger. Entries are stored as JSON lines under the
directory named by `LEDGER_DIR` (default `~/.local/share/ledger`).

## Install

    pip install -e .

## Usage

```python
from ledger import core
core.record("groceries", 42.10)
core.balance()
```

Live exchange rates (optional) need `LEDGER_RATES_TOKEN` set.
