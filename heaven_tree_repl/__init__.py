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
    
    def __init__(self, graph_config: dict = None, parent_approval_callback=None):
        # Use agent management config if no config provided
        if graph_config is None:
            graph_config = self._get_user_interface_config()
        
        TreeShell.__init__(self, graph_config)
        self.__init_user_features__(parent_approval_callback)


class FullstackTreeShell(UserTreeShell, TreeReplFullstackMixin):
    """
    Complete fullstack TreeShell supporting nested human-agent interactions.
    """
    
    def __init__(self, graph_config: dict = None, parent_approval_callback=None):
        UserTreeShell.__init__(self, graph_config, parent_approval_callback)
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
]