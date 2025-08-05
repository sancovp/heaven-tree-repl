"""
HEAVEN Tree REPL - Hierarchical Embodied Autonomously Validating Evolution Network Tree REPL

A modular tree navigation system with persistent state, pathway recording, 
and agent management capabilities.
"""

__version__ = "0.1.0"

# Import main classes for public API
from .base import TreeShellBase
from .display_brief import DisplayBrief
from .renderer import render_response

# Import mixins for advanced usage
from .meta_operations import MetaOperationsMixin
from .pathway_management import PathwayManagementMixin
from .command_handlers import CommandHandlersMixin
from .rsi_analysis import RSIAnalysisMixin
from .execution_engine import ExecutionEngineMixin
from .agent_management import AgentTreeReplMixin, UserTreeReplMixin, TreeReplFullstackMixin
from .approval_system import ApprovalQueue

# Import MCP generator
from .mcp_generator import generate_mcp_from_config, generate_mcp_from_dict, TreeShellMCPConfig, MCPGenerator

# Main TreeShell class combining all functionality
class TreeShell(
    TreeShellBase,
    MetaOperationsMixin,
    PathwayManagementMixin,
    CommandHandlersMixin,
    RSIAnalysisMixin,
    ExecutionEngineMixin
):
    """
    Complete TreeShell implementation combining all modules.
    
    Provides geometric tree navigation with live variable persistence,
    pathway recording and templates, RSI analysis, and comprehensive
    command handling.
    """
    
    def __init__(self, graph_config: dict):
        """Initialize TreeShell with graph configuration."""
        super().__init__(graph_config)
    
    def _manage_pathways(self, final_args: dict) -> tuple:
        """Show pathway management interface."""
        pathways_info = {
            "saved_pathways": len(self.saved_pathways),
            "saved_templates": len(self.saved_templates),
            "pathway_list": list(self.saved_pathways.keys()),
            "ontology_domains": len(self.graph_ontology["domains"]),
            "crystallization_history": len(self.graph_ontology["crystallization_history"])
        }
        
        return pathways_info, True
    
    # === Documentation Functions ===
    
    def _docs_execution_syntax(self, final_args: dict) -> tuple:
        """Show execution syntax documentation."""
        docs = """📋 **Execution Syntax Guide**

When executing callable nodes, use these argument patterns:

**With Arguments (Dictionary):**
• `1 {"name": "Alice", "age": 30}` → calls func({"name": "Alice", "age": 30})
• `1 {"message": "Hello World"}` → calls func({"message": "Hello World"})

**Empty Arguments (Empty Dictionary):**  
• `1 {}` → calls func({}) - function receives empty dict

**No Arguments (Empty Parentheses):**
• `1 ()` → calls func() - function called with zero arguments
• Use this for functions like os.getcwd() that take no parameters

**Examples:**
• Math function: `1 {"a": 5, "b": 3}`
• Status check: `1 {}`  
• Get directory: `1 ()`

**Jump with Arguments:**
• `jump 0.1.5 {"data": "value"}` → navigate and execute with args
• `jump 0.1.5 ()` → navigate and execute with no args"""
        
        return docs, True
    
    def _docs_callable_nodes(self, final_args: dict) -> tuple:
        """Show callable nodes documentation."""
        docs = """🔧 **Callable Nodes Guide**

Create callable nodes using add_node (0.0.2.10) with 3 approaches:

**1. Import Existing Function:**
```json
{
  "type": "Callable",
  "prompt": "Get Directory", 
  "function_name": "_get_dir",
  "is_async": false,
  "import_path": "os",
  "import_object": "getcwd"
}
```

**2. Dynamic Function Code:**
```json
{
  "type": "Callable",
  "prompt": "System Info",
  "function_name": "_sys_info", 
  "is_async": false,
  "function_code": "def _sys_info(args): import os; return f'Dir: {os.getcwd()}', True"
}
```

**3. Use Existing Function:**
```json
{
  "type": "Callable",
  "prompt": "List Variables",
  "function_name": "_meta_list_vars",
  "is_async": false
}
```

**Required Fields:**
• `type`: "Callable"
• `prompt`: Display name
• `function_name`: Internal function name
• `is_async`: true/false for async handling

**Execution:** Use syntax from 0.2.1 (Execution Syntax)"""
        
        return docs, True
    
    def _docs_navigation(self, final_args: dict) -> tuple:
        """Show navigation documentation.""" 
        docs = """🧭 **Navigation Commands**

**Basic Navigation:**
• `1`, `2`, `3` → Navigate to menu options
• `back` → Go back one level
• `menu` → Go to nearest menu (find closest .0 node)
• `exit` → Exit TreeShell

**Jump Commands:**
• `jump 0.1.5` → Navigate directly to coordinate
• `jump 0.1.5 {"arg": "value"}` → Navigate and execute with args
• `jump 0.1.5 ()` → Navigate and execute with no args

**Chain Execution:**
• `chain 0.1.1 {} -> 0.1.2 {"data": "test"}` → Execute sequence
• Results from step1 available as variables in step2

**Universal Commands Available Everywhere:**
• jump, chain, build_pathway, save_emergent_pathway
• follow_established_pathway, show_execution_history
• analyze_patterns, crystallize_pattern, rsi_insights

**Coordinate System:**
• Every position has implicit .0 (menu/introspect)  
• 0 = root, 0.0 = settings, 0.1 = domain, 0.2 = docs
• Navigate hierarchically: 0 → 0.1 → 0.1.3 → 0.1.3.2"""
        
        return docs, True
    
    def _docs_pathways(self, final_args: dict) -> tuple:
        """Show pathway system documentation."""
        docs = """🛤️ **Pathway System**

**Recording Pathways:**
• `build_pathway` → Start recording your actions
• Navigate and execute commands (they get recorded)
• `save_emergent_pathway mypath` → Save recorded pathway

**From History:**
• `save_emergent_pathway_from_history mypath [0,1,2]` → Create from specific steps
• `save_emergent_pathway_from_history mypath [0-5]` → Create from range
• `show_execution_history` → See available steps

**Using Pathways:**
• `follow_established_pathway` → Show all pathways
• `follow_established_pathway mypath {"arg": "value"}` → Execute with args
• `follow_established_pathway domain=math` → Query by domain
• `follow_established_pathway tags=arithmetic` → Query by tags

**Analysis (RSI System):**
• `analyze_patterns` → Find optimization opportunities
• `crystallize_pattern mypattern` → Create reusable pattern
• `rsi_insights` → Show learning insights

**Pathway Management:** 
• Navigate to 0.0.1 for pathway management interface
• View saved pathways, templates, and ontology data"""
        
        return docs, True
    
    def _docs_meta_operations(self, final_args: dict) -> tuple:
        """Show meta operations documentation."""
        docs = """⚙️ **Meta Operations (0.0.2)**

**Session Variables:**
• `save_var` → Store value: {"name": "myvar", "value": "data"}
• `get_var` → Retrieve: {"name": "myvar"}  
• `append_to_var` → Add to list/string: {"name": "myvar", "value": "more"}
• `delete_var` → Remove: {"name": "myvar"}
• `list_vars` → Show all variables: {}

**File Operations:**
• `save_to_file` → Write var to file: {"filename": "data.json", "var_name": "myvar"}
• `load_from_file` → Read file to var: {"filename": "data.json", "var_name": "loaded"}
• `export_session` → Save complete session: {"filename": "session.json"}

**Tree Structure CRUD:**
• `add_node` → Create new nodes (see 0.2.2 for details)
• `update_node` → Modify existing: {"coordinate": "0.1.5", "updates": {...}}
• `delete_node` → Remove: {"coordinate": "0.1.5"}
• `list_nodes` → Show nodes: {"pattern": "0.1"} (optional filter)
• `get_node` → View details: {"coordinate": "0.1.5"}

**Session Info:**
• `session_stats` → Memory usage, variables, nodes count: {}

**MCP Generator:** Navigate to 0.0.3 for MCP server generation
**OmniTool Access:** Navigate to 0.0.4 for HEAVEN tool ecosystem"""
        
        return docs, True


class AgentTreeShell(TreeShell, AgentTreeReplMixin):
    """
    Agent-level TreeShell with quarantine restrictions.
    Agents can create workflows but cannot approve them.
    """
    
    def __init__(self, graph_config: dict, session_id: str = None, approval_callback=None):
        TreeShell.__init__(self, graph_config)
        self.__init_agent_features__(session_id, approval_callback)
    
    def handle_command(self, command: str) -> dict:
        """Override to use agent command handling."""
        return self.handle_command_agent(command)


class UserTreeShell(TreeShell, UserTreeReplMixin):
    """
    User-level TreeShell with agent management and approval capabilities.
    Humans can launch agents and approve/reject their workflows.
    """
    
    def __init__(self, config: dict = None, parent_approval_callback=None):
        # Handle nested config structure
        if config is None:
            # Use default agent management hub
            graph_config = self._get_user_interface_config()
        elif "graph" in config:
            # Merge app config into graph config
            graph_config = config["graph"].copy()
            if "app" in config:
                graph_config.update(config["app"])
        else:
            # Legacy: assume config is graph config
            graph_config = config
        
        TreeShell.__init__(self, graph_config)
        self.__init_user_features__(parent_approval_callback)


class FullstackTreeShell(UserTreeShell, TreeReplFullstackMixin):
    """
    Complete fullstack TreeShell supporting nested human-agent interactions.
    """
    
    def __init__(self, config: dict = None, parent_approval_callback=None):
        UserTreeShell.__init__(self, config, parent_approval_callback)
        self.__init_fullstack_features__(parent_approval_callback)


# Public API
__all__ = [
    "TreeShell",
    "AgentTreeShell", 
    "UserTreeShell",
    "FullstackTreeShell",
    "TreeShellBase",
    "DisplayBrief",
    "render_response",
    "ApprovalQueue",
    # Mixins for advanced usage
    "MetaOperationsMixin",
    "PathwayManagementMixin",
    "CommandHandlersMixin",
    "RSIAnalysisMixin",
    "ExecutionEngineMixin",
    "AgentTreeReplMixin",
    "UserTreeReplMixin",
    "TreeReplFullstackMixin",
    # MCP Generator
    "generate_mcp_from_config",
    "generate_mcp_from_dict", 
    "TreeShellMCPConfig",
    "MCPGenerator",
]