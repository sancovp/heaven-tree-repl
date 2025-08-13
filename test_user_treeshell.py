#!/usr/bin/env python3

import sys
import asyncio
sys.path.insert(0, '/home/GOD/heaven-tree-repl')

from heaven_tree_repl.shells import UserTreeShell
from heaven_tree_repl import render_response

async def main():
    shell = UserTreeShell({})
    
    # Get command from command line argument
    command = sys.argv[1]
    result = await shell.handle_command(command)
    rendered = render_response(result)
    print(rendered)

if __name__ == "__main__":
    asyncio.run(main())