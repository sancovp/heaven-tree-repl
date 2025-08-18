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
    INSTANTIATE_COMPUTATIONAL_SPACE = "instantiate_computational_space"


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
    
    def _find_latest_user_config(self, heaven_data_dir: str) -> str:
        """Find the latest user config directory with dev customizations."""
        try:
            if not os.path.exists(heaven_data_dir):
                return None
                
            # Look for directories that match the pattern: app_name_v1_0, etc.
            config_dirs = []
            for item in os.listdir(heaven_data_dir):
                item_path = os.path.join(heaven_data_dir, item)
                if os.path.isdir(item_path):
                    # Check if it has a configs subdirectory
                    configs_path = os.path.join(item_path, 'configs')
                    if os.path.exists(configs_path):
                        config_dirs.append(configs_path)
            
            if not config_dirs:
                return None
                
            # Return the most recently modified config directory
            latest_config_dir = max(config_dirs, key=lambda x: os.path.getmtime(x))
            return latest_config_dir
            
        except Exception as e:
            print(f"Warning: Could not find user config directory: {e}")
            return None
    
    async def _initialize_shell(self):
        """Initialize the conversation management shell"""
        try:
            # Set HEAVEN_DATA_DIR if not set
            if not os.getenv('HEAVEN_DATA_DIR'):
                os.environ['HEAVEN_DATA_DIR'] = '/tmp/heaven_data'
                os.makedirs('/tmp/heaven_data', exist_ok=True)
            
            # Create and initialize UserTreeShell with user's dev customizations
            # Find the user's latest dev config directory from HEAVEN_DATA_DIR
            heaven_data_dir = os.getenv('HEAVEN_DATA_DIR', '/tmp/heaven_data')
            user_config_path = self._find_latest_user_config(heaven_data_dir)
            
            if user_config_path:
                print(f"Loading user customizations from: {user_config_path}")
                shell_instance = UserTreeShell(user_config_path=user_config_path)
            else:
                print("No user customizations found, using clean system configs")
                shell_instance = UserTreeShell()
                
            self.shell = await shell_instance.main()
            
        except Exception as e:
            print(f"Warning: Could not initialize conversation shell: {e}")
            self.shell = None
    
    async def instantiate_computational_space(self, command: str) -> dict:
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
    server = Server("heaven-tree-repl")
    treeshell_server = TreeShellMCPServer()
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available TreeShell tools"""
        return [
            Tool(
                name=TreeShellTools.INSTANTIATE_COMPUTATIONAL_SPACE.value,
                description="""
                Run commands in the TreeShell conversation management interface.
                
                TreeShell provides tree-based navigation with persistent state management.
                
                ## Core Navigation Commands:
                - '' (empty) - Show current menu/options
                - 'jump X.Y.Z' - Navigate to specific coordinate (e.g., 'jump 0.1.1' numeric address or jump 'system' semantic address)
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
                
                ## Chain Execution:
                - 'chain COORDS' - Execute multiple coordinates in sequence (e.g., 'chain <address> {...} -> <address2> {...}' (supports more than 2 steps))
                
                ## Conversation Management Structure:
                - start_chat (title, message, tags)
                - continue_chat (message)
                - list_conversations (limit)
                - load_conversation (conversation_id)
                - search_conversations (query)
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
                case TreeShellTools.INSTANTIATE_COMPUTATIONAL_SPACE.value:
                    command = arguments.get("command", "")
                    result = await treeshell_server.instantiate_computational_space(command)
                    
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