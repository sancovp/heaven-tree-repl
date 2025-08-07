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
        self.about_app = graph_config.get("about_app", "")
        self.about_domain = graph_config.get("about_domain", "")
        
        # Initialize function registries before building nodes
        self.async_functions = {}
        self.sync_functions = {}
        
        # Build nodes (may need to import functions)
        self.nodes = self._build_coordinate_nodes(graph_config)
        
        # Navigation state
        self.current_position = "0"
        self.stack = ["0"]
        
        # Live session state - persists objects during session
        self.session_vars = {}
        self.execution_history = []
        
        # Load shortcuts
        self._load_shortcuts()
        
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
        
        # LinguisticStructure hierarchy tracking
        self.linguistic_structures = {
            "words": [],      # atomic units (coordinates, shortcuts, operands)
            "sentences": [],  # combinations with operands
            "paragraphs": [], # 2+ sentences
            "pages": [],      # 5 paragraphs
            "chapters": [],   # 2+ pages
            "books": [],      # 2+ chapters
            "volumes": []     # 2+ books
        }
        
        # Automation system: Schedule = when + if + then, Automation = set of schedules  
        self.schedules = {}  # Individual schedules: name -> {when, if, then, created, last_run}
        self.automations = {}  # Collections of schedules: name -> {schedules: [], description}
        self.master_schedule = {}  # All automations
        self.scheduler_active = False
        
        # Chain execution state
        self.chain_results = {}
        self.step_counter = 0
    
    def _load_shortcuts(self) -> None:
        """Load shortcuts from JSON files. Override in subclasses for different layers."""
        shortcuts = {}
        
        # Load base shortcuts (always loaded)
        base_shortcuts = self._load_shortcuts_file("base_shortcuts.json")
        if base_shortcuts:
            shortcuts.update(base_shortcuts)
        
        # Store in session vars
        self.session_vars["_shortcuts"] = shortcuts
    
    def _load_config_file(self, filename: str) -> dict:
        """Load configuration from a JSON file."""
        import os
        import json
        
        # Get the directory where this module is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to heaven-tree-repl directory, then into configs
        configs_dir = os.path.join(os.path.dirname(current_dir), "configs")
        file_path = os.path.join(configs_dir, filename)
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            else:
                print(f"Warning: Config file not found: {file_path}")
                return {}
        except Exception as e:
            print(f"Error loading config from {filename}: {e}")
            return {}
    
    def _load_shortcuts_file(self, filename: str) -> dict:
        """Load shortcuts from a specific JSON file."""
        import os
        import json
        
        # Get the directory where this module is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to heaven-tree-repl directory, then into shortcuts
        shortcuts_dir = os.path.join(os.path.dirname(current_dir), "shortcuts")
        file_path = os.path.join(shortcuts_dir, filename)
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            else:
                print(f"Warning: Shortcuts file not found: {file_path}")
                return {}
        except Exception as e:
            print(f"Error loading shortcuts from {filename}: {e}")
            return {}
    
    def _save_shortcut_to_file(self, alias: str, shortcut_data: dict) -> None:
        """Save shortcut to appropriate JSON file based on TreeShell type. Override in subclasses."""
        # Base TreeShell saves to base_shortcuts.json
        self._save_shortcut_to_specific_file(alias, shortcut_data, "base_shortcuts.json")
    
    def _save_shortcut_to_specific_file(self, alias: str, shortcut_data: dict, filename: str) -> None:
        """Save shortcut to a specific JSON file."""
        import os
        import json
        
        # Get the directory where this module is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to heaven-tree-repl directory, then into shortcuts
        shortcuts_dir = os.path.join(os.path.dirname(current_dir), "shortcuts")
        file_path = os.path.join(shortcuts_dir, filename)
        
        try:
            # Load existing shortcuts
            existing_shortcuts = {}
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    existing_shortcuts = json.load(f)
            
            # Add new shortcut
            existing_shortcuts[alias] = shortcut_data
            
            # Save back to file
            with open(file_path, 'w') as f:
                json.dump(existing_shortcuts, f, indent=2)
                
        except Exception as e:
            print(f"Error saving shortcut to {filename}: {e}")
    
    def register_async_function(self, function_name: str, async_func) -> None:
        """Register an async function for use in tree repl."""
        self.async_functions[function_name] = async_func
    
    def register_sync_function(self, function_name: str, sync_func) -> None:
        """Register a sync function for use in tree repl."""
        self.sync_functions[function_name] = sync_func
    
    def _get_async_function(self, function_name: str):
        """Get async function if registered."""
        return self.async_functions.get(function_name)
    
    def _get_sync_function(self, function_name: str):
        """Get sync function if registered."""
        return self.sync_functions.get(function_name)
    
    def _build_coordinate_nodes(self, node_config: dict) -> dict:
        """Convert node config to coordinate-based addressing."""
        # Check if we already have fully formed nodes (new JSON-based system)
        if "nodes" in node_config and isinstance(node_config["nodes"], dict):
            nodes_dict = node_config["nodes"]
            # Check if this looks like coordinate-based nodes
            has_coordinate_nodes = any(
                key == "0" or "." in key 
                for key in nodes_dict.keys()
            )
            if has_coordinate_nodes:
                return nodes_dict.copy()
        
        # Fallback to old system for backward compatibility
        nodes = {}
        
        # Load base configuration from JSON
        base_config = self._load_config_file("base_default_config.json")
        if base_config and "nodes" in base_config:
            # Start with base nodes
            nodes.update(base_config["nodes"])
            
            # Update root node description with current app_id if different
            if "0" in nodes:
                nodes["0"]["description"] = f"Root menu for {self.app_id}"
        
        # Convert provided domain nodes to coordinate system starting at 0.1
        # Only convert nodes that aren't already coordinate-based
        if "nodes" in node_config and node_config["nodes"]:
            domain_nodes = self._convert_to_coordinates(node_config["nodes"], "0.1")
            nodes.update(domain_nodes)
        
        # Process all callable nodes (including base nodes and domain nodes) to import external functions
        processed_count = 0
        for coordinate, node_data in nodes.items():
            if node_data.get("type") == "Callable":
                try:
                    result_detail, success = self._process_callable_node(node_data, coordinate)
                    if success:
                        processed_count += 1
                        print(f"Debug: Successfully processed callable node {coordinate}: {result_detail}")
                    else:
                        print(f"Warning: Failed to process callable node {coordinate}: {result_detail}")
                except Exception as e:
                    print(f"Error: Exception processing callable node {coordinate}: {e}")
                    import traceback
                    traceback.print_exc()
        print(f"Debug: Processed {processed_count} callable nodes total")
        
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
            "role": self.role,
            "shortcuts": self.session_vars.get("_shortcuts", {})  # Include shortcuts for game state
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
                    # Handle simple variable substitution: "$variable_name"
                    var_name = value[1:]
                    # Special handling for agent config resolution
                    if var_name == "selected_agent_config" and hasattr(self, '_resolve_agent_config'):
                        config_identifier = self.session_vars.get("selected_agent_config")
                        if config_identifier:
                            substituted[key] = self._resolve_agent_config(config_identifier)
                        else:
                            substituted[key] = value  # Keep original if not found
                    elif var_name in self.session_vars:
                        substituted[key] = self.session_vars[var_name]
                    elif var_name in self.chain_results:
                        substituted[key] = self.chain_results[var_name]
                    else:
                        substituted[key] = value  # Keep original if not found
                elif "{$" in value:
                    # Handle string formatting with variables: "Hello {$name}, you are {$role}"
                    substituted[key] = self._format_string_with_variables(value)
                else:
                    substituted[key] = value
            else:
                substituted[key] = value
        return substituted
    
    def _format_string_with_variables(self, text: str) -> str:
        """Format string with session variables using {$variable_name} syntax."""
        import re
        
        # Find all {$variable_name} patterns
        pattern = r'\{\$([^}]+)\}'
        
        def replace_var(match):
            var_name = match.group(1)
            # Special handling for agent config resolution
            if var_name == "selected_agent_config" and hasattr(self, '_resolve_agent_config'):
                config_identifier = self.session_vars.get("selected_agent_config")
                if config_identifier:
                    resolved_config = self._resolve_agent_config(config_identifier)
                    return str(resolved_config)
                else:
                    return match.group(0)  # Keep original if not found
            elif var_name in self.session_vars:
                return str(self.session_vars[var_name])
            elif var_name in self.chain_results:
                return str(self.chain_results[var_name])
            else:
                return match.group(0)  # Keep original if not found
        
        return re.sub(pattern, replace_var, text)
    
    def _process_callable_node(self, node_data: dict, coordinate: str) -> tuple:
        """
        Shared logic for processing callable nodes with imports/function_code.
        Used by both _build_coordinate_nodes and _meta_add_node.
        
        Returns: (result_detail_string, success_bool)
        """
        if node_data.get("type") != "Callable":
            return "static node", True
        
        function_name = node_data.get("function_name")
        if not function_name:
            return "callable node without function_name", False
        
        is_async = node_data.get("is_async", False)
        
        # Approach 1: Import from external module
        if "import_path" in node_data and "import_object" in node_data:
            import_path = node_data["import_path"]
            import_object = node_data["import_object"]
            
            try:
                # Dynamic import: from import_path import import_object
                module = __import__(import_path, fromlist=[import_object])
                imported_func = getattr(module, import_object)
                
                # All imported functions go to registries (not instance attributes)
                if is_async:
                    self.register_async_function(function_name, imported_func)
                else:
                    self.register_sync_function(function_name, imported_func)
                
                return f"imported {import_object} from {import_path} ({'async' if is_async else 'sync'})", True
                
            except ImportError as e:
                return f"Failed to import {import_object} from {import_path}: {str(e)}", False
            except AttributeError as e:
                return f"Object {import_object} not found in {import_path}: {str(e)}", False
            except Exception as e:
                return f"Import failed: {str(e)}", False
        
        # Approach 2: Execute function code dynamically
        elif "function_code" in node_data:
            function_code = node_data["function_code"]
            
            try:
                # Create function from code string with enhanced globals
                exec_globals = {
                    "__builtins__": __builtins__,
                    "self": self,  # Allow access to shell instance
                }
                exec(function_code, exec_globals)
                
                # Register the function based on async flag
                if function_name in exec_globals:
                    if is_async:
                        self.register_async_function(function_name, exec_globals[function_name])
                    else:
                        self.register_sync_function(function_name, exec_globals[function_name])
                    return f"compiled function code ({'async' if is_async else 'sync'})", True
                else:
                    return f"Function {function_name} not found in provided code", False
                    
            except Exception as e:
                return f"Failed to compile function code: {str(e)}", False
        
        # Approach 3: Function name only (assumes function already exists)
        else:
            # Check if function already exists
            if is_async:
                if function_name not in self.async_functions:
                    return f"Async function {function_name} not found in async registry", False
            else:
                # Check sync registry first, then instance attributes
                if function_name not in self.sync_functions and not hasattr(self, function_name):
                    return f"Sync function {function_name} not found in sync registry or as instance method", False
            
            return f"using existing function ({'async' if is_async else 'sync'})", True
    
    def _get_function_docs(self, function_name: str, node: dict = None) -> tuple:
        """Extract signature and docstring from function with graceful fallbacks."""
        import inspect
        
        # Try to get the function from registries
        function = None
        if function_name in self.async_functions:
            function = self.async_functions[function_name]
        elif function_name in self.sync_functions:
            function = self.sync_functions[function_name]
        elif hasattr(self, function_name):
            function = getattr(self, function_name)
        
        # If not found and we have node data, try to import it
        if not function and node:
            if "import_path" in node and "import_object" in node:
                try:
                    import_path = node["import_path"]
                    import_object = node["import_object"]
                    module = __import__(import_path, fromlist=[import_object])
                    function = getattr(module, import_object)
                except Exception:
                    pass  # Will fall through to warning message
        
        if not function:
            return f"⚠️ Function {function_name} not found", f"⚠️ Could not display docstring for {function_name}"
        
        # Extract signature with fallback
        try:
            signature = str(inspect.signature(function))
            signature = f"{function_name}{signature}"
        except Exception:
            signature = f"⚠️ Could not extract signature for {function_name}"
        
        # Extract docstring with fallback
        try:
            docstring = function.__doc__
            if not docstring or not docstring.strip():
                docstring = "⚠️ No docstring available"
            else:
                docstring = docstring.strip()
        except Exception:
            docstring = f"⚠️ Could not display docstring for {function_name}"
        
        return signature, docstring

    def _get_node_menu(self, node_coord: str) -> dict:
        """Get menu display for a node."""
        node = self.nodes.get(node_coord)
        if not node:
            return {"error": f"Node {node_coord} not found"}
            
        menu_options = {}
        
        # Universal options - 0 shows description, 1 executes
        menu_options["1"] = "execute"
        
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
        
        # Get description and signature
        description = node.get("description", "No description available")
        signature = "No signature available"
        
        # For callable nodes, try to extract function documentation
        if node.get("type") == "Callable":
            function_name = node.get("function_name")
            if function_name:
                func_signature, func_docstring = self._get_function_docs(function_name, node)
                signature = func_signature
                # Use docstring as description if available and not a fallback warning
                if func_docstring and not func_docstring.startswith("⚠️"):
                    description = func_docstring
                elif func_docstring:
                    # Show both original description and warning
                    description = f"{description}\n\n{func_docstring}"
        
        # Use DisplayBrief for root node description
        if node_coord == "0":
            from .display_brief import DisplayBrief
            shortcuts = self.session_vars.get("_shortcuts", {})
            if shortcuts:
                display_brief = DisplayBrief(
                    shortcuts=shortcuts, 
                    role=self.role,
                    app_id=self.app_id,
                    domain=self.domain,
                    about_app=self.about_app,
                    about_domain=self.about_domain
                )
                description = display_brief.to_display_string()
            else:
                display_brief = DisplayBrief(
                    role=self.role,
                    app_id=self.app_id,
                    domain=self.domain,
                    about_app=self.about_app,
                    about_domain=self.about_domain
                )
                if display_brief.has_content():
                    description = display_brief.to_display_string()
        
        return {
            "prompt": node.get("prompt", f"Node {node_coord}"),
            "description": description,
            "signature": signature,
            "menu_options": menu_options,
            "universal_commands": universal_commands,
            "node_type": node.get("type"),
            "position": node_coord
        }
    
    async def run(self):
        """
        Run the TreeShell - initialize and return self for command handling.
        
        This method should be called to properly start a TreeShell instance.
        It performs any necessary initialization and returns the shell ready
        for command handling via handle_command().
        
        Returns:
            self: The initialized TreeShell instance
        """
        # Perform any additional initialization if needed
        # (Currently TreeShell initializes in __init__, but this provides
        # a consistent interface for future async initialization needs)
        
        return self
    
    async def main(self):
        """
        Main entry point for TreeShell execution.
        
        This provides the same interface that was previously in default_chat_app.py
        but as a method on the TreeShell instance itself.
        
        Returns:
            self: The initialized TreeShell instance ready for command handling
        """
        return await self.run()