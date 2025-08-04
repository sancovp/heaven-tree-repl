#!/usr/bin/env python3
"""
Debug script to understand what completion_runner actually returns.
"""

import asyncio
from heaven_base import HeavenAgentConfig, ProviderEnum, completion_runner
from heaven_base.langgraph.foundation import HeavenState
from heaven_base.utils.heaven_response_utils import debug_heaven_result_structure


async def debug_completion_structure():
    """Debug what completion_runner actually returns."""
    
    agent = HeavenAgentConfig(
        name="DebugAgent",
        system_prompt="You are a test agent.",
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
    
    print("🔍 DEBUGGING COMPLETION_RUNNER RESULT STRUCTURE")
    print("=" * 50)
    
    try:
        result = await completion_runner(
            state,
            prompt="Say hello briefly",
            agent=agent
        )
        
        print(f"📊 Top-level result type: {type(result)}")
        print(f"📊 Top-level result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict) and "results" in result:
            results_list = result["results"]
            print(f"📊 Results list length: {len(results_list)}")
            
            if results_list:
                last_result = results_list[-1]
                print(f"📊 Last result keys: {list(last_result.keys())}")
                
                if "raw_result" in last_result:
                    raw_result = last_result["raw_result"]
                    print(f"📊 Raw result type: {type(raw_result)}")
                    print(f"📊 Raw result class name: {raw_result.__class__.__name__}")
                    
                    # Check if it's a History object
                    if hasattr(raw_result, '__module__'):
                        print(f"📊 Raw result module: {raw_result.__module__}")
                    
                    # List all attributes
                    attrs = [attr for attr in dir(raw_result) if not attr.startswith('_')]
                    print(f"📊 Raw result attributes: {attrs[:10]}...")  # First 10 attributes
                    
                    # Check for History-specific methods
                    history_methods = ['iterations', 'messages', 'to_markdown', 'to_json']
                    for method in history_methods:
                        has_method = hasattr(raw_result, method)
                        print(f"📊 Has {method}: {has_method}")
                        
                        if has_method and method == 'iterations':
                            try:
                                iterations = getattr(raw_result, method)
                                if callable(iterations):
                                    iterations_result = iterations()
                                    print(f"📊 Iterations (callable) result: {type(iterations_result)}, keys: {list(iterations_result.keys()) if isinstance(iterations_result, dict) else 'Not dict'}")
                                else:
                                    print(f"📊 Iterations (property) type: {type(iterations)}, keys: {list(iterations.keys()) if isinstance(iterations, dict) else 'Not dict'}")
                            except Exception as e:
                                print(f"📊 Error accessing iterations: {e}")
                        
                        if has_method and method == 'messages':
                            try:
                                messages = getattr(raw_result, method)
                                print(f"📊 Messages type: {type(messages)}")
                                if isinstance(messages, list):
                                    print(f"📊 Messages count: {len(messages)}")
                                    if messages:
                                        print(f"📊 First message type: {type(messages[0])}")
                                        print(f"📊 First message class: {messages[0].__class__.__name__}")
                            except Exception as e:
                                print(f"📊 Error accessing messages: {e}")
                    
                    # If it's a dict, show the structure
                    if isinstance(raw_result, dict):
                        print(f"📊 Raw result dict keys: {list(raw_result.keys())}")
                        if "messages" in raw_result:
                            messages = raw_result["messages"]
                            print(f"📊 Dict messages count: {len(messages)}")
                            if messages:
                                print(f"📊 First dict message: {messages[0]}")
        
        # Use our debug utility too
        debug_info = debug_heaven_result_structure(result)
        print(f"\n📊 Debug utility analysis: {debug_info}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_completion_structure())