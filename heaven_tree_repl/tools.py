#!/usr/bin/env python3
"""
HEAVEN Tools for TreeShell Integration

This module contains HEAVEN tools that wrap TreeShell applications
to make them available as tools for HEAVEN agents.
"""

from typing import Dict, Any
from datetime import datetime
from heaven_base.baseheaventool import BaseHeavenTool, ToolArgsSchema, ToolResult
from . import TreeShell, AgentTreeReplMixin


class ConversationTreeShellBase(TreeShell, AgentTreeReplMixin):
    """TreeShell configured for conversation management."""
    
    def __init__(self):
        # Get conversation app configuration
        config = self._get_conversation_config()
        super().__init__(config)
        
        # Initialize agent features (no approval needed for testing)
        self.__init_agent_features__(session_id="test_agent", approval_callback=None)
    
    def _get_conversation_config(self):
        """Configuration for conversation management TreeShell."""
        return {
            "app_id": "heaven_conversation_chat",
            "domain": "conversation", 
            "role": "assistant",
            "nodes": {
                "0": {
                    "type": "Menu",
                    "prompt": "💬 HEAVEN Conversation Chat",
                    "description": "Chat with conversation management",
                    "signature": "chat() -> conversation_options",
                    "options": {
                        "1": "0.1",  # start_chat
                        "2": "0.2",  # continue_chat
                        "3": "0.3",  # list_conversations
                        "4": "0.4",  # load_conversation
                        "5": "0.5"   # search_conversations
                    }
                },
                "0.1": {
                    "type": "Callable",
                    "prompt": "Start New Chat",
                    "description": "Start a new conversation with a title and first message",
                    "signature": "start_chat(title: str, message: str, tags: str) -> conversation_result",
                    "function_name": "_start_chat_simple",
                    "args_schema": {
                        "title": "str", 
                        "message": "str",
                        "tags": "str"  # comma-separated
                    }
                },
                "0.2": {
                    "type": "Callable",
                    "prompt": "Continue Chat",
                    "description": "Continue existing conversation with new message",
                    "signature": "continue_chat(message: str) -> chat_response",
                    "function_name": "_continue_chat_simple",
                    "args_schema": {
                        "message": "str"
                    }
                },
                "0.3": {
                    "type": "Callable",
                    "prompt": "List Conversations",
                    "description": "Show available conversations",
                    "signature": "list_conversations(limit: int) -> conversation_list",
                    "function_name": "_list_conversations_simple",
                    "args_schema": {
                        "limit": "int"
                    }
                },
                "0.4": {
                    "type": "Callable",
                    "prompt": "Load Conversation",
                    "description": "Switch to existing conversation",
                    "signature": "load_conversation(conversation_id: str) -> load_result",
                    "function_name": "_load_conversation_simple",
                    "args_schema": {
                        "conversation_id": "str"
                    }
                },
                "0.5": {
                    "type": "Callable",
                    "prompt": "Search Conversations",
                    "description": "Search conversations by query",
                    "signature": "search_conversations(query: str) -> search_results",
                    "function_name": "_search_conversations_simple",
                    "args_schema": {
                        "query": "str"
                    }
                }
            }
        }
    
    # Simplified implementations for testing
    def _start_chat_simple(self, args):
        """Simplified start chat for testing."""
        title = args.get("title", "").strip()
        message = args.get("message", "").strip()
        tags = args.get("tags", "").strip()
        
        if not title or not message:
            return {"error": "Title and message required"}, False
            
        return {
            "action": "start_chat",
            "title": title,
            "message": message,
            "tags": tags,
            "result": f"Started conversation '{title}' with message: {message[:50]}..."
        }, True
    
    def _continue_chat_simple(self, args):
        """Simplified continue chat for testing.""" 
        message = args.get("message", "").strip()
        
        if not message:
            return {"error": "Message required"}, False
            
        return {
            "action": "continue_chat",
            "message": message,
            "result": f"Continued conversation with: {message[:50]}..."
        }, True
    
    def _list_conversations_simple(self, args):
        """Simplified list conversations for testing."""
        limit = args.get("limit", 10)
        
        return {
            "action": "list_conversations",
            "limit": limit,
            "conversations": [
                {"id": "conv_1", "title": "Test Conversation 1"},
                {"id": "conv_2", "title": "Test Conversation 2"}
            ],
            "result": f"Found 2 conversations (limit: {limit})"
        }, True
    
    def _load_conversation_simple(self, args):
        """Simplified load conversation for testing."""
        conversation_id = args.get("conversation_id", "").strip()
        
        if not conversation_id:
            return {"error": "Conversation ID required"}, False
            
        return {
            "action": "load_conversation", 
            "conversation_id": conversation_id,
            "result": f"Loaded conversation: {conversation_id}"
        }, True
    
    def _search_conversations_simple(self, args):
        """Simplified search conversations for testing."""
        query = args.get("query", "").strip()
        
        if not query:
            return {"error": "Search query required"}, False
            
        return {
            "action": "search_conversations",
            "query": query,
            "results": [
                {"id": "conv_1", "title": "Test Conversation 1", "relevance": 0.8}
            ],
            "result": f"Found 1 conversation matching '{query}'"
        }, True


