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
    # Create shell using new 19-config system API
    # UserTreeShell now loads system configs and applies dev customizations automatically
    shell = UserTreeShell(user_config_path=None)  # No dev customizations, use system defaults
    
    # Get command from command line argument
    command = sys.argv[1]
    result = await shell.handle_command(command)
    rendered = render_response(result)
    print(rendered)

if __name__ == "__main__":
    asyncio.run(main())