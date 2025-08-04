"""
TreeShell MCP Server
Tree navigation REPL for AI agents using HEAVEN framework
"""
from .server import serve


def main():
    """Main entry point for TreeShell MCP Server"""
    import asyncio
    asyncio.run(serve())


if __name__ == "__main__":
    main()