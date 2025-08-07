#!/usr/bin/env python3
"""
MCP Server entry point for heaven-tree-repl.
Allows running the server with: python -m heaven_tree_repl.mcp_server
"""

import sys
import asyncio
from .server import serve

if __name__ == "__main__":
    asyncio.run(serve())