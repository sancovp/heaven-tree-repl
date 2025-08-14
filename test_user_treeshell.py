#!/usr/bin/env python3

import os
import sys
import asyncio

# Set HEAVEN_DATA_DIR environment variable
os.environ['HEAVEN_DATA_DIR'] = '/tmp/heaven_data'

sys.path.insert(0, '/home/GOD/heaven-tree-repl')

from heaven_tree_repl.shells import UserTreeShell
from heaven_tree_repl import render_response

async def main():
    # Create shell with proper config including session persistence
    config = {
        "app_id": "user_interface_hub",
        "domain": "user_management", 
        "role": "user"
    }
    shell = UserTreeShell(config)
    
    # Get command from command line argument
    command = sys.argv[1]
    result = await shell.handle_command(command)
    rendered = render_response(result)
    print(rendered)

if __name__ == "__main__":
    asyncio.run(main())