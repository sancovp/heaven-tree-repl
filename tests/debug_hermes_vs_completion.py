#!/usr/bin/env python3
"""
Compare what hermes_runner returns vs completion_runner.
"""

import asyncio
from heaven_base import HeavenAgentConfig, ProviderEnum
from heaven_base.langgraph.foundation import HeavenState, completion_runner, hermes_runner


async def compare_runners():
    """Compare hermes_runner vs completion_runner return structures."""
    
    agent = HeavenAgentConfig(
        name="ComparisonAgent",
        system_prompt="You are a test agent for comparing runners.",
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
    
    print("🔍 COMPARING HERMES_RUNNER VS COMPLETION_RUNNER")
    print("=" * 55)
    
    # Test completion_runner
    print("\n1️⃣ COMPLETION_RUNNER:")
    print("-" * 25)
    try:
        completion_result = await completion_runner(
            state,
            prompt="Say hello briefly",
            agent=agent
        )
        
        print(f"📊 Type: {type(completion_result)}")
        print(f"📊 Keys: {list(completion_result.keys()) if isinstance(completion_result, dict) else 'Not dict'}")
        
        if isinstance(completion_result, dict) and "results" in completion_result:
            results = completion_result["results"]
            if results:
                raw_result = results[-1].get("raw_result", {})
                print(f"📊 Raw result type: {type(raw_result)}")
                print(f"📊 Raw result keys: {list(raw_result.keys()) if isinstance(raw_result, dict) else 'Not dict'}")
                print(f"📊 Has iterations: {hasattr(raw_result, 'iterations')}")
                print(f"📊 Has messages: {'messages' in raw_result if isinstance(raw_result, dict) else hasattr(raw_result, 'messages')}")
                
    except Exception as e:
        print(f"❌ Completion runner error: {e}")
    
    # Test hermes_runner  
    print("\n2️⃣ HERMES_RUNNER:")
    print("-" * 20)
    try:
        hermes_result = await hermes_runner(
            state,
            goal="Say hello briefly and explain what you are",
            agent=agent,
            iterations=1
        )
        
        print(f"📊 Type: {type(hermes_result)}")
        print(f"📊 Keys: {list(hermes_result.keys()) if isinstance(hermes_result, dict) else 'Not dict'}")
        
        if isinstance(hermes_result, dict) and "results" in hermes_result:
            results = hermes_result["results"]
            if results:
                raw_result = results[-1].get("raw_result", {})
                print(f"📊 Raw result type: {type(raw_result)}")
                print(f"📊 Raw result keys: {list(raw_result.keys()) if isinstance(raw_result, dict) else 'Not dict'}")
                print(f"📊 Has iterations: {hasattr(raw_result, 'iterations')}")
                print(f"📊 Has messages: {'messages' in raw_result if isinstance(raw_result, dict) else hasattr(raw_result, 'messages')}")
                
                # If it's an object, check what type
                if not isinstance(raw_result, dict):
                    print(f"📊 Raw result class: {raw_result.__class__.__name__}")
                    print(f"📊 Raw result module: {getattr(raw_result, '__module__', 'Unknown')}")
                    
                    # Check for History methods
                    history_methods = ['iterations', 'messages', 'to_markdown', 'to_json']
                    for method in history_methods:
                        has_method = hasattr(raw_result, method)
                        print(f"📊 Has {method}: {has_method}")
                        
                        if has_method and method == 'iterations':
                            try:
                                iterations = getattr(raw_result, method)
                                if callable(iterations):
                                    iterations_result = iterations()
                                    print(f"📊 Iterations result: {type(iterations_result)}")
                                    if isinstance(iterations_result, dict):
                                        print(f"📊 Iteration keys: {list(iterations_result.keys())}")
                                        for key, value in iterations_result.items():
                                            print(f"📊   {key}: {len(value)} messages" if isinstance(value, list) else f"📊   {key}: {type(value)}")
                                else:
                                    print(f"📊 Iterations (property): {type(iterations)}")
                                    if isinstance(iterations, dict):
                                        print(f"📊 Iteration keys: {list(iterations.keys())}")
                            except Exception as e:
                                print(f"📊 Error accessing iterations: {e}")
                
    except Exception as e:
        print(f"❌ Hermes runner error: {e}")
    
    print("\n🔬 ANALYSIS:")
    print("-" * 12)
    print("Looking for differences in return structure...")


if __name__ == "__main__":
    asyncio.run(compare_runners())