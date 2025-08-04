#!/usr/bin/env python3
"""
Inspect the actual contents of hermes_runner's raw_result dict.
"""

import asyncio
import json
from heaven_base import HeavenAgentConfig, ProviderEnum
from heaven_base.langgraph.foundation import HeavenState, hermes_runner


async def inspect_hermes_raw_result():
    """Deep inspect what's actually IN the hermes raw_result dict."""
    
    agent = HeavenAgentConfig(
        name="InspectAgent",
        system_prompt="You are a test agent. Say hello briefly.",
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
    
    print("🔍 DEEP INSPECTION OF HERMES RAW_RESULT")
    print("=" * 45)
    
    try:
        hermes_result = await hermes_runner(
            state,
            goal="Say hello briefly",
            agent=agent,
            iterations=1
        )
        
        print(f"📊 Top level type: {type(hermes_result)}")
        print(f"📊 Top level keys: {list(hermes_result.keys())}")
        
        if "results" in hermes_result:
            results = hermes_result["results"]
            print(f"📊 Results length: {len(results)}")
            
            if results:
                last_result = results[-1]
                print(f"📊 Last result keys: {list(last_result.keys())}")
                
                if "raw_result" in last_result:
                    raw_result = last_result["raw_result"]
                    print(f"\n🔬 RAW_RESULT DEEP DIVE:")
                    print(f"📊 Raw result type: {type(raw_result)}")
                    print(f"📊 Raw result keys: {list(raw_result.keys())}")
                    
                    # Inspect each key in raw_result
                    for key, value in raw_result.items():
                        print(f"\n🔑 KEY: {key}")
                        print(f"   Type: {type(value)}")
                        
                        if key == "raw_result":  # Nested raw_result!
                            print(f"   🚨 NESTED RAW_RESULT FOUND!")
                            print(f"   Nested type: {type(value)}")
                            if hasattr(value, '__dict__'):
                                print(f"   Nested object attributes: {dir(value)}")
                            if isinstance(value, dict):
                                print(f"   Nested dict keys: {list(value.keys())}")
                                
                                # Check if THIS is the History object
                                if hasattr(value, 'iterations') or (isinstance(value, dict) and 'iterations' in value):
                                    print(f"   🎯 FOUND ITERATIONS IN NESTED RAW_RESULT!")
                                    iterations = value.get('iterations') if isinstance(value, dict) else getattr(value, 'iterations', None)
                                    print(f"   Iterations type: {type(iterations)}")
                                    if isinstance(iterations, dict):
                                        print(f"   Iteration keys: {list(iterations.keys())}")
                            
                        elif key == "history_id":
                            print(f"   Value: {value}")
                            
                        elif key == "formatted_output":
                            print(f"   Length: {len(str(value))} chars")
                            print(f"   Preview: {str(value)[:100]}...")
                            
                        elif key == "agent_status":
                            print(f"   Agent status: {value}")
                            
                        elif key == "prepared_message":
                            print(f"   Prepared message length: {len(str(value))} chars")
                            
                        elif isinstance(value, (list, dict)):
                            if isinstance(value, list):
                                print(f"   List length: {len(value)}")
                                if value:
                                    print(f"   First item type: {type(value[0])}")
                            elif isinstance(value, dict):
                                print(f"   Dict keys: {list(value.keys())}")
                        else:
                            print(f"   Value: {value}")
                    
                    # Check if the outer raw_result itself has iterations
                    if hasattr(raw_result, 'iterations'):
                        print(f"\n🎯 OUTER RAW_RESULT HAS ITERATIONS!")
                        iterations = raw_result.iterations
                        print(f"   Iterations type: {type(iterations)}")
                        if isinstance(iterations, dict):
                            print(f"   Iteration keys: {list(iterations.keys())}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(inspect_hermes_raw_result())