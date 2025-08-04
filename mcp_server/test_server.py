#!/usr/bin/env python3
"""
Test script for TreeShell MCP Server
"""
import asyncio
import json

# Test imports before server startup
try:
    from server import TreeShellServer, TreeShellTools
    print("✅ Server imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)


async def test_server():
    """Test TreeShell server functionality"""
    print("\n🧪 TESTING TREESHELL MCP SERVER")
    print("=" * 40)
    
    # Initialize server
    server = TreeShellServer()
    print("✅ Server initialized")
    
    # Test 1: Start a conversation
    print("\n📝 Test 1: Starting conversation...")
    result = await server.start_conversation(
        title="Test Conversation",
        message="Hello! This is a test message.",
        tags=["test", "mcp"]
    )
    
    if result["success"]:
        print(f"✅ Conversation started: {result['conversation_id']}")
        print(f"   Response: {result['response'][:100]}...")
        conv_id = result["conversation_id"]
    else:
        print(f"❌ Failed: {result['error']}")
        return
    
    # Test 2: Continue conversation
    print("\n📝 Test 2: Continuing conversation...")
    result = await server.continue_conversation(
        message="Do you remember what we just talked about?"
    )
    
    if result["success"]:
        print(f"✅ Conversation continued (exchange #{result['exchange_number']})")
        print(f"   Response: {result['response'][:100]}...")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Test 3: List conversations
    print("\n📝 Test 3: Listing conversations...")
    result = server.list_conversations(limit=5)
    
    if result["success"]:
        print(f"✅ Found {result['total']} conversations")
        for conv in result["conversations"]:
            current = " (CURRENT)" if conv["is_current"] else ""
            print(f"   - {conv['title'][:30]}{current}")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Test 4: Search conversations
    print("\n📝 Test 4: Searching conversations...")
    result = server.search_conversations("test")
    
    if result["success"]:
        print(f"✅ Found {result['total']} matches for 'test'")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Test 5: Response modes
    print("\n📝 Test 5: Testing response modes...")
    
    # Test truncated actions mode
    result = server.set_response_mode("truncated_actions")
    if result["success"]:
        print(f"✅ Set mode to: {result['response_mode']}")
    
    # Continue with truncated mode
    result = await server.continue_conversation(
        message="Can you help me understand Python decorators?"
    )
    
    if result["success"]:
        print(f"✅ Got truncated response:")
        response = result["response"]
        if isinstance(response, dict):
            print(f"   Actions: {response.get('action_summary', [])}")
            print(f"   Response: {response.get('final_response', '')[:100]}...")
    
    # Test 6: Get current conversation
    print("\n📝 Test 6: Getting current conversation...")
    result = server.get_current_conversation()
    
    if result["success"]:
        if result["current_conversation"]:
            curr = result["current_conversation"]
            print(f"✅ Current: {curr['title']} ({curr['total_exchanges']} exchanges)")
        else:
            print("✅ No current conversation")
    
    print("\n🎉 ALL TESTS COMPLETED!")


if __name__ == "__main__":
    asyncio.run(test_server())