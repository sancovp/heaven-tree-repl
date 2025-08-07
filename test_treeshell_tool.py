#!/usr/bin/env python3
"""
Test script for ConversationTreeShellTool integration with HEAVEN agents.

This tests whether agents can properly navigate and use TreeShell interfaces.
"""

import sys
import asyncio
from pathlib import Path

# Add paths
sys.path.insert(0, '/home/GOD/heaven-framework-repo')
sys.path.insert(0, '/home/GOD/heaven-tree-repl')

from heaven_base import HeavenAgentConfig, ProviderEnum, completion_runner
from heaven_base.langgraph.foundation import HeavenState
from heaven_base.tools.network_edit_tool import NetworkEditTool
from heaven_tree_repl.tools import ConversationTreeShellTool


async def test_with_agent():
    """Test the tool with a HEAVEN agent."""
    print("\n\n=== Testing ConversationTreeShellTool with HEAVEN Agent ===")
    
    # Create agent config with the TreeShell tool
    agent_config = HeavenAgentConfig(
        name="TreeShellTestAgent",
        system_prompt="""You are a TreeShell Test Agent. Your job is to test the ConversationTreeShellTool.

You have access to a ConversationTreeShellTool that provides a TreeShell interface for managing conversations.

Please test the following workflow:
1. Show the main menu
2. Navigate to start_chat
3. Start a new chat with title "Agent Test Chat" and message "Hello from agent"
4. Navigate to continue_chat
5. Continue the conversation with "How does this TreeShell work?"
6. List conversations

Use the ConversationTreeShellTool with various commands to navigate and test the interface.""",
        tools=[ConversationTreeShellTool],
        provider=ProviderEnum.OPENAI,
        model="o4-mini",
        temperature=0.7
    )
    
    # Create initial state
    state = HeavenState({
        "results": [],
        "context": {},
        "agents": {}
    })
    
    # Run the agent
    print("Running agent to test ConversationTreeShellTool...")
    result = await completion_runner(
        state,
        prompt="Please test the ConversationTreeShellTool by running the command '' (empty string) to show the main menu.",
        agent=agent_config
    )
    
    print("Agent response:")
    print("=" * 50)
    print(result)


async def main():
    """Run tests with agent."""
    await test_with_agent()


if __name__ == "__main__":
    asyncio.run(main())