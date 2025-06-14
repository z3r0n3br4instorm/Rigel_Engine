from typing import List
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Rigel Tool", port=8001)


@mcp.tool()
def current_time() -> str:
    """Returns the current time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    mcp.run(transport="sse")