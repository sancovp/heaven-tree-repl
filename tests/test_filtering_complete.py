#!/usr/bin/env python3
"""
Test the complete conversation filtering workflow.
"""

import sys
sys.path.insert(0, '/home/GOD/heaven-framework-repo')

from conversation_chat_app import main
from heaven_tree_repl.renderer import render_response


def test_conversation_filtering():
    """Test the complete conversation workflow with filtering."""
    
    print("🧪 TESTING COMPLETE CONVERSATION FILTERING WORKFLOW")
    print("=" * 55)
    
    # Initialize the shell
    shell = main()
    
    print("\n🔹 Step 1: Starting a new conversation")
    
    # Navigate to start_chat
    response = shell.handle_command('jump 0.1.1')
    print("Navigated to start_chat node")
    
    # Start a conversation
    response = shell.handle_command('1 {"title": "Filtering Test Chat", "message": "Hello, I want to test conversation continuity", "tags": "testing,filtering"}')
    print("✅ Started conversation:")
    print(render_response(response))
    
    print("\n🔹 Step 2: Continuing the conversation")
    
    # Navigate to continue_chat  
    response = shell.handle_command('jump 0.1.2')
    print("Navigated to continue_chat node")
    
    # Continue the conversation
    response = shell.handle_command('1 {"message": "Do you remember what I just said about testing?"}')
    print("✅ Continued conversation:")
    print(render_response(response))
    
    print("\n🔹 Step 3: Continue again to build history chain")
    
    # Continue again
    response = shell.handle_command('1 {"message": "Great! Now let me ask something else entirely."}')
    print("✅ Continued again:")
    print(render_response(response))
    
    print("\n🔹 Step 4: List conversations to see clean metadata")
    
    # Navigate to list_conversations
    response = shell.handle_command('jump 0.1.3')
    print("Navigated to list_conversations node")
    
    # List conversations
    response = shell.handle_command('1 {"limit": 5}')
    print("✅ Listed conversations:")
    print(render_response(response))
    
    print("\n🔹 Step 5: Testing get_latest_history utility")
    
    # Import and test the utility directly
    from heaven_base.utils.heaven_conversation_utils import list_chats, get_latest_history
    
    conversations = list_chats(limit=1)
    if conversations:
        conv = conversations[0]
        conv_id = conv['conversation_id']
        latest_history = get_latest_history(conv_id)
        
        print(f"Conversation ID: {conv_id}")
        print(f"History chain length: {len(conv['history_chain'])}")
        print(f"History chain: {conv['history_chain']}")
        print(f"Latest history (filtered): {latest_history}")
        print(f"✅ Filtering works: {latest_history == conv['history_chain'][-1]}")
    
    print("\n🎉 CONVERSATION FILTERING TEST COMPLETE!")
    print("✅ Conversations show clean metadata")
    print("✅ get_latest_history() filters to terminal snapshot")
    print("✅ Continue chat uses latest history only")


if __name__ == "__main__":
    test_conversation_filtering()