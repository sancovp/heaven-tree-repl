#!/usr/bin/env python3
"""
Agent Management module - Agent and user tree repl classes.
"""
import json
import datetime
import uuid
from typing import Dict, List, Any, Optional
from .approval_system import ApprovalQueue


class AgentTreeReplMixin:
    """
    Agent interface mixin - TreeShell with approval callback but no approval commands.
    Agents can create workflows but cannot approve them.
    """
    
    def __init_agent_features__(self, session_id: str = None, approval_callback=None):
        """Initialize agent-specific features."""
        self.session_id = session_id or uuid.uuid4().hex[:8]
        self.approval_callback = approval_callback
        self.quarantined_coordinates = set()
        
    def _handle_save_pathway_agent(self, name: str) -> dict:
        """Save pathway but mark as quarantined until approved."""
        if not self.recording_pathway:
            return {"error": "No pathway recording in progress"}
            
        if not name:
            return {"error": "Pathway name required"}
        
        # Create template from recorded steps
        template = self._analyze_pathway_template(self.pathway_steps)
        
        # Determine domain from starting position
        domain = self._get_domain_root(self.recording_start_position)
        
        # Get next coordinate in domain
        coordinate = self._get_next_coordinate_in_domain(domain)
        
        # Save pathway data
        self.saved_pathways[name] = {
            "steps": self.pathway_steps.copy(),
            "created": datetime.datetime.utcnow().isoformat(),
            "start_position": self.recording_start_position,
            "end_position": self.current_position,
            "domain": domain,
            "coordinate": coordinate,
            "status": "QUARANTINED"
        }
        
        self.saved_templates[name] = template
        
        # Mark coordinate as quarantined
        self.quarantined_coordinates.add(coordinate)
        
        # Send approval request to parent (human or parent agent)
        if self.approval_callback:
            workflow_data = {
                "pathway_name": name,
                "coordinate": coordinate,
                "session_id": self.session_id,
                "description": f"{template['type']} pathway with {len(self.pathway_steps)} steps",
                "steps": self.pathway_steps.copy(),
                "template": template
            }
            approval_id = self.approval_callback(workflow_data)
        
        self.recording_pathway = False
        self.recording_start_position = None
        self.pathway_steps = []
        
        return self._build_response({
            "action": "save_pathway_quarantined",
            "pathway_name": name,
            "coordinate": coordinate,
            "status": "QUARANTINED - awaiting approval",
            "session_id": self.session_id,
            "message": f"Pathway '{name}' created at {coordinate} but blocked until approved"
        })
    
    def _handle_jump_agent(self, args_str: str) -> dict:
        """Handle jump with quarantine checking."""
        if not args_str:
            return {"error": "Jump target required"}
        
        parts = args_str.split(None, 1)
        target_coord = parts[0]
        args_json = parts[1] if len(parts) > 1 else "{}"
        
        # Block quarantined coordinates
        if target_coord in self.quarantined_coordinates:
            return {
                "error": "BLOCKED: Pathway quarantined awaiting approval",
                "coordinate": target_coord,
                "session_id": self.session_id,
                "action_required": "wait_for_approval"
            }
        
        # Execute normal jump
        try:
            args = json.loads(args_json)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON arguments"}
        
        return self._handle_jump(args_str)
    
    def handle_command_agent(self, command: str) -> dict:
        """Override to block approval commands."""
        command = command.strip()
        if not command:
            return self._get_node_menu(self.current_position)
        
        # Block any approval-related commands
        if command.startswith("approve_") or command.startswith("reject_"):
            return {
                "error": "Approval commands not available to agents", 
                "session_id": self.session_id,
                "available_commands": self._get_agent_commands()
            }
        
        return self.handle_command(command)
    
    def _get_agent_commands(self):
        """Return commands available to agents (no approval commands)."""
        return [
            "jump <node_id> [args]",
            "chain <sequence>", 
            "build_pathway",
            "save_emergent_pathway <name>",
            "follow_established_pathway [name] [args]",
            "show_execution_history",
            "analyze_patterns",
            "back", "menu", "exit"
        ]
    
    def receive_approval(self, coordinate: str):
        """Receive approval for a quarantined coordinate."""
        if coordinate in self.quarantined_coordinates:
            self.quarantined_coordinates.remove(coordinate)
            # Update pathway status
            for pathway in self.saved_pathways.values():
                if pathway.get("coordinate") == coordinate:
                    pathway["status"] = "GOLDEN"
            return True
        return False


class UserTreeReplMixin:
    """
    Human interface mixin - TreeShell with agent management and approval capabilities.
    Humans can launch agents and approve/reject their workflows.
    """
    
    def __init_user_features__(self, parent_approval_callback=None):
        """Initialize user-specific features."""
        self.active_agent_sessions = {}
        self.approval_queue = ApprovalQueue()
        self.parent_approval_callback = parent_approval_callback
    
    def _get_user_interface_config(self):
        """Configuration for the human user interface."""
        return {
            "app_id": "agent_management_hub",
            "initial_node": "0",
            "nodes": {
                "0": {
                    "type": "Menu",
                    "prompt": "🎮 Agent Management Hub", 
                    "description": "Human interface for managing AI agents and workflows",
                    "signature": "hub() -> management_options",
                    "options": {
                        "1": "0.1",  # agent_management
                        "2": "0.2",  # workflow_approvals
                        "3": "0.3",  # session_management
                        "4": "0.4"   # system_stats
                    }
                },
                "0.1": {
                    "type": "Menu",
                    "prompt": "🤖 Agent Management",
                    "description": "Launch and manage AI agents",
                    "signature": "agent_management() -> agent_options",
                    "options": {
                        "1": "0.1.1",  # launch_math_agent
                        "2": "0.1.2",  # launch_text_agent  
                        "3": "0.1.3",  # launch_custom_agent
                        "4": "0.1.4"   # list_active_agents
                    }
                },
                "0.2": {
                    "type": "Menu", 
                    "prompt": "✅ Workflow Approvals",
                    "description": "Review and approve agent-generated workflows",
                    "signature": "approvals() -> approval_options",
                    "options": {
                        "1": "0.2.1",  # view_pending_approvals
                        "2": "0.2.2",  # approve_workflow_action
                        "3": "0.2.3",  # reject_workflow_action
                        "4": "0.2.4"   # view_approved_workflows
                    }
                },
                "0.1.1": {
                    "type": "Callable",
                    "prompt": "Launch Math Agent",
                    "description": "Start a new mathematical operations agent",
                    "signature": "launch_math_agent() -> agent_session",
                    "function_name": "_launch_math_agent"
                },
                "0.2.1": {
                    "type": "Callable",
                    "prompt": "View Pending Approvals",
                    "description": "Show all workflows awaiting human approval",
                    "signature": "view_pending() -> approval_list",
                    "function_name": "_view_pending_approvals"
                },
                "0.2.2": {
                    "type": "Callable",
                    "prompt": "Approve Workflow",
                    "description": "Approve a quarantined agent workflow",
                    "signature": "approve_workflow(approval_id: str) -> approval_result",
                    "function_name": "_approve_workflow_action",
                    "args_schema": {
                        "approval_id": "str"
                    }
                }
            }
        }
    
    def _launch_math_agent(self, args: dict = None) -> dict:
        """Launch a mathematical operations agent."""
        # Load math agent configuration
        math_config = self._get_math_agent_config()
        
        # Create agent session - would need to be implemented by the main class
        # This is a placeholder for the interface
        session_id = uuid.uuid4().hex[:8]
        
        return {
            "agent_type": "mathematical_operations",
            "session_id": session_id,
            "status": "ACTIVE",
            "message": f"Math agent {session_id} launched successfully"
        }
    
    def _get_math_agent_config(self):
        """Get configuration for math agents."""
        # This would load from the math_app_config.json
        try:
            with open('/home/GOD/tree_repl/math_app_config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback basic config
            return {
                "app_id": "math_agent",
                "nodes": {
                    "root": {
                        "type": "Menu",
                        "prompt": "Math Operations",
                        "options": {"basic": "basic_ops"}
                    }
                }
            }
    
    def _receive_agent_approval_request(self, workflow_data):
        """Receive approval request from agent."""
        approval_id = self.approval_queue.add_quarantine_request(workflow_data)
        
        # Show notification to human
        print(f"\n🔔 APPROVAL REQUEST")
        print(f"Agent {workflow_data['session_id']} created workflow: {workflow_data['pathway_name']}")
        print(f"Approval ID: {approval_id}")
        print(f"Use: approve_workflow_action {{'approval_id': '{approval_id}'}}")
        print("🔔 Review pending approvals for details\n")
        
        return approval_id
    
    def _view_pending_approvals(self, args: dict = None) -> dict:
        """Show all pending workflow approvals."""
        pending = self.approval_queue.list_pending()
        
        if not pending:
            return {
                "pending_count": 0,
                "message": "No workflows awaiting approval"
            }
        
        return {
            "pending_count": len(pending),
            "pending_approvals": pending,
            "message": f"{len(pending)} workflows awaiting approval"
        }
    
    def _approve_workflow_action(self, args: dict) -> dict:
        """Approve a workflow by approval ID."""
        approval_id = args.get("approval_id")
        if not approval_id:
            return {"error": "approval_id required"}
        
        approved = self.approval_queue.approve_workflow(approval_id)
        if not approved:
            return {"error": f"Approval ID {approval_id} not found"}
        
        # Notify the agent session
        session_id = approved["session_id"]
        if session_id in self.active_agent_sessions:
            agent = self.active_agent_sessions[session_id]
            agent.receive_approval(approved["coordinate"])
        
        return {
            "action": "workflow_approved",
            "pathway_name": approved["pathway_name"],
            "coordinate": approved["coordinate"],
            "session_id": session_id,
            "message": f"Workflow '{approved['pathway_name']}' approved for agent {session_id}"
        }


class TreeReplFullstackMixin:
    """
    Complete fullstack tree repl system supporting nested human-agent interactions.
    Manages the relationship between UserTreeRepl and AgentTreeRepl instances.
    """
    
    def __init_fullstack_features__(self, parent_approval_callback=None):
        """Initialize fullstack features."""
        self.parent_callback = parent_approval_callback
        
    def escalate_approval(self, workflow_data):
        """Escalate approval request to parent level."""
        if self.parent_callback:
            return self.parent_callback(workflow_data)
        else:
            # Top level - handle locally
            return self._receive_agent_approval_request(workflow_data)
    
    def create_nested_fullstack(self):
        """Create a nested fullstack system with this as parent."""
        # This would need to be implemented by the main class
        pass