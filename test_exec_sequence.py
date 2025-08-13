#!/usr/bin/env python3

import sys
import asyncio
sys.path.insert(0, '/home/GOD/heaven-tree-repl')

from heaven_tree_repl.shells import UserTreeShell
from heaven_tree_repl import render_response

async def main():
    shell = UserTreeShell({})
    
    print("=== Step 1: Jump to callable node ===")
    result1 = await shell.handle_command('jump 0.1.2.5')
    print(render_response(result1))
    
    print("\n=== Step 2: Execute with 'exec' command ===") 
    result2 = await shell.handle_command('exec')
    print(render_response(result2))

if __name__ == "__main__":
    asyncio.run(main())