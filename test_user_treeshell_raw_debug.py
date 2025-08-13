#!/usr/bin/env python3

import sys
import asyncio
import json
sys.path.insert(0, '/home/GOD/heaven-tree-repl')

from heaven_tree_repl.shells import UserTreeShell

async def main():
    shell = UserTreeShell({})
    
    # Get command from command line argument
    command = sys.argv[1]
    result = await shell.handle_command(command)
    
    # Print raw result for debugging
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())