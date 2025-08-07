"""
TreeShell MCP Server - Tree-based navigation REPL for AI agents
"""
import json
import os
from enum import Enum
from typing import Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from mcp.shared.exceptions import McpError

# Import TreeShell components
from heaven_tree_repl import UserTreeShell, render_response


class TreeShellTools(str, Enum):
    """Available TreeShell tools"""
    RUN_CONVERSATION_SHELL = "run_conversation_shell"


class TreeShellMCPServer:
    """
    TreeShell MCP Server
    
    Provides a single tool to run the conversation management TreeShell.
    This gives AI agents access to the complete tree navigation interface
    for managing conversations with HEAVEN framework integration.
    """
    
    def __init__(self):
        """Initialize the TreeShell MCP server"""
        # Initialize the conversation shell
        self.shell = None
    
    async def _initialize_shell(self):
        """Initialize the conversation management shell"""
        try:
            # Set HEAVEN_DATA_DIR if not set
            if not os.getenv('HEAVEN_DATA_DIR'):
                os.environ['HEAVEN_DATA_DIR'] = '/tmp/heaven_data'
                os.makedirs('/tmp/heaven_data', exist_ok=True)
            
            # Create and initialize UserTreeShell using its own main method
            shell_instance = UserTreeShell({})
            self.shell = await shell_instance.main()
            
        except Exception as e:
            print(f"Warning: Could not initialize conversation shell: {e}")
            self.shell = None
    
    async def run_conversation_shell(self, command: str) -> dict:
        """
        Run a command in the conversation management TreeShell.
        
        Args:
            command: TreeShell command to execute
            
        Returns:
            Dict with command result
        """
        if not self.shell:
            await self._initialize_shell()
        
        if not self.shell:
            return {
                "success": False,
                "error": "TreeShell not initialized. Check HEAVEN_DATA_DIR and dependencies."
            }
        
        try:
            # Handle command through TreeShell
            result = await self.shell.handle_command(command)
            
            # Render the result using TreeShell's renderer
            rendered_output = render_response(result)
            
            return {
                "success": True,
                "command": command,
                "rendered_output": rendered_output,
                "raw_result": result  # Keep raw result for debugging if needed
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing command '{command}': {str(e)}"
            }


async def serve() -> None:
    """Main MCP server function"""
    server = Server("heaven-treeshell")
    treeshell_server = TreeShellMCPServer()
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available TreeShell tools"""
        return [
            Tool(
                name=TreeShellTools.RUN_CONVERSATION_SHELL.value,
                description="""
                Run commands in the TreeShell conversation management interface.
                
                TreeShell provides tree-based navigation with persistent state management.
                
                ## Core Navigation Commands:
                - '' (empty) - Show current menu/options
                - 'jump X.Y.Z' - Navigate to specific coordinate (e.g., 'jump 0.1.1')
                - 'back' - Go back to previous position
                - 'menu' - Show current node menu
                - 'exit' - Exit TreeShell
                
                ## Action Execution:
                - NUMBER - Execute numbered menu option (e.g., '1', '2', '3')
                - NUMBER + JSON - Execute with arguments (e.g., '1 {"title": "Chat", "message": "Hello"}')
                - NUMBER, args={...} - Alternative argument format
                
                ## Pathway Management:
                - 'build_pathway' - Start recording a pathway
                - 'save_emergent_pathway NAME' - Save recorded pathway with name
                - 'save_emergent_pathway_from_history NAME' - Save pathway from execution history
                - 'follow_established_pathway NAME' - Execute saved pathway
                - 'show_execution_history' - View command history
                
                ## Pattern Analysis (RSI System):
                - 'analyze_patterns' - Analyze execution patterns for optimization
                - 'crystallize_pattern NAME' - Create reusable pattern from analysis
                - 'rsi_insights' - Show learning insights from execution
                
                ## Chain Execution:
                - 'chain COORDS' - Execute multiple coordinates in sequence (e.g., 'chain 0.1.1,0.1.2')
                
                ## Conversation Management Structure:
                - 0.1.1 = start_chat (title, message, tags)
                - 0.1.2 = continue_chat (message)
                - 0.1.3 = list_conversations (limit)
                - 0.1.4 = load_conversation (conversation_id)
                - 0.1.5 = search_conversations (query)
                
                ## Example Workflow:
                1. '' - Show main menu
                2. 'jump 0.1.1' - Go to start_chat
                3. '1 {"title": "My Chat", "message": "Hello", "tags": "test"}' - Start conversation
                4. 'jump 0.1.2' - Go to continue_chat
                5. '1 {"message": "How are you?"}' - Continue conversation
                6. 'jump 0.1.3' - Go to list_conversations
                7. '1 {"limit": 5}' - List recent conversations
                """,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "TreeShell command to execute (e.g., 'jump 0.1.1', '1 {\"message\": \"hello\"}', or '' for menu)",
                        }
                    },
                    "required": ["command"],
                },
            ),
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
        """Handle tool calls"""
        try:
            match name:
                case TreeShellTools.RUN_CONVERSATION_SHELL.value:
                    command = arguments.get("command", "")
                    result = await treeshell_server.run_conversation_shell(command)
                    
                    # Return only the rendered output, not the full JSON
                    if result.get("success"):
                        output_text = result.get("rendered_output", "No output available")
                    else:
                        output_text = f"❌ Error: {result.get('error', 'Unknown error')}"
                
                case _:
                    raise ValueError(f"Unknown tool: {name}")
            
            return [
                TextContent(type="text", text=output_text)
            ]
        
        except Exception as e:
            raise ValueError(f"Error processing TreeShell operation: {str(e)}")
    
    # Initialize server and run
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)


if __name__ == "__main__":
    import asyncio
    asyncio.run(serve())