"""
HEAVEN Tree REPL - Hierarchical Embodied Autonomously Validating Evolution Network Tree REPL

A modular tree navigation system with persistent state, pathway recording, 
and agent management capabilities.
"""

import sys
import traceback

# 🚨 GLOBAL ERROR HANDLER - CATCH EVERYTHING AND SHOW TRACEBACKS 🚨
def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Global exception handler that shows full tracebacks for EVERYTHING."""
    print(f"\n🚨 GLOBAL ERROR HANDLER TRIGGERED 🚨")
    print(f"Exception Type: {exc_type.__name__}")
    print(f"Exception Message: {exc_value}")
    print("\nFULL TRACEBACK:")
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    print("🚨 END GLOBAL ERROR 🚨\n")

# Install the global handler to catch ALL exceptions (for development debugging)
# Can be disabled by setting TREESHELL_DEBUG=0
import os
if os.getenv("TREESHELL_DEBUG", "1") == "1":  # Default ON for development
    sys.excepthook = global_exception_handler

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

# Import Shell classes from shells module
from .shells import TreeShell, AgentTreeShell, UserTreeShell, FullstackTreeShell

# Import agent config management functions
from .agent_config_management import (
    equip_system_prompt, unequip_system_prompt, list_system_prompts,
    equip_tool, unequip_tool, list_tools,
    equip_provider, unequip_provider, list_providers,
    equip_model, unequip_model, list_models,
    equip_temperature, unequip_temperature, list_temperature,
    equip_max_tokens, unequip_max_tokens, list_max_tokens,
    equip_name, unequip_name, list_names,
    equip_prompt_block, unequip_prompt_block, list_prompt_blocks,
    save_config_as, copy_existing, list_saved_configs, preview_dynamic_config,
    get_dynamic_config, reset_dynamic_config
)

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
    # Agent Config Management Functions
    "equip_system_prompt", "unequip_system_prompt", "list_system_prompts",
    "equip_tool", "unequip_tool", "list_tools",
    "equip_provider", "unequip_provider", "list_providers",
    "equip_model", "unequip_model", "list_models",
    "equip_temperature", "unequip_temperature", "list_temperature",
    "equip_max_tokens", "unequip_max_tokens", "list_max_tokens",
    "equip_name", "unequip_name", "list_names",
    "equip_prompt_block", "unequip_prompt_block", "list_prompt_blocks",
    "save_config_as", "copy_existing", "list_saved_configs", "preview_dynamic_config",
    "get_dynamic_config", "reset_dynamic_config",
]