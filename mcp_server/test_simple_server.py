#!/usr/bin/env python3
"""
Test script for simplified TreeShell MCP Server
"""
import os

# Set environment
os.environ['HEAVEN_DATA_DIR'] = '/tmp/heaven_data'
os.makedirs('/tmp/heaven_data', exist_ok=True)

# Test imports
try:
    from server import TreeShellMCPServer
    print("✅ Server imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)


def test_server():
    """Test TreeShell MCP server functionality"""
    print("\n🧪 TESTING SIMPLIFIED TREESHELL MCP SERVER")
    print("=" * 45)
    
    # Initialize server
    server = TreeShellMCPServer()
    if not server.shell:
        print("❌ Shell not initialized")
        return
    
    print("✅ Server initialized")
    
    # Test 1: Show root menu
    print("\n📝 Test 1: Show root menu...")
    result = server.run_conversation_shell("")
    
    if result["success"]:
        print("✅ Got root menu")
        print(f"   Current node: {result.get('current_node', 'unknown')}")
    else:
        print(f"❌ Failed: {result['error']}")
        return
    
    # Test 2: Navigate to start_chat
    print("\n📝 Test 2: Navigate to start_chat...")
    result = server.run_conversation_shell("jump 0.1.1")
    
    if result["success"]:
        print("✅ Navigated to start_chat")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Test 3: Start a conversation
    print("\n📝 Test 3: Start conversation...")
    cmd = '1 {"title": "MCP Test Chat", "message": "Hello from MCP!", "tags": "mcp,test"}'
    result = server.run_conversation_shell(cmd)
    
    if result["success"]:
        print("✅ Started conversation via MCP")
        # Try to extract conversation info from result
        import json
        try:
            result_data = json.loads(result["result"])
            if "conversation_id" in result_data:
                print(f"   Conversation ID: {result_data['conversation_id']}")
        except:
            pass
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Test 4: Navigate to list conversations
    print("\n📝 Test 4: List conversations...")
    result = server.run_conversation_shell("jump 0.1.3")
    if result["success"]:
        result = server.run_conversation_shell('1 {"limit": 5}')
        if result["success"]:
            print("✅ Listed conversations via MCP")
        else:
            print(f"❌ List failed: {result['error']}")
    else:
        print(f"❌ Navigation failed: {result['error']}")
    
    print("\n🎉 SIMPLIFIED MCP SERVER TESTS COMPLETED!")


if __name__ == "__main__":
    test_server()