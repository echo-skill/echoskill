"""stdio MCP server over tinykv.store. Tool descriptions are what an agent sees."""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import store

mcp = FastMCP("tinykv")


@mcp.tool()
def put(k: str, v: str) -> dict:
    """Store a value."""
    return store.put(k, v)


@mcp.tool()
def get(k: str) -> str | None:
    """Read a value."""
    return store.get(k)


@mcp.tool()
def remove(k: str) -> bool:
    """Delete."""
    return store.remove(k)


@mcp.tool()
def list_keys(prefix: str = "") -> list[str]:
    """List keys."""
    return store.list_keys(prefix)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
