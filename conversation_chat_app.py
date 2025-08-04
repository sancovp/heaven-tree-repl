#!/usr/bin/env python3
"""
Enhanced HEAVEN Chat App with Conversation Management

This demonstrates proper conversation flow:
- start_chat: Creates new conversation + first history
- continue_chat: Adds new history to existing conversation
- list_conversations: Show available conversations
- load_conversation: Switch to existing conversation

Uses both heaven_response_utils and heaven_conversation_utils.
"""

import asyncio
from heaven_tree_repl import TreeShell, render_response
from heaven_base import HeavenAgentConfig, ProviderEnum, completion_runner
from heaven_base.langgraph.foundation import HeavenState
from heaven_base.utils.heaven_response_utils import extract_heaven_response, extract_history_id_from_result
from heaven_base.utils.heaven_conversation_utils import start_chat, continue_chat, load_chat, list_chats, search_chats, get_latest_history


def main():
    config = {
        "app_id": "heaven_conversation_chat",
        "domain": "conversation", 
        "role": "assistant",
        "nodes": {
            "root": {
                "type": "Menu",
                "prompt": "💬 HEAVEN Conversation Chat",
                "description": "Chat with conversation management",
                "options": {
                    "1": "start_chat",
                    "2": "continue_chat", 
                    "3": "list_conversations",
                    "4": "load_conversation",
                    "5": "search_conversations"
                }
            },
            "start_chat": {
                "type": "Callable",
                "prompt": "Start New Chat",
                "description": "Start a new conversation with a title and first message",
                "function_name": "_start_chat",
                "args_schema": {
                    "title": "str", 
                    "message": "str",
                    "tags": "str"  # comma-separated
                }
            },
            "continue_chat": {
                "type": "Callable",
                "prompt": "Continue Chat", 
                "description": "Continue the current active conversation",
                "function_name": "_continue_chat",
                "args_schema": {"message": "str"}
            },
            "list_conversations": {
                "type": "Callable",
                "prompt": "List Conversations",
                "description": "Show recent conversations",
                "function_name": "_list_conversations",
                "args_schema": {"limit": "int"}
            },
            "load_conversation": {
                "type": "Callable",
                "prompt": "Load Conversation",
                "description": "Switch to an existing conversation",
                "function_name": "_load_conversation", 
                "args_schema": {"conversation_id": "str"}
            },
            "search_conversations": {
                "type": "Callable",
                "prompt": "Search Conversations",
                "description": "Search conversations by title or tags",
                "function_name": "_search_conversations",
                "args_schema": {"query": "str"}
            }
        }
    }
    
    # Create shell and state
    shell = TreeShell(config)
    
    # Global state for current conversation
    current_conversation = {
        "conversation_id": None,
        "conversation_data": None
    }
    
    # Create HEAVEN agent
    agent = HeavenAgentConfig(
        name="ConversationAgent",
        system_prompt="You are a helpful conversational assistant. Be friendly and remember context from the conversation history.",
        tools=[],
        provider=ProviderEnum.OPENAI,
        model="gpt-4o-mini",
        temperature=0.7
    )
    
    async def _start_chat(args):
        """Start a new conversation."""
        title = args.get("title", "").strip()
        message = args.get("message", "").strip()
        tags_str = args.get("tags", "").strip()
        
        if not title:
            return "❌ Please provide a conversation title", False
        if not message:
            return "❌ Please provide a first message", False
        
        try:
            # Parse tags
            tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()] if tags_str else []
            
            # Create HEAVEN state and get first response
            state = HeavenState({
                "results": [],
                "context": {},
                "agents": {}
            })
            
            result = await completion_runner(
                state,
                prompt=message,
                agent=agent
            )
            
            # Extract response and history_id
            response = extract_heaven_response(result)
            history_id = extract_history_id_from_result(result)
            
            if not history_id:
                return "❌ Failed to get history_id from completion", False
            
            # Start the conversation
            conversation_data = start_chat(
                title=title,
                first_history_id=history_id,
                agent_name=agent.name,
                tags=tags
            )
            
            # Update current conversation
            current_conversation["conversation_id"] = conversation_data["conversation_id"]
            current_conversation["conversation_data"] = conversation_data
            
            result_text = f"""🚀 **Started New Conversation**
📝 **Title:** {title}
🆔 **ID:** {conversation_data['conversation_id']}
🏷️ **Tags:** {', '.join(tags) if tags else 'None'}

**Your message:** {message}
**Agent response:** {response}"""
            
            return result_text, True
            
        except Exception as e:
            return f"❌ Error starting conversation: {str(e)}", False
    
    async def _continue_chat(args):
        """Continue the current conversation."""
        message = args.get("message", "").strip()
        
        if not message:
            return "❌ Please provide a message", False
        
        if not current_conversation["conversation_id"]:
            return "❌ No active conversation. Please start a new chat first.", False
        
        try:
            # Get conversation context from the latest complete history only
            conv_data = current_conversation["conversation_data"]
            latest_history_id = get_latest_history(current_conversation["conversation_id"])
            
            # Build context-aware prompt with conversation context
            context_prompt = f"Continuing conversation '{conv_data['title']}'.\n\nUser message: {message}"
            
            # TODO: Could load actual conversation context from latest_history_id if needed
            # For now using simplified context with conversation title
            
            # Create HEAVEN state and get response
            state = HeavenState({
                "results": [],
                "context": {},
                "agents": {}
            })
            
            result = await completion_runner(
                state,
                prompt=context_prompt,
                agent=agent
            )
            
            # Extract response and history_id
            response = extract_heaven_response(result)
            history_id = extract_history_id_from_result(result)
            
            if not history_id:
                return "❌ Failed to get history_id from completion", False
            
            # Continue the conversation
            updated_conv = continue_chat(
                current_conversation["conversation_id"],
                history_id
            )
            
            # Update current conversation data
            current_conversation["conversation_data"] = updated_conv
            
            result_text = f"""💬 **Continued Conversation**
📝 **Title:** {conv_data['title']}
🔢 **Exchange #{updated_conv['metadata']['total_exchanges']}**

**Your message:** {message}
**Agent response:** {response}"""
            
            return result_text, True
            
        except Exception as e:
            return f"❌ Error continuing conversation: {str(e)}", False
    
    def _list_conversations(args):
        """List recent conversations."""
        limit = args.get("limit", 10)
        
        try:
            conversations = list_chats(limit=limit)
            
            if not conversations:
                return "📭 No conversations found", True
            
            result_lines = [f"📚 **Recent Conversations** (showing {len(conversations)}):"]
            result_lines.append("")
            
            for i, conv in enumerate(conversations, 1):
                tags_str = ", ".join(conv["metadata"]["tags"]) if conv["metadata"]["tags"] else "None"
                exchanges = conv["metadata"]["total_exchanges"]
                last_updated = conv["last_updated"][:19].replace("T", " ")  # Format datetime
                
                # Mark current conversation
                current_marker = " 🔹 (ACTIVE)" if conv["conversation_id"] == current_conversation["conversation_id"] else ""
                
                result_lines.append(f"{i}. **{conv['title']}**{current_marker}")
                result_lines.append(f"   🆔 ID: `{conv['conversation_id']}`")
                result_lines.append(f"   💬 Exchanges: {exchanges} | 🕐 Updated: {last_updated}")
                result_lines.append(f"   🏷️ Tags: {tags_str}")
                result_lines.append("")
            
            return "\n".join(result_lines), True
            
        except Exception as e:
            return f"❌ Error listing conversations: {str(e)}", False
    
    def _load_conversation(args):
        """Load an existing conversation."""
        conversation_id = args.get("conversation_id", "").strip()
        
        if not conversation_id:
            return "❌ Please provide a conversation_id", False
        
        try:
            conv_data = load_chat(conversation_id)
            
            if not conv_data:
                return f"❌ Conversation '{conversation_id}' not found", False
            
            # Update current conversation
            current_conversation["conversation_id"] = conversation_id
            current_conversation["conversation_data"] = conv_data
            
            tags_str = ", ".join(conv_data["metadata"]["tags"]) if conv_data["metadata"]["tags"] else "None"
            exchanges = conv_data["metadata"]["total_exchanges"]
            histories = len(conv_data["history_chain"])
            
            result_text = f"""✅ **Loaded Conversation**
📝 **Title:** {conv_data['title']}
🆔 **ID:** {conversation_id}
💬 **Exchanges:** {exchanges}
📚 **Histories:** {histories}
🏷️ **Tags:** {tags_str}
🕐 **Created:** {conv_data['created_datetime'][:19].replace('T', ' ')}
🕐 **Updated:** {conv_data['last_updated'][:19].replace('T', ' ')}

Ready to continue this conversation!"""
            
            return result_text, True
            
        except Exception as e:
            return f"❌ Error loading conversation: {str(e)}", False
    
    def _search_conversations(args):
        """Search conversations."""
        query = args.get("query", "").strip()
        
        if not query:
            return "❌ Please provide a search query", False
        
        try:
            matches = search_chats(query)
            
            if not matches:
                return f"🔍 No conversations found matching '{query}'", True
            
            result_lines = [f"🔍 **Search Results for '{query}'** ({len(matches)} found):"]
            result_lines.append("")
            
            for i, conv in enumerate(matches, 1):
                tags_str = ", ".join(conv["metadata"]["tags"]) if conv["metadata"]["tags"] else "None"
                exchanges = conv["metadata"]["total_exchanges"]
                
                result_lines.append(f"{i}. **{conv['title']}**")
                result_lines.append(f"   🆔 ID: `{conv['conversation_id']}`")
                result_lines.append(f"   💬 Exchanges: {exchanges}")
                result_lines.append(f"   🏷️ Tags: {tags_str}")
                result_lines.append("")
            
            return "\n".join(result_lines), True
            
        except Exception as e:
            return f"❌ Error searching conversations: {str(e)}", False
    
    # Register functions
    shell.register_async_function("_start_chat", _start_chat)
    shell.register_async_function("_continue_chat", _continue_chat)
    shell._list_conversations = _list_conversations
    shell._load_conversation = _load_conversation
    shell._search_conversations = _search_conversations
    
    print("🎉 HEAVEN Conversation Chat App")
    print("=" * 35)
    print("Commands:")
    print("1. start_chat     - Start new conversation")
    print("2. continue_chat  - Continue current conversation")
    print("3. list_conversations - Show recent conversations")
    print("4. load_conversation - Switch to existing conversation")
    print("5. search_conversations - Search by title/tags")
    print()
    print("Example usage:")
    print("shell.handle_command('jump 0.1.1')  # Go to start_chat")
    print('shell.handle_command(\'1 {"title": "My Chat", "message": "Hello", "tags": "test"}\')  # Start chat')
    print()
    
    # Return the shell for manual testing
    return shell


if __name__ == "__main__":
    main()