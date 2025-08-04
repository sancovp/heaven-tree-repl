#!/usr/bin/env python3
"""
Test the new extract_last_iteration_complete function.
"""

import asyncio
from heaven_base import HeavenAgentConfig, ProviderEnum
from heaven_base.langgraph.foundation import HeavenState, completion_runner
from heaven_base.utils.heaven_response_utils import extract_heaven_response, extract_last_iteration_complete, format_iteration_to_markdown


async def test_last_iteration():
    """Test extracting the complete last iteration."""
    
    agent = HeavenAgentConfig(
        name="IterationTestAgent",
        system_prompt="You are a helpful assistant. Say hello and briefly explain what you are.",
        tools=[],
        provider=ProviderEnum.OPENAI,
        model="gpt-4o-mini",
        temperature=0.7
    )
    
    state = HeavenState({
        "results": [],
        "context": {},
        "agents": {}
    })
    
    print("🧪 TESTING COMPLETE LAST ITERATION EXTRACTION")
    print("=" * 50)
    
    try:
        # Get a completion result
        result = await completion_runner(
            state,
            prompt="Say hello and tell me what you are",
            agent=agent
        )
        
        print("✅ Got completion result")
        
        # Test 1: Extract just the AI response (current mode)
        ai_response = extract_heaven_response(result)
        print(f"📊 AI Response Only: {ai_response}")
        print()
        
        # Test 2: Extract complete last iteration (new mode)
        last_iteration = extract_last_iteration_complete(result)
        print(f"📊 Last Iteration Complete:")
        print(f"   Type: {type(last_iteration)}")
        if last_iteration:
            print(f"   Messages count: {len(last_iteration)}")
            print(f"   Message types: {[type(msg).__name__ for msg in last_iteration]}")
            print()
            
            # Format the complete iteration as markdown
            formatted = format_iteration_to_markdown("last_iteration", last_iteration)
            print(f"📊 Formatted Last Iteration:")
            print(formatted)
        else:
            print("   ❌ No last iteration found")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_last_iteration())