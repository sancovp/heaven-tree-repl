#!/usr/bin/env python3
"""
Base TreeShell module - Core navigation and state management.
Part of HEAVEN (Hierarchical Embodied Autonomously Validating Evolution Network).
"""
import json
import datetime
import copy
import uuid
from typing import Dict, List, Any, Optional, Tuple


class TreeShellBase:
    """
    Core tree navigation shell with persistent object state.
    Provides geometric addressing (0.1.1.1.3) with live variable persistence.
    """
    
    def __init__(self, graph_config: dict):
        # Core graph structure
        self.graph = graph_config
        self.app_id = graph_config.get("app_id", "default")
        self.domain = graph_config.get("domain", "general")
        self.role = graph_config.get("role", "assistant")
        self.nodes = self._build_coordinate_nodes(graph_config.get("nodes", {}))
        
        # Navigation state
        self.current_position = "0"
        self.stack = ["0"]
        
        # Live session state - persists objects during session
        self.session_vars = {}
        self.execution_history = []
        
        # Pathway recording - enhanced system
        self.recording_pathway = False
        self.recording_start_position = None
        self.pathway_steps = []
        self.saved_pathways = {}
        self.saved_templates = {}  # Analyzed templates for execution
        
        # Enhanced Ontology system for RSI analysis
        self.graph_ontology = {
            "domains": {},
            "pathway_index": {},
            "tags": {},
            "next_coordinates": {},  # Track next available coordinate per domain
            # RSI Analysis Components
            "execution_patterns": {},  # Pattern recognition for optimization
            "pathway_performance": {},  # Performance metrics per pathway
            "dependency_graph": {},     # Pathway dependency analysis
            "optimization_suggestions": [],  # AI-generated improvements
            "learning_insights": {},    # Extracted insights from execution
            "crystallization_history": []  # Track RSI iterations
        }
        
        # Chain execution state
        self.chain_results = {}
        self.step_counter = 0
        
        # Async function registry
        self.async_functions = {}
    
    def register_async_function(self, function_name: str, async_func) -> None:
        """Register an async function for use in tree repl."""
        self.async_functions[function_name] = async_func
    
    def _get_async_function(self, function_name: str):
        """Get async function if registered."""
        return self.async_functions.get(function_name)
    
    def _build_coordinate_nodes(self, node_config: dict) -> dict:
        """Convert node config to coordinate-based addressing."""
        nodes = {}
        
        # Root node (0)
        nodes["0"] = {
            "type": "Menu",
            "prompt": "Main Menu",
            "description": f"Root menu for {self.app_id}",
            "signature": "menu() -> navigation_options",
            "options": {
                "1": "0.0",  # settings
                "2": "0.1"   # domain
            }
        }
        
        # Settings node (0.0)
        nodes["0.0"] = {
            "type": "Menu", 
            "prompt": "Settings & Management",
            "description": "System configuration and pathway management",
            "signature": "settings() -> management_options",
            "options": {
                "1": "0.0.1",  # manage_pathways
                "2": "0.0.2",  # meta_operations
                "3": "0.0.3"   # session_info
            }
        }
        
        # Add settings sub-nodes
        nodes["0.0.1"] = {
            "type": "Callable",
            "prompt": "Manage Pathways",
            "description": "View and manage saved pathways",
            "signature": "manage_pathways() -> pathway_list",
            "function_name": "_manage_pathways"
        }
        
        # Meta Operations Menu (0.0.2)
        nodes["0.0.2"] = {
            "type": "Menu",
            "prompt": "Meta Operations",
            "description": "State management and session operations",
            "signature": "meta_operations() -> operation_options",
            "options": {
                "1": "0.0.2.1",  # save_var
                "2": "0.0.2.2",  # get_var
                "3": "0.0.2.3",  # append_to_var
                "4": "0.0.2.4",  # delete_var
                "5": "0.0.2.5",  # list_vars
                "6": "0.0.2.6",  # save_to_file
                "7": "0.0.2.7",  # load_from_file
                "8": "0.0.2.8",  # export_session
                "9": "0.0.2.9",  # session_stats
            }
        }
        
        # State Management Operations
        nodes["0.0.2.1"] = {
            "type": "Callable",
            "prompt": "Save Variable",
            "description": "Store value in session variables",
            "signature": "save_var(name: str, value: any) -> bool",
            "function_name": "_meta_save_var",
            "args_schema": {"name": "str", "value": "any"}
        }
        
        nodes["0.0.2.2"] = {
            "type": "Callable", 
            "prompt": "Get Variable",
            "description": "Retrieve session variable value",
            "signature": "get_var(name: str) -> any",
            "function_name": "_meta_get_var",
            "args_schema": {"name": "str"}
        }
        
        nodes["0.0.2.3"] = {
            "type": "Callable",
            "prompt": "Append to Variable",
            "description": "Append value to existing variable (list/string)",
            "signature": "append_to_var(name: str, value: any) -> bool",
            "function_name": "_meta_append_to_var", 
            "args_schema": {"name": "str", "value": "any"}
        }
        
        nodes["0.0.2.4"] = {
            "type": "Callable",
            "prompt": "Delete Variable",
            "description": "Remove session variable",
            "signature": "delete_var(name: str) -> bool",
            "function_name": "_meta_delete_var",
            "args_schema": {"name": "str"}
        }
        
        nodes["0.0.2.5"] = {
            "type": "Callable",
            "prompt": "List Variables", 
            "description": "Show all session variables with values",
            "signature": "list_vars() -> dict",
            "function_name": "_meta_list_vars"
        }
        
        # Persistence Operations
        nodes["0.0.2.6"] = {
            "type": "Callable",
            "prompt": "Save to File",
            "description": "Write variable value to file",
            "signature": "save_to_file(filename: str, var_name: str) -> bool",
            "function_name": "_meta_save_to_file",
            "args_schema": {"filename": "str", "var_name": "str"}
        }
        
        nodes["0.0.2.7"] = {
            "type": "Callable",
            "prompt": "Load from File", 
            "description": "Load file content into variable",
            "signature": "load_from_file(filename: str, var_name: str) -> bool",
            "function_name": "_meta_load_from_file",
            "args_schema": {"filename": "str", "var_name": "str"}
        }
        
        nodes["0.0.2.8"] = {
            "type": "Callable",
            "prompt": "Export Session",
            "description": "Save complete session state to file",
            "signature": "export_session(filename: str) -> bool", 
            "function_name": "_meta_export_session",
            "args_schema": {"filename": "str"}
        }
        
        # Introspection Operations
        nodes["0.0.2.9"] = {
            "type": "Callable",
            "prompt": "Session Stats",
            "description": "Show session statistics and memory usage",
            "signature": "session_stats() -> dict",
            "function_name": "_meta_session_stats"
        }
        
        # Tree Structure CRUD Operations
        nodes["0.0.2.10"] = {
            "type": "Callable",
            "prompt": "Add Node",
            "description": "Create a new node in the tree structure",
            "signature": "add_node(coordinate: str, node_data: dict) -> bool",
            "function_name": "_meta_add_node",
            "args_schema": {"coordinate": "str", "node_data": "dict"}
        }
        
        nodes["0.0.2.11"] = {
            "type": "Callable",
            "prompt": "Update Node",
            "description": "Modify an existing node in the tree",
            "signature": "update_node(coordinate: str, updates: dict) -> bool",
            "function_name": "_meta_update_node",
            "args_schema": {"coordinate": "str", "updates": "dict"}
        }
        
        nodes["0.0.2.12"] = {
            "type": "Callable",
            "prompt": "Delete Node",
            "description": "Remove a node from the tree structure",
            "signature": "delete_node(coordinate: str) -> bool",
            "function_name": "_meta_delete_node",
            "args_schema": {"coordinate": "str"}
        }
        
        nodes["0.0.2.13"] = {
            "type": "Callable",
            "prompt": "List Nodes",
            "description": "Show all nodes in the tree structure",
            "signature": "list_nodes(pattern: str) -> list",
            "function_name": "_meta_list_nodes",
            "args_schema": {"pattern": "str"}
        }
        
        nodes["0.0.2.14"] = {
            "type": "Callable",
            "prompt": "Get Node",
            "description": "View details of a specific node",
            "signature": "get_node(coordinate: str) -> dict",
            "function_name": "_meta_get_node",
            "args_schema": {"coordinate": "str"}
        }
        
        # Convert provided nodes to coordinate system starting at 0.1
        domain_nodes = self._convert_to_coordinates(node_config, "0.1")
        nodes.update(domain_nodes)
        
        return nodes
    
    def _convert_to_coordinates(self, node_config: dict, prefix: str) -> dict:
        """Convert node configuration to coordinate addressing."""
        coordinate_nodes = {}
        
        # Create mapping from original keys to coordinates
        key_to_coord = {}
        coord_index = 1
        
        # First pass: assign coordinates to all nodes
        for key, node in node_config.items():
            if key == "root":
                coord = prefix  # Root gets the prefix directly (0.1)
            else:
                coord = f"{prefix}.{coord_index}"
                coord_index += 1
            key_to_coord[key] = coord
        
        # Second pass: create nodes with proper coordinate references
        for key, node in node_config.items():
            coord = key_to_coord[key]
            
            coordinate_nodes[coord] = {
                "type": node.get("type", "Menu"),
                "prompt": node.get("prompt", f"Node {coord}"),
                "description": node.get("description", f"Node at {coord}"),
                "signature": node.get("signature", f"execute() -> result"),
                "function_name": node.get("function_name"),
                "args_schema": node.get("args_schema", {}),
                "options": {}
            }
            
            # Convert options to coordinate references
            if "options" in node:
                option_index = 1
                for opt_key, opt_target in node["options"].items():
                    if opt_target in key_to_coord:
                        target_coord = key_to_coord[opt_target]
                        coordinate_nodes[coord]["options"][str(option_index)] = target_coord
                        option_index += 1
        
        return coordinate_nodes
    
    def _get_current_node(self) -> dict:
        """Get the current node definition."""
        return self.nodes.get(self.current_position, {})
    
    def _build_response(self, payload: dict) -> dict:
        """Build standard response with current state."""
        base = {
            "state_id": datetime.datetime.utcnow().isoformat(),
            "position": self.current_position,
            "stack": self.stack.copy(),
            "session_vars_keys": list(self.session_vars.keys()),
            "recording_pathway": self.recording_pathway,
            "app_id": self.app_id,
            "domain": self.domain,
            "role": self.role
        }
        base.update(payload)
        return base
    
    def _substitute_variables(self, args: dict) -> dict:
        """Substitute session variables and chain results in arguments."""
        if not isinstance(args, dict):
            return args
            
        substituted = {}
        for key, value in args.items():
            if isinstance(value, str):
                if value.startswith("$"):
                    var_name = value[1:]
                    if var_name in self.session_vars:
                        substituted[key] = self.session_vars[var_name]
                    elif var_name in self.chain_results:
                        substituted[key] = self.chain_results[var_name]
                    else:
                        substituted[key] = value  # Keep original if not found
                else:
                    substituted[key] = value
            else:
                substituted[key] = value
        return substituted
    
    def _get_node_menu(self, node_coord: str) -> dict:
        """Get menu display for a node."""
        node = self.nodes.get(node_coord)
        if not node:
            return {"error": f"Node {node_coord} not found"}
            
        menu_options = {}
        
        # Universal options
        menu_options["0"] = "introspect (description & signature)"
        menu_options["1"] = "execute (run with current args)"
        
        # Node-specific options
        options = node.get("options", {})
        for i, (key, target) in enumerate(options.items(), start=2):
            target_node = self.nodes.get(target)
            if target_node:
                action_name = target_node.get("prompt", f"Node {target}")
                menu_options[str(i)] = action_name
            else:
                menu_options[str(i)] = f"{key} -> {target}"
        
        # Add universal commands
        universal_commands = [
            "jump <node_id> [args]",
            "chain <sequence>", 
            "build_pathway",
            "save_emergent_pathway <name>",
            "save_emergent_pathway_from_history <name> [step_ids]",
            "follow_established_pathway [name] [args]",
            "show_execution_history",
            "analyze_patterns",
            "crystallize_pattern <name>",
            "rsi_insights",
            "back",
            "menu", 
            "exit"
        ]
        
        return {
            "prompt": node.get("prompt", f"Node {node_coord}"),
            "menu_options": menu_options,
            "universal_commands": universal_commands,
            "node_type": node.get("type"),
            "position": node_coord
        }