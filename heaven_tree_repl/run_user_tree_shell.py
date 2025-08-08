#!/usr/bin/env python3
"""
UserTreeShell command runner - Execute UserTreeShell commands from command line.
"""
import sys
import asyncio
from . import UserTreeShell
from .renderer import render_response


async def run_command(command: str = ""):
    """Run a single UserTreeShell command and return the result."""
    shell = UserTreeShell()
    result = await shell.handle_command(command)
    return result


async def main():
    """Main entry point for command-line UserTreeShell execution."""
    # Get command from command line args
    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
    else:
        command = ""  # Default to main menu
    
    try:
        result = await run_command(command)
        print(render_response(result))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())