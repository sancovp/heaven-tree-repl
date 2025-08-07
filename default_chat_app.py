#!/usr/bin/env python3
"""
Default Chat App - Provides UserTreeShell with full conversation management

This exposes the default UserTreeShell which now includes:
- Complete conversation management (0.4.* coordinates)
- Agent configuration builder (0.3.1.* coordinates)  
- All standard TreeShell functionality

The conversation management functionality that was previously in a custom
conversation_chat_app has been moved into the default UserTreeShell configuration.
"""

import asyncio
from heaven_tree_repl import UserTreeShell, render_response


async def main():
    """
    Create and return a UserTreeShell with default configuration.
    
    The default UserTreeShell now includes all conversation management
    functionality at coordinates 0.4.*:
    - 0.4.1: Start New Chat
    - 0.4.2: Continue Chat  
    - 0.4.3: List Conversations
    - 0.4.4: Load Conversation
    - 0.4.5: Search Conversations
    
    Returns:
        UserTreeShell: Configured shell with conversation management
    """
    # Create shell with default user configuration
    shell = UserTreeShell({})
    return shell


if __name__ == "__main__":
    # Test the shell when run directly
    async def test_shell():
        shell = await main()
        response = await shell.handle_command("")
        print(render_response(response))
    
    asyncio.run(test_shell())