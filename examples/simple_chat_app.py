#!/usr/bin/env python3
"""
Simple HEAVEN Chat App - Calls actual HEAVEN agents for chat
"""

import asyncio
from heaven_tree_repl import TreeShell, render_response
from heaven_base import HeavenAgentConfig, ProviderEnum, completion_runner


def main():
    """Simple HEAVEN chat application."""
    
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
    
    # Create HEAVEN agent
    agent = HeavenAgentConfig(
        name="ChatAgent",
        system_prompt="You are a helpful chat assistant. Be conversational and friendly.",
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
            # Import HeavenState and create properly initialized state
            from heaven_base.langgraph.foundation import HeavenState
            state = HeavenState({
                "results": [],
                "context": {},
                "agents": {}
            })
            
            # Call HEAVEN completion
            result = await completion_runner(
                state,
                prompt=message,
                agent=agent
            )
            
            # Extract response from HEAVEN result structure
            response = "No response"
            if result and isinstance(result, dict) and "results" in result:
                results_list = result["results"]
                if results_list:
                    # Get the last (most recent) result
                    last_result = results_list[-1]
                    if "raw_result" in last_result:
                        raw_result = last_result["raw_result"]
                        # The raw_result should contain messages from the completion
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
        
        history = "💬 Chat History:\n\n"
        for i, turn in enumerate(conversation, 1):
            history += f"{i}. You: {turn['user']}\n"
            history += f"   Agent: {turn['agent']}\n\n"
        
        return history.strip(), True
    
    # Register functions  
    shell.register_async_function("_chat", _chat)
    shell._history = _history
    
    print("💬 HEAVEN Chat App Demo")
    print("=" * 25)
    
    # Show available nodes for debugging
    print("\nAvailable nodes:")
    for coord, node in shell.nodes.items():
        print(f"  {coord}: {node.get('prompt', 'No prompt')}")
    
    print("\n1. Show main menu:")
    response = shell.handle_command("")
    print(render_response(response))
    
    print("\n2. Jump to chat node:")
    response = shell.handle_command("jump 0.1.1")
    print(render_response(response))
    
    print("\n3. Send message to HEAVEN agent:")
    response = shell.handle_command('1 {"message": "Hello! Tell me a short joke."}')
    print(render_response(response))
    
    print("\n4. Jump to history node:")
    response = shell.handle_command("jump 0.1.2")
    print(render_response(response))
    
    print("\n5. View chat history:")
    response = shell.handle_command("1")
    print(render_response(response))
    
    print("\n✅ HEAVEN Chat Demo completed!")


if __name__ == "__main__":
    main()