# tinykv

A tiny key/value store exposed as a stdio MCP server. Values are strings.
Data lives in one JSON file at `TINYKV_PATH` (default `~/.local/share/tinykv/data.json`).

Run the server:

    python -m tinykv            # or: tinykv-mcp

Tools: `put`, `get`, `remove`, `list_keys`.