class ConversationTreeShellToolArgsSchema(ToolArgsSchema):
    arguments: Dict[str, Dict[str, Any]] = {
        "command": {
            "name": "command",
            "type": "str", 
            "description": "TreeShell command to execute (e.g., 'jump 0.1', '1 {\"title\": \"My Chat\", \"message\": \"Hello\"}', or '' for menu)",
            "required": True
        }
    }


class TreeShellSessionManager:
    """Manages a single persistent TreeShell session."""
    
    def __init__(self):
        self.shell = None
    
    def get_shell(self) -> ConversationTreeShellBase:
        """Get the persistent shell instance."""
        if self.shell is None:
            self.shell = ConversationTreeShellBase()
        return self.shell


async def conversation_treeshell_func(command: str) -> str:
    """Execute a command in the conversation TreeShell."""
    
    # Get the persistent shell instance
    shell = ConversationTreeShellTool.get_session_manager().get_shell()
    
    # Execute command
    result = await shell.handle_command(command)
    
    # Format the result
    if isinstance(result, dict):
        if result.get("error"):
            return f"❌ Error: {result['error']}"
        else:
            # Format successful result
            return f"✅ TreeShell Result:\n{result}"
    else:
        return str(result)


class ConversationTreeShellTool(BaseHeavenTool):
    name = "ConversationTreeShellTool"
    description = """Navigate and execute commands in a conversation management TreeShell with persistent state.
    
This tool provides access to a TreeShell interface for managing conversations with:
- Starting new conversations
- Continuing existing conversations  
- Listing and searching conversations
- Loading specific conversations

Session Management:
- Tool maintains one persistent TreeShell session automatically
- Navigation state and session variables persist across calls

Commands:
- '' (empty) - Show current menu/options
- 'jump 0.1' - Navigate to start_chat
- '1 {"title": "My Chat", "message": "Hello", "tags": "test"}' - Execute with arguments
- 'back' - Go back to previous position
- 'menu' - Show current node menu

Example workflow:
1. '' - Show main menu
2. 'jump 0.1' - Go to start_chat
3. '1 {"title": "Test Chat", "message": "Hello world", "tags": "test"}' - Start conversation
4. 'jump 0.2' - Go to continue_chat
5. '1 {"message": "How are you?"}' - Continue conversation
"""
    func = conversation_treeshell_func
    args_schema = ConversationTreeShellToolArgsSchema
    is_async = True
    
    _session_manager = None  # Class-level singleton
    
    @classmethod
    def get_session_manager(cls):
        """Get or create the persistent session manager."""
        if cls._session_manager is None:
            cls._session_manager = TreeShellSessionManager()
        return cls._session_manager