"""Entry point for running the MCP server as a module: python -m admob_mcp"""
from admob_mcp.server import mcp

mcp.run(transport="stdio")

