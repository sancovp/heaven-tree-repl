#!/usr/bin/env python3
"""
Test the updated heaven_response_utils that load History objects by ID.
"""

import asyncio
from heaven_base import HeavenAgentConfig, ProviderEnum
from heaven_base.langgraph.foundation import HeavenState, completion_runner
from heaven_base.utils.heaven_response_utils import extract_heaven_response, extract_history_id_from_result, extract_and_format_iterations


async def test_updated_utils():
    """Test the updated utility functions."""
    
    agent = HeavenAgentConfig(
        name="TestAgent",
        system_prompt="You are a helpful assistant. Say hello briefly.",
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
    
    print("🧪 TESTING UPDATED HEAVEN RESPONSE UTILS")
    print("=" * 45)
    
    try:
        # Get a completion result
        result = await completion_runner(
            state,
            prompt="Say hello briefly",
            agent=agent
        )
        
        print("✅ Got completion result")
        
        # Test 1: Extract history_id
        history_id = extract_history_id_from_result(result)
        print(f"📊 Extracted history_id: {history_id}")
        
        # Test 2: Extract response using new method
        response = extract_heaven_response(result)
        print(f"📊 Extracted response: {response}")
        
        # Test 3: Extract and format iterations
        iterations_md = extract_and_format_iterations(result)
        print(f"📊 Iterations markdown preview:")
        print(iterations_md[:200] + "..." if len(iterations_md) > 200 else iterations_md)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_updated_utils())