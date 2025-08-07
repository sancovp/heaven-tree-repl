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
        from heaven_base.baseheavenagent import HeavenAgentConfig
        from heaven_base.unified_chat import ProviderEnum
        
        self.active_agent_sessions = {}
        self.approval_queue = ApprovalQueue()
        self.parent_approval_callback = parent_approval_callback
        self.dynamic_agent_config = HeavenAgentConfig(
            name="DynamicAgent",
            system_prompt="You are a helpful AI assistant.",
            tools=[],
            provider=ProviderEnum.OPENAI,
            model="o4-mini",
            temperature=0.7,
            max_tokens=8000
        )
        
        # Store dynamic_agent_config in session variables so equipment system can access it
        self.session_vars["dynamic_agent_config"] = self.dynamic_agent_config
        
        # Store selected_agent_config as string identifier - initially points to dynamic config
        self.session_vars["selected_agent_config"] = "dynamic"
    
    def _resolve_agent_config(self, config_identifier: str):
        """Resolve config identifier to actual HeavenAgentConfig object."""
        from heaven_base.unified_chat import ProviderEnum
        from .agent_config_management import get_dynamic_config
        
        if config_identifier == "dynamic":
            # UPDATE the existing dynamic config with equipped values
            dynamic_data = get_dynamic_config()
            
            # Update the existing config object with equipped values
            if 'name' in dynamic_data:
                self.dynamic_agent_config.name = dynamic_data['name']
            if 'system_prompt' in dynamic_data:
                self.dynamic_agent_config.system_prompt = dynamic_data['system_prompt']
            if 'tools' in dynamic_data:
                self.dynamic_agent_config.tools = dynamic_data['tools']
            if 'provider' in dynamic_data:
                # Map provider string to enum
                provider_map = {
                    'anthropic': ProviderEnum.ANTHROPIC,
                    'openai': ProviderEnum.OPENAI,
                    'google': ProviderEnum.GOOGLE
                }
                self.dynamic_agent_config.provider = provider_map.get(dynamic_data['provider'], ProviderEnum.OPENAI)
            if 'model' in dynamic_data:
                self.dynamic_agent_config.model = dynamic_data['model']
            if 'temperature' in dynamic_data:
                self.dynamic_agent_config.temperature = dynamic_data['temperature']
            if 'max_tokens' in dynamic_data:
                self.dynamic_agent_config.max_tokens = dynamic_data['max_tokens']
            if 'prompt_suffix_blocks' in dynamic_data:
                self.dynamic_agent_config.prompt_suffix_blocks = dynamic_data['prompt_suffix_blocks']
            
            return self.dynamic_agent_config  # Return the updated existing object
        else:
            # TODO: Load saved config by name
            # For now, fall back to the original dynamic agent config
            return self.dynamic_agent_config
    
    def _get_user_interface_config(self):
        """Load user interface configuration from JSON file."""
        return self._load_config_file("user_default_config.json")
    
    def _reject_workflow_action(self, args: dict) -> dict:
        """Reject a workflow by approval ID."""
        approval_id = args.get("approval_id")
        if not approval_id:
            return {"error": "approval_id required"}, False
        
        rejected = self.approval_queue.reject_workflow(approval_id)
        if not rejected:
            return {"error": f"Approval ID {approval_id} not found"}, False
        
        return {
            "action": "workflow_rejected",
            "approval_id": approval_id,
            "message": f"Workflow rejected"
        }, True
    
    def _view_approved_workflows(self, args: dict = None) -> dict:
        """Show all approved workflows."""
        approved = self.approval_queue.list_approved()
        
        if not approved:
            return {
                "approved_count": 0,
                "message": "No approved workflows"
            }, True
        
        return {
            "approved_count": len(approved),
            "approved_workflows": approved,
            "message": f"{len(approved)} approved workflows"
        }, True
    
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
    
    def _view_pending_approvals(self, args: dict = None) -> tuple:
        """Show all pending workflow approvals."""
        pending = self.approval_queue.list_pending()
        
        if not pending:
            return {
                "pending_count": 0,
                "message": "No workflows awaiting approval"
            }, True
        
        return {
            "pending_count": len(pending),
            "pending_approvals": pending,
            "message": f"{len(pending)} workflows awaiting approval"
        }, True
    
    def _approve_workflow_action(self, args: dict) -> tuple:
        """Approve a workflow by approval ID."""
        approval_id = args.get("approval_id")
        if not approval_id:
            return {"error": "approval_id required"}, False
        
        approved = self.approval_queue.approve_workflow(approval_id)
        if not approved:
            return {"error": f"Approval ID {approval_id} not found"}, False
        
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
        }, True


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