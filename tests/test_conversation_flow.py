#!/usr/bin/env python3
"""
Test conversation flow to verify history continuity.
Predetermined conversation to check if the AI maintains context.
"""

import asyncio
from heaven_tree_repl import TreeShell, render_response
from heaven_base import HeavenAgentConfig, ProviderEnum, completion_runner
from heaven_base.langgraph.foundation import HeavenState


def test_conversation_flow():
    """Test predetermined conversation flow."""
    
    config = {
        "app_id": "conversation_test",
        "domain": "chat_continuity", 
        "role": "assistant",
        "nodes": {
            "root": {
                "type": "Menu",
                "prompt": "🧪 Conversation Test",
                "description": "Test chat continuity",
                "options": {
                    "1": "chat",
                    "2": "history"
                }
            },
            "chat": {
                "type": "Callable",
                "prompt": "Chat",
                "description": "Send message to HEAVEN agent",
                "function_name": "_chat",
                "args_schema": {"message": "str"}
            },
            "history": {
                "type": "Callable", 
                "prompt": "Chat History",
                "description": "View conversation history",
                "function_name": "_history",
                "args_schema": {}
            }
        }
    }
    
    # Create shell and conversation storage
    shell = TreeShell(config)
    conversation = []
    
    # Create HEAVEN agent
    agent = HeavenAgentConfig(
        name="ContinuityTestAgent",
        system_prompt="You are a helpful assistant. Remember what we discuss and reference previous parts of our conversation when relevant. Be conversational and show that you remember context.",
        tools=[],
        provider=ProviderEnum.OPENAI,
        model="gpt-4o-mini",
        temperature=0.7
    )
    
    async def _chat(args):
        message = args.get("message", "")
        if not message:
            return "Please provide a message!", False
        
        try:
            # Create state with conversation history as context
            state = HeavenState({
                "results": [],
                "context": {"conversation_history": conversation},
                "agents": {}
            })
            
            # Build context-aware prompt including recent conversation
            context_prompt = message
            if conversation:
                # Add last few exchanges for context
                recent_history = conversation[-3:] if len(conversation) > 3 else conversation
                history_text = "\n".join([
                    f"Previous - You: {turn['user']}\nPrevious - Assistant: {turn['agent']}" 
                    for turn in recent_history
                ])
                context_prompt = f"Previous conversation:\n{history_text}\n\nCurrent message: {message}"
            
            result = await completion_runner(
                state,
                prompt=context_prompt,
                agent=agent
            )
            
            # Extract response from HEAVEN result structure
            response = "No response"
            if result and isinstance(result, dict) and "results" in result:
                results_list = result["results"]
                if results_list:
                    last_result = results_list[-1]
                    if "raw_result" in last_result:
                        raw_result = last_result["raw_result"]
                        if isinstance(raw_result, dict) and "messages" in raw_result:
                            messages = raw_result["messages"]
                            for msg in reversed(messages):
                                if isinstance(msg, dict) and msg.get('type') == 'AIMessage' and msg.get('content'):
                                    response = msg['content']
                                    break
            
            # Store in conversation
            conversation.append({"user": message, "agent": response})
            
            return response, True
            
        except Exception as e:
            return f"Error: {str(e)}", False
    
    def _history(args):
        if not conversation:
            return "No conversation history yet.", True
        
        history = "🧪 Conversation Test History:\n\n"
        for i, turn in enumerate(conversation, 1):
            history += f"{i}. You: {turn['user']}\n"
            history += f"   Agent: {turn['agent']}\n\n"
        
        return history.strip(), True
    
    # Register functions  
    shell.register_async_function("_chat", _chat)
    shell._history = _history
    
    print("🧪 CONVERSATION CONTINUITY TEST")
    print("=" * 40)
    print("Testing predetermined conversation flow to verify context continuity...\n")
    
    # Predetermined conversation flow to test continuity
    test_messages = [
        "Hi! My name is Alice and I love astronomy. What's your favorite planet?",
        "That's interesting! Can you tell me why you like that planet?", 
        "Since I mentioned I love astronomy, what do you think I should observe tonight with my telescope?",
        "Great suggestions! By the way, do you remember what my name is?",
        "Perfect! Now, given that I love astronomy and you know my name, can you write me a short personalized stargazing tip?"
    ]
    
    print("CONVERSATION FLOW:")
    print("-" * 20)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n🔹 Step {i}: Sending message...")
        print(f"User: {message}")
        
        # Jump to chat node and send message
        shell.handle_command("jump 0.1.1")
        response = shell.handle_command(f'1 {{"message": "{message}"}}')
        
        # Extract and display the response
        agent_response = "No response extracted"
        if "result" in response and isinstance(response["result"], dict):
            result_data = response["result"]
            if "result" in result_data:
                agent_response = result_data["result"]
            elif "raw_result" in result_data:
                agent_response = result_data["raw_result"]
        
        print(f"Agent: {agent_response}")
        
        # Debug: print response structure
        print(f"[DEBUG] Response keys: {list(response.keys()) if isinstance(response, dict) else 'Not dict'}")
        if isinstance(response, dict) and "result" in response:
            result_keys = list(response["result"].keys()) if isinstance(response["result"], dict) else "Not dict"
            print(f"[DEBUG] Result keys: {result_keys}")
        
        # Small delay to make it easier to read
        import time
        time.sleep(1)
    
    print(f"\n{'='*40}")
    print("FINAL CONVERSATION HISTORY:")
    print("-" * 25)
    
    # Show complete history
    shell.handle_command("jump 0.1.2")
    history_response = shell.handle_command("1")
    
    if "result" in history_response and isinstance(history_response["result"], dict):
        history_text = history_response["result"].get("result", "No history")
        print(history_text)
    
    print(f"\n{'='*40}")
    print("CONTINUITY ANALYSIS:")
    print("-" * 20)
    
    analysis_points = [
        "✓ Does the agent remember Alice's name?",
        "✓ Does it reference her love of astronomy?", 
        "✓ Does it build on previous responses?",
        "✓ Does the final tip feel personalized?",
        "✓ Is the conversation flow natural and connected?"
    ]
    
    for point in analysis_points:
        print(point)
    
    print(f"\n🧪 Test completed! Review the conversation above to verify continuity.")


if __name__ == "__main__":
    test_conversation_flow()