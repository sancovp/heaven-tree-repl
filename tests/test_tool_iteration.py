#!/usr/bin/env python3
"""
Test complete iteration extraction with WriteBlockReportTool.
This should show AI message + tool call + tool result in the iteration.
"""

import asyncio
import sys
sys.path.insert(0, '/home/GOD/heaven-framework-repo')

from heaven_base import HeavenAgentConfig, ProviderEnum
from heaven_base.langgraph.foundation import HeavenState, completion_runner
from heaven_base.utils.heaven_response_utils import extract_heaven_response, extract_last_iteration_complete, format_iteration_to_markdown, extract_truncated_actions_with_response, format_truncated_actions_display


async def test_tool_iteration():
    """Test complete iteration with tool usage."""
    
    # Create agent - tools are automatically available
    agent = HeavenAgentConfig(
        name="ToolTestAgent",
        system_prompt="You are a helpful assistant. When asked to create a block report, use the WriteBlockReportTool to generate it.",
        tools=[],  # Tools are internally added
        provider=ProviderEnum.OPENAI,
        model="gpt-4o-mini",
        temperature=0.7
    )
    
    state = HeavenState({
        "results": [],
        "context": {},
        "agents": {}
    })
    
    print("🧪 TESTING COMPLETE ITERATION WITH TOOL USAGE")
    print("=" * 55)
    
    try:
        # Ask the agent to use WriteBlockReportTool
        result = await completion_runner(
            state,
            prompt="Please use WriteBlockReportTool to create a test block report with completed_tasks=['analyze_data'], current_task='generate_summary', and explanation='Testing the block report functionality'",
            agent=agent
        )
        
        print("✅ Got completion result with tool usage")
        
        # Test 1: Extract just the AI response
        ai_response = extract_heaven_response(result)
        print(f"📊 AI Response Only:")
        print(f"{ai_response}")
        print()
        
        # Test 2: Extract complete last iteration
        last_iteration = extract_last_iteration_complete(result)
        print(f"📊 Last Iteration Complete:")
        if last_iteration:
            print(f"   Messages count: {len(last_iteration)}")
            print(f"   Message types: {[type(msg).__name__ for msg in last_iteration]}")
            print()
            
            # Format the complete iteration
            formatted = format_iteration_to_markdown("tool_usage_iteration", last_iteration)
            print(f"📊 Formatted Complete Iteration:")
            print("=" * 50)
            print(formatted)
            print("=" * 50)
        else:
            print("   ❌ No last iteration found")
        
        # Test 3: Extract truncated actions with response
        truncated_data = extract_truncated_actions_with_response(result)
        print(f"\n📊 Truncated Actions Data:")
        print(f"   Has actions: {truncated_data['has_actions']}")
        print(f"   Action summary: {truncated_data['action_summary']}")
        print(f"   Final response: {truncated_data['final_response']}")
        
        # Format truncated display
        truncated_display = format_truncated_actions_display(truncated_data)
        print(f"\n📊 Truncated Actions Display:")
        print("=" * 50)
        print(truncated_display)
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_tool_iteration())