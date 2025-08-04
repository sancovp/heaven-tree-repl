#!/usr/bin/env python3
"""
Simple conversation test - just run the original example but with multiple messages to test continuity.
"""

import asyncio
from heaven_tree_repl import TreeShell, render_response
from heaven_base import HeavenAgentConfig, ProviderEnum, completion_runner
from heaven_base.langgraph.foundation import HeavenState
from heaven_base.utils.heaven_response_utils import extract_heaven_response, debug_heaven_result_structure, extract_and_format_iterations


def main():
    config = {
        "app_id": "heaven_chat",
        "domain": "conversation", 
        "role": "assistant",
        "nodes": {
            "root": {
                "type": "Menu",
                "prompt": "💬 HEAVEN Chat",
                "description": "Chat with HEAVEN agents",
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
    
    # Create HEAVEN agent with memory instructions
    agent = HeavenAgentConfig(
        name="ChatAgent",
        system_prompt="You are a helpful chat assistant. Be conversational and friendly. Remember what the user tells you and reference it in future responses when relevant.",
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
            # Include conversation history in the prompt for continuity
            state = HeavenState({
                "results": [],
                "context": {},
                "agents": {}
            })
            
            # Build context-aware prompt
            context_prompt = message
            if conversation:
                # Add recent conversation history
                recent_history = conversation[-3:]  # Last 3 exchanges
                history_text = "\n".join([
                    f"User previously said: {turn['user']}\nYou previously replied: {turn['agent']}" 
                    for turn in recent_history
                ])
                context_prompt = f"Recent conversation history:\n{history_text}\n\nCurrent user message: {message}\n\nPlease respond while being aware of the conversation history above."
            
            result = await completion_runner(
                state,
                prompt=context_prompt,
                agent=agent
            )
            
            # Extract response using HEAVEN iteration utilities
            response = extract_heaven_response(result)
            
            # Debug: print result structure and iterations for the first message
            if len(conversation) == 0:
                debug_info = debug_heaven_result_structure(result)
                print(f"[DEBUG] First completion result structure: {debug_info}")
                
                # Try to format iterations as markdown
                iterations_md = extract_and_format_iterations(result)
                print(f"[DEBUG] Iterations markdown:\n{iterations_md}")
                print("-" * 50)
            
            # Store in conversation
            conversation.append({"user": message, "agent": response})
            return response, True
            
        except Exception as e:
            return f"Error: {str(e)}", False
    
    def _history(args):
        if not conversation:
            return "No conversation history yet.", True
        
        history = "💬 Chat History:\n\n"
        for i, turn in enumerate(conversation, 1):
            history += f"{i}. You: {turn['user']}\n"
            history += f"   Agent: {turn['agent']}\n\n"
        
        return history.strip(), True
    
    # Register functions  
    shell.register_async_function("_chat", _chat)
    shell._history = _history
    
    print("🧪 Testing Conversation Continuity")
    print("=" * 35)
    
    # Test messages for continuity
    messages = [
        "Hi, my name is Alice and I love stargazing.",
        "What's the best planet to observe tonight?",
        "Thanks! By the way, do you remember my name?",
        "Perfect! Can you give me a personalized tip for stargazing?"
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"\n🔹 Message {i}: {msg}")
        
        # Send message
        shell.handle_command("jump 0.1.1")
        response = shell.handle_command(f'1 {{"message": "{msg}"}}')
        
        # Show response using the renderer
        print(render_response(response))
        print("-" * 50)
    
    print("\n📋 FINAL CONVERSATION HISTORY:")
    shell.handle_command("jump 0.1.2") 
    history_response = shell.handle_command("1")
    print(render_response(history_response))


if __name__ == "__main__":
    main()