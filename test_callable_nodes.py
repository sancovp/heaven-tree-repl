#!/usr/bin/env python3
"""
Test script for the enhanced callable node functionality.
Tests all 3 approaches: import, function_code, and existing function.
"""

import asyncio
import json
from heaven_tree_repl import TreeShell, render_response

async def main():
    # Create a basic TreeShell
    config = {
        "app_id": "callable_test",
        "domain": "testing",
        "nodes": {
            "root": {
                "type": "Menu",
                "prompt": "Callable Node Test",
                "description": "Testing callable node functionality",
                "options": {}
            }
        }
    }
    
    shell = TreeShell(config)
    
    print("🧪 Testing Enhanced Callable Node System")
    print("=" * 50)
    
    # Test 1: Dynamic function code (sync)
    print("\n📝 Test 1: Dynamic Function Code (sync)")
    
    node_data_1 = {
        "type": "Callable",
        "prompt": "System Info",
        "function_name": "_system_info",
        "is_async": False,
        "function_code": """
import os
import datetime

def _system_info(args):
    env = os.environ.get('NODE_ENV', 'development')
    time = datetime.datetime.now().strftime('%H:%M:%S')
    cwd = os.getcwd()
    info = f'''🖥️ System Information:
Environment: {env}
Current Time: {time}
Working Directory: {cwd}
Python Path: Available'''
    return info, True
"""
    }
    
    result = await shell.handle_command(f'jump 0.0.2.10 {json.dumps({"coordinate": "0.1.10", "node_data": node_data_1})}')
    print("Add node result:", result.get("result", {}).get("result", "Failed"))
    
    # Test the created function
    if result.get("result", {}).get("result", {}).get("added"):
        print("\n🔧 Testing the created function:")
        test_result = await shell.handle_command('jump 0.1.10 {}')
        print(render_response(test_result))
    
    # Test 2: Dynamic function code (async) 
    print("\n📝 Test 2: Dynamic Function Code (async)")
    
    node_data_2 = {
        "type": "Callable",
        "prompt": "Async Greeting",
        "function_name": "_async_greeting",
        "is_async": True,
        "function_code": """
import asyncio

async def _async_greeting(args):
    name = args.get('name', 'Friend')
    await asyncio.sleep(0.1)  # Simulate async work
    greeting = f'Hello {name}! This response came from an async function. ⚡'
    return greeting, True
"""
    }
    
    result = await shell.handle_command(f'jump 0.0.2.10 {json.dumps({"coordinate": "0.1.11", "node_data": node_data_2})}')
    print("Add async node result:", result.get("result", {}).get("result", "Failed"))
    
    # Test the created async function
    if result.get("result", {}).get("result", {}).get("added"):
        print("\n🔧 Testing the async function:")
        test_result = await shell.handle_command('jump 0.1.11 {"name": "Alice"}')
        print(render_response(test_result))
    
    # Test 3: Use existing function
    print("\n📝 Test 3: Use Existing Function")
    
    node_data_3 = {
        "type": "Callable",
        "prompt": "List Session Variables",
        "function_name": "_meta_list_vars",  # This already exists
        "is_async": False
    }
    
    result = await shell.handle_command(f'jump 0.0.2.10 {json.dumps({"coordinate": "0.1.12", "node_data": node_data_3})}')
    print("Add existing function node result:", result.get("result", {}).get("result", "Failed"))
    
    # Test the existing function
    if result.get("result", {}).get("result", {}).get("added"):
        print("\n🔧 Testing the existing function:")
        test_result = await shell.handle_command('jump 0.1.12 {}')
        print(render_response(test_result))
    
    # Test 4: Error handling - missing required fields
    print("\n📝 Test 4: Error Handling - Missing is_async")
    
    bad_node_data = {
        "type": "Callable",
        "prompt": "Bad Node",
        "function_name": "_bad_func"
        # Missing is_async!
    }
    
    result = await shell.handle_command(f'jump 0.0.2.10 {json.dumps({"coordinate": "0.1.13", "node_data": bad_node_data})}')
    error_msg = result.get("result", {}).get("result", {}).get("error", "No error shown")
    print("Expected error:", error_msg)
    
    print("\n✅ All tests completed!")
    
    # Show final tree structure
    print("\n🌳 Final Tree Structure:")
    list_result = await shell.handle_command('jump 0.0.2.13 {"pattern": "0.1"}')
    nodes = list_result.get("result", {}).get("result", {}).get("nodes", {})
    for coord, node_info in nodes.items():
        print(f"  {coord}: {node_info['prompt']} ({node_info['type']})")

if __name__ == "__main__":
    asyncio.run(main())