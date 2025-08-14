#!/usr/bin/env python3
"""
Proof of Concept: Agent App Generation Pipeline

This demonstrates how a coder agent can read TreeShell documentation
and generate complete applications from natural language descriptions.
"""

import os
import json
from typing import Dict, List, Any


class TreeShellAppGenerator:
    """
    Agent that generates TreeShell applications from natural language.
    
    This is a proof of concept showing how we can teach an agent to:
    1. Read our documentation and patterns
    2. Understand TreeShell architecture  
    3. Generate complete apps from descriptions
    """
    
    def __init__(self):
        """Initialize the app generator with TreeShell knowledge."""
        self.knowledge_base = {
            "config_system": self._load_config_knowledge(),
            "shell_patterns": self._load_shell_patterns(), 
            "heaven_tools": self._load_heaven_tools_catalog(),
            "example_apps": self._load_example_apps()
        }
    
    def generate_app(self, description: str) -> Dict[str, Any]:
        """
        Generate a complete TreeShell app from natural language description.
        
        Args:
            description: Natural language description of desired app
            
        Returns:
            Dict containing all files, configs, and metadata for the app
        """
        print(f"🤖 Generating TreeShell app from: {description}")
        
        # Step 1: Analyze requirements
        requirements = self._analyze_requirements(description)
        print(f"📋 Requirements analyzed: {requirements['app_type']}")
        
        # Step 2: Design architecture
        architecture = self._design_architecture(requirements)
        print(f"🏗️ Architecture designed: {architecture['shell_type']}")
        
        # Step 3: Select tools
        tools = self._select_tools(architecture)
        print(f"🛠️ Tools selected: {len(tools)} tools")
        
        # Step 4: Generate configs
        configs = self._generate_configs(architecture, tools)
        print(f"⚙️ Configs generated: {len(configs)} config files")
        
        # Step 5: Generate code
        code = self._generate_code(architecture, configs)
        print(f"💻 Code generated: {len(code)} code files")
        
        # Step 6: Package as MCP
        mcp = self._package_as_mcp(code, configs, requirements)
        print(f"📦 MCP package created")
        
        return {
            "metadata": requirements,
            "architecture": architecture,
            "tools": tools,
            "configs": configs,
            "code": code,
            "mcp": mcp
        }
    
    def _analyze_requirements(self, description: str) -> Dict[str, Any]:
        """Analyze natural language description to extract requirements."""
        # In real implementation, this would use an LLM
        # For now, simple keyword matching
        
        requirements = {
            "description": description,
            "app_type": "general",
            "features": [],
            "user_types": ["user"],
            "data_types": [],
            "integrations": []
        }
        
        # Detect app type
        if "chat" in description.lower() or "conversation" in description.lower():
            requirements["app_type"] = "chat_system"
            requirements["features"].extend(["messaging", "history", "users"])
            
        elif "support" in description.lower() or "ticket" in description.lower():
            requirements["app_type"] = "support_system" 
            requirements["features"].extend(["tickets", "routing", "agents"])
            requirements["user_types"].extend(["agent", "manager"])
            
        elif "project" in description.lower() or "task" in description.lower():
            requirements["app_type"] = "project_management"
            requirements["features"].extend(["tasks", "assignments", "tracking"])
            
        # Detect features
        feature_keywords = {
            "search": "search",
            "analytics": "analytics", 
            "notifications": "notifications",
            "workflow": "workflow_automation",
            "approval": "approval_process"
        }
        
        for keyword, feature in feature_keywords.items():
            if keyword in description.lower():
                requirements["features"].append(feature)
        
        return requirements
    
    def _design_architecture(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Design TreeShell architecture based on requirements."""
        architecture = {
            "shell_type": "UserTreeShell",  # Default
            "config_layers": ["base", "user"],
            "families": ["system"],
            "navigation": {},
            "workflows": []
        }
        
        # Choose shell type based on user types
        if "agent" in requirements["user_types"]:
            if "user" in requirements["user_types"]:
                architecture["shell_type"] = "FullstackTreeShell"
                architecture["config_layers"] = ["base", "agent", "user"]
            else:
                architecture["shell_type"] = "AgentTreeShell"
                architecture["config_layers"] = ["base", "agent"]
        
        # Add families based on app type
        app_families = {
            "chat_system": ["conversations", "users"],
            "support_system": ["tickets", "agents", "knowledge_base"],
            "project_management": ["projects", "tasks", "teams"]
        }
        
        if requirements["app_type"] in app_families:
            architecture["families"].extend(app_families[requirements["app_type"]])
        
        return architecture
    
    def _select_tools(self, architecture: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Select HEAVEN tools based on architecture needs."""
        # Default tools everyone needs
        tools = [
            {"name": "NetworkEditTool", "purpose": "file_operations"},
            {"name": "BashTool", "purpose": "system_operations"}
        ]
        
        # Add tools based on families
        family_tools = {
            "conversations": [
                {"name": "ConversationTool", "purpose": "chat_management"},
                {"name": "HistoryTool", "purpose": "message_history"}
            ],
            "tickets": [
                {"name": "TicketTool", "purpose": "ticket_management"}, 
                {"name": "RoutingTool", "purpose": "assignment_logic"}
            ],
            "projects": [
                {"name": "ProjectTool", "purpose": "project_management"},
                {"name": "TaskTool", "purpose": "task_tracking"}
            ]
        }
        
        for family in architecture["families"]:
            if family in family_tools:
                tools.extend(family_tools[family])
        
        return tools
    
    def _generate_configs(self, architecture: Dict[str, Any], tools: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate all config files for the app."""
        configs = {}
        
        # Generate user config based on shell type and tools
        for layer in architecture["config_layers"]:
            if layer != "base":  # Base is system-level
                config = self._generate_user_config(layer, architecture, tools)
                configs[f"user_{layer}_config.json"] = json.dumps(config, indent=2)
        
        # Generate nav config
        nav_config = self._generate_nav_config(architecture)
        configs["nav_config.json"] = json.dumps(nav_config, indent=2)
        
        # Generate zone config if needed
        if architecture["shell_type"] in ["UserTreeShell", "FullstackTreeShell"]:
            zone_config = self._generate_zone_config(architecture)
            configs["user_zone_config.json"] = json.dumps(zone_config, indent=2)
        
        return configs
    
    def _generate_user_config(self, layer: str, architecture: Dict[str, Any], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a user config file for a specific layer."""
        return {
            "override_nodes": {},
            "add_nodes": self._generate_nodes_for_tools(tools),
            "exclude_nodes": [],
            f"app_id": f"{architecture.get('app_name', 'generated')}_app",
            "about_app": f"Generated {layer} shell application"
        }
    
    def _generate_nodes_for_tools(self, tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate TreeShell nodes for selected tools."""
        nodes = {}
        
        for i, tool in enumerate(tools, 1):
            node_id = f"tool_{tool['name'].lower()}"
            nodes[node_id] = {
                "type": "Callable",
                "prompt": f"Use {tool['name']}",
                "description": f"Execute {tool['name']} for {tool['purpose']}",
                "function_name": f"_execute_{tool['name'].lower()}",
                "is_async": True,
                "args_schema": {
                    "tool_name": tool['name'],
                    "parameters": "$user_parameters"  # Will be filled at runtime
                }
            }
        
        return nodes
    
    def _generate_nav_config(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Generate navigation configuration."""
        return {
            "nav_tree_order": architecture["families"],
            "coordinate_mapping": {
                f"0.{i+1}": family for i, family in enumerate(architecture["families"])
            }
        }
    
    def _generate_zone_config(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Generate zone configuration for user interface."""
        return {
            "active_zone": "main_zone",
            "custom_zones": {
                "main_zone": {
                    "name": "Main Application Zone",
                    "zone_tree": architecture["families"]
                }
            }
        }
    
    def _generate_code(self, architecture: Dict[str, Any], configs: Dict[str, str]) -> Dict[str, str]:
        """Generate Python code for the TreeShell application."""
        code = {}
        
        # Generate main shell class
        shell_code = self._generate_shell_class(architecture)
        code[f"{architecture.get('app_name', 'generated')}_shell.py"] = shell_code
        
        # Generate MCP server
        mcp_server_code = self._generate_mcp_server(architecture)
        code["mcp_server.py"] = mcp_server_code
        
        # Generate setup.py
        setup_code = self._generate_setup_py(architecture)
        code["setup.py"] = setup_code
        
        return code
    
    def _generate_shell_class(self, architecture: Dict[str, Any]) -> str:
        """Generate the main TreeShell class for the app."""
        shell_type = architecture["shell_type"]
        app_name = architecture.get('app_name', 'Generated')
        
        return f'''#!/usr/bin/env python3
"""
{app_name} TreeShell Application
Generated automatically by HEAVEN TreeShell App Generator
"""

from heaven_tree_repl import {shell_type}


class {app_name}Shell({shell_type}):
    """
    {app_name} application built on TreeShell.
    
    This shell provides a tree-based navigation interface for
    managing {app_name.lower()} operations through the HEAVEN ecosystem.
    """
    
    def __init__(self, user_config_path: str = None):
        """
        Initialize the {app_name} shell.
        
        Args:
            user_config_path: Path to user configuration directory
        """
        # Load user configs if provided
        config = {{}}
        if user_config_path:
            config = self._load_user_configs_from_path(user_config_path)
        
        super().__init__(config)
    
    async def run_app(self):
        """Run the {app_name} application."""
        print(f"🌳 Starting {app_name} TreeShell...")
        print(f"Use 'nav' to see available options")
        print(f"Use 'lang' to learn TreeShell syntax")
        
        while True:
            try:
                command = input(f"<<[🔮‍🌳 {app_name}]>> ")
                if command.lower() in ['exit', 'quit']:
                    break
                
                result = await self.handle_command(command)
                if result.get('content'):
                    print(result['content'])
                    
            except KeyboardInterrupt:
                print("\\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {{e}}")


if __name__ == "__main__":
    import asyncio
    
    async def main():
        shell = {app_name}Shell()
        await shell.run_app()
    
    asyncio.run(main())
'''
    
    def _generate_mcp_server(self, architecture: Dict[str, Any]) -> str:
        """Generate MCP server for the application."""
        app_name = architecture.get('app_name', 'generated')
        
        return f'''#!/usr/bin/env python3
"""
{app_name.title()} MCP Server
Generated automatically by HEAVEN TreeShell App Generator
"""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from {app_name}_shell import {app_name.title()}Shell


class {app_name.title()}MCPServer:
    """MCP Server for {app_name.title()} application."""
    
    def __init__(self):
        self.shell = None
    
    async def run_shell_command(self, command: str) -> dict:
        """Execute command in {app_name.title()}Shell."""
        if not self.shell:
            self.shell = {app_name.title()}Shell()
        
        try:
            result = await self.shell.handle_command(command)
            return {{"success": True, "result": result}}
        except Exception as e:
            return {{"success": False, "error": str(e)}}


async def serve():
    """Main MCP server function."""
    server = Server("{app_name}-treeshell")
    app_server = {app_name.title()}MCPServer()
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="run_shell_command",
                description="Execute commands in {app_name.title()} TreeShell interface",
                inputSchema={{
                    "type": "object",
                    "properties": {{
                        "command": {{"type": "string", "description": "TreeShell command to execute"}}
                    }},
                    "required": ["command"]
                }}
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "run_shell_command":
            result = await app_server.run_shell_command(arguments["command"])
            return [TextContent(type="text", text=str(result))]
        
        raise ValueError(f"Unknown tool: {{name}}")
    
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)


if __name__ == "__main__":
    asyncio.run(serve())
'''
    
    def _generate_setup_py(self, architecture: Dict[str, Any]) -> str:
        """Generate setup.py for the application."""
        app_name = architecture.get('app_name', 'generated')
        
        return f'''#!/usr/bin/env python3
"""Setup script for {app_name} TreeShell application."""

from setuptools import setup, find_packages

setup(
    name="{app_name}-treeshell",
    version="1.0.0",
    description="{app_name.title()} application built on HEAVEN TreeShell",
    author="Generated by HEAVEN TreeShell App Generator",
    packages=find_packages(),
    install_requires=[
        "heaven-tree-repl>=0.1.33",
        "mcp>=0.1.0"
    ],
    entry_points={{
        "console_scripts": [
            "{app_name}=={app_name}_shell:{app_name.title()}Shell.run_app",
        ],
    }},
    python_requires=">=3.8",
)
'''
    
    def _package_as_mcp(self, code: Dict[str, str], configs: Dict[str, str], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Package the generated app as an MCP server."""
        return {
            "mcp_manifest": {
                "name": f"{requirements.get('app_name', 'generated')}-treeshell",
                "version": "1.0.0", 
                "description": requirements["description"],
                "tools": ["run_shell_command"],
                "dependencies": ["heaven-tree-repl>=0.1.33"]
            },
            "installation_instructions": f"""
# Install {requirements.get('app_name', 'Generated')} TreeShell App

1. Clone or download this generated application
2. Install dependencies:
   pip install -r requirements.txt
   
3. Run the application:
   python {requirements.get('app_name', 'generated')}_shell.py
   
4. Or use as MCP server:
   python mcp_server.py
"""
        }
    
    def _load_config_knowledge(self) -> Dict[str, Any]:
        """Load knowledge about TreeShell config system."""
        return {
            "config_files": [
                "system_base_config.json", "user_base_config.json",
                "system_agent_config.json", "user_agent_config.json", 
                "system_user_config.json", "user_user_config.json",
                "nav_config.json", "zone_config.json"
            ],
            "user_config_structure": {
                "override_nodes": "dict - modify existing nodes",
                "add_nodes": "dict - add new nodes", 
                "exclude_nodes": "list - remove nodes entirely"
            }
        }
    
    def _load_shell_patterns(self) -> Dict[str, Any]:
        """Load knowledge about TreeShell patterns."""
        return {
            "shell_types": {
                "TreeShell": "Base shell with core navigation",
                "AgentTreeShell": "AI agent with quarantine restrictions",
                "UserTreeShell": "Human interface with agent management", 
                "FullstackTreeShell": "Complete system with all capabilities"
            },
            "common_mixins": [
                "MetaOperationsMixin", "PathwayManagementMixin",
                "CommandHandlersMixin", "RSIAnalysisMixin"
            ]
        }
    
    def _load_heaven_tools_catalog(self) -> List[Dict[str, Any]]:
        """Load catalog of available HEAVEN tools."""
        return [
            {"name": "NetworkEditTool", "category": "file_operations"},
            {"name": "BashTool", "category": "system_operations"},
            {"name": "ConversationTool", "category": "chat_management"},
            {"name": "TicketTool", "category": "support_systems"},
            {"name": "ProjectTool", "category": "project_management"},
            {"name": "AnalyticsTool", "category": "data_analysis"}
        ]
    
    def _load_example_apps(self) -> List[Dict[str, Any]]:
        """Load examples of successful TreeShell applications."""
        return [
            {
                "name": "Conversation Management System",
                "type": "chat_system",
                "features": ["messaging", "history", "users"],
                "shell_type": "UserTreeShell"
            }
        ]


def demo_app_generation():
    """Demonstrate the app generation pipeline."""
    generator = TreeShellAppGenerator()
    
    # Example: Generate a customer support system
    description = """
    Build me a customer support chat system with:
    - Ticket creation and routing
    - Agent assignment  
    - Knowledge base search
    - Chat history management
    - Escalation workflows
    """
    
    app = generator.generate_app(description)
    
    print("\\n" + "="*50)
    print("🎉 GENERATED APP STRUCTURE:")
    print("="*50)
    
    print("\\n📁 Configuration Files:")
    for filename in app["configs"].keys():
        print(f"  - {filename}")
    
    print("\\n💻 Code Files:")
    for filename in app["code"].keys():
        print(f"  - {filename}")
    
    print("\\n🛠️ Selected Tools:")
    for tool in app["tools"]:
        print(f"  - {tool['name']} ({tool['purpose']})")
    
    print("\\n🏗️ Architecture:")
    print(f"  - Shell Type: {app['architecture']['shell_type']}")
    print(f"  - Config Layers: {', '.join(app['architecture']['config_layers'])}")
    print(f"  - Families: {', '.join(app['architecture']['families'])}")
    
    return app


if __name__ == "__main__":
    demo_app_generation()