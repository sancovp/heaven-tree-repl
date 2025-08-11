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
        
        # Load zone config from library first to get version for HEAVEN_DATA_DIR
        self.zone_config = self._load_library_config_file("zone_config.json")
        
        # Initialize HEAVEN_DATA_DIR with correct version
        self._initialize_heaven_data_dir()
        
        # Now reload all configs from HEAVEN_DATA_DIR (user configs take precedence)
        self.nav_config = self._load_config_file("nav_config.json")
        self.zone_config = self._load_config_file("zone_config.json")  # Reload to get user version if exists
        
        # Load family and navigation configurations
        self.family_mappings = {}  # family_name -> nav_coordinate mapping
        self._build_family_mappings()
        
        # Load zone mappings for RPG theming
        self.zone_mappings = {}  # zone_name -> families mapping
        self._build_zone_mappings()
        
        # Load legacy nodes for backward compatibility
        legacy_config = self._load_config_file("base_default_config.json")
        self.legacy_nodes = legacy_config.get("nodes", {})
        
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
    
    def _build_family_mappings(self) -> None:
        """Build family name to coordinate mappings from nav config."""
        if self.nav_config and "nav_tree_order" in self.nav_config:
            nav_tree_order = self.nav_config["nav_tree_order"]
            
            # ALWAYS inject "system" at position 0 if not present
            if not nav_tree_order or nav_tree_order[0] != "system":
                nav_tree_order.insert(0, "system")
                # print("Debug: Injected 'system' family at position 0")
            
            # Build coordinate mappings: position in nav_tree_order maps to 0.X coordinate
            for i, family_name in enumerate(nav_tree_order):
                coordinate = f"0.{i}"
                self.family_mappings[family_name] = coordinate
                # print(f"Debug: Mapped family '{family_name}' to coordinate '{coordinate}'")
        elif self.nav_config and "coordinate_mapping" in self.nav_config:
            # Fallback to old coordinate_mapping format
            coordinate_mapping = self.nav_config["coordinate_mapping"]
            for coord, family_name in coordinate_mapping.items():
                self.family_mappings[family_name] = coord
    
    def _build_zone_mappings(self) -> None:
        """Build zone name to families mapping from zone config."""
        if self.zone_config and "zones" in self.zone_config:
            zones = self.zone_config["zones"]
            for zone_name, zone_data in zones.items():
                if "zone_tree" in zone_data:
                    self.zone_mappings[zone_name] = zone_data["zone_tree"]
                    # print(f"Debug: Mapped zone '{zone_name}' to families: {zone_data['zone_tree']}")
    
    def _load_family_configs(self) -> dict:
        """Load all family configurations from the families directory."""
        import os
        families = {}
        
        # First, try to load from user's HEAVEN_DATA_DIR
        heaven_data_dir = os.environ.get('HEAVEN_DATA_DIR')
        if heaven_data_dir:
            version = self._get_safe_version()
            app_data_dir = os.path.join(heaven_data_dir, f"{self.app_id}_{version}")
            user_families_dir = os.path.join(app_data_dir, "configs", "families")
            
            if os.path.exists(user_families_dir):
                try:
                    for filename in os.listdir(user_families_dir):
                        if filename.endswith("_family.json"):
                            family_name = filename.replace("_family.json", "")
                            family_path = os.path.join(user_families_dir, filename)
                            try:
                                with open(family_path, 'r') as f:
                                    family_config = json.load(f)
                                    families[family_name] = family_config
                                    # print(f"Debug: Loaded user family '{family_name}' with {len(family_config.get('nodes', {}))} nodes")
                            except Exception as e:
                                print(f"Error loading user family config {filename}: {e}")
                except Exception as e:
                    print(f"Error reading user families directory: {e}")
        
        # Fall back to library families for any not found in user directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        library_families_dir = os.path.join(os.path.dirname(current_dir), "configs", "families")
        
        if os.path.exists(library_families_dir):
            try:
                for filename in os.listdir(library_families_dir):
                    if filename.endswith("_family.json"):
                        family_name = filename.replace("_family.json", "")
                        # Only load if not already loaded from user directory
                        if family_name not in families:
                            family_path = os.path.join(library_families_dir, filename)
                            try:
                                with open(family_path, 'r') as f:
                                    family_config = json.load(f)
                                    families[family_name] = family_config
                                    # print(f"Debug: Loaded library family '{family_name}' with {len(family_config.get('nodes', {}))} nodes")
                            except Exception as e:
                                print(f"Error loading library family config {filename}: {e}")
            except Exception as e:
                print(f"Error reading library families directory: {e}")
        
        return families
    
    def _convert_family_to_coordinates(self, family_config: dict, family_name: str, all_families: dict = None) -> dict:
        """Convert family nodes to coordinate-based addressing."""
        nodes = {}
        family_nodes = family_config.get("nodes", {})
        
        # Get the nav coordinate for this family, with automatic rollup for sub-families
        nav_coord = self.family_mappings.get(family_name)
        has_nav_coord = bool(nav_coord)
        if not nav_coord:
            # Check if this is a sub-family that should roll up (e.g., system_meta -> system)
            for base_family, base_coord in self.family_mappings.items():
                if family_name.startswith(f"{base_family}_"):
                    nav_coord = base_coord
                    has_nav_coord = True
                    # print(f"Debug: Rolling up '{family_name}' into '{base_family}' -> '{base_coord}'")
                    break
            
            if not nav_coord:
                # Family exists in semantic space only, not nav coordinate space
                # Use family name as semantic coordinate base
                nav_coord = family_name
                # print(f"Debug: Family '{family_name}' using semantic coordinates")
        else:
            # print(f"Debug: Family '{family_name}' using nav coordinate '{nav_coord}' + semantic coordinates")
            pass
        
        # No copying needed - just load each family into its own semantic space
        # The semantic resolver will handle family references like "system_pathways"

        for node_id, node_data in family_nodes.items():
            # Convert family addressing to coordinate addressing
            if node_id == family_name:
                # Root family node maps to nav coordinate
                coordinate = nav_coord
            else:
                # Convert family.node.subnode to nav_coord.node.subnode
                if node_id.startswith(f"{family_name}."):
                    relative_path = node_id[len(family_name) + 1:]  # Remove "family_name."
                    coordinate = f"{nav_coord}.{relative_path}"
                else:
                    # Fallback for any other format
                    coordinate = f"{nav_coord}.{node_id}"
            
            # Start with ALL original node data to preserve everything
            coord_node = node_data.copy()
            
            # Override prompt if title exists, otherwise ensure prompt exists
            if "title" in node_data:
                coord_node["prompt"] = node_data["title"]
            elif "prompt" not in coord_node:
                coord_node["prompt"] = f"Node {coordinate}"
            
            # Ensure options exist for auto-generation
            if "options" not in coord_node:
                coord_node["options"] = {}
            
            # Handle nested callable structure if it exists (legacy support)
            if "callable" in node_data:
                callable_info = node_data["callable"]
                coord_node.update({
                    "function_name": callable_info.get("function_name"),
                    "import_path": callable_info.get("import_path"),
                    "import_object": callable_info.get("import_object"),
                    "is_async": callable_info.get("is_async", False),
                    "args_schema": callable_info.get("args_schema", {})
                })
                # Remove the nested callable structure since we've flattened it
                del coord_node["callable"]
            
            nodes[coordinate] = coord_node
            
            # ALSO create legacy coordinate mapping if specified
            if "legacy_coordinate" in node_data:
                legacy_coord = node_data["legacy_coordinate"]
                nodes[legacy_coord] = coord_node.copy()
            
            # For nav families, ALSO create semantic coordinate versions
            if has_nav_coord and node_id == family_name:
                # Create semantic version: family_name -> family_name (not nav_coord)
                semantic_coordinate = family_name
                semantic_node = coord_node.copy()  # Copy the node
                nodes[semantic_coordinate] = semantic_node
                # print(f"Debug: Created semantic duplicate '{semantic_coordinate}' for nav family '{family_name}'")
            elif has_nav_coord:
                # Create semantic versions of sub-nodes too
                if node_id.startswith(f"{family_name}."):
                    relative_path = node_id[len(family_name) + 1:]  # Remove "family_name."
                    semantic_coordinate = f"{family_name}.{relative_path}"
                else:
                    semantic_coordinate = f"{family_name}.{node_id}"
                semantic_node = coord_node.copy()  # Copy the node
                nodes[semantic_coordinate] = semantic_node
        
        return nodes

    def _load_shortcuts(self) -> None:
        """Load shortcuts from JSON files. Override in subclasses for different layers."""
        shortcuts = {}
        
        # Load base shortcuts (always loaded)
        base_shortcuts = self._load_shortcuts_file("base_shortcuts.json")
        if base_shortcuts:
            shortcuts.update(base_shortcuts)
        
        # Store in session vars
        self.session_vars["_shortcuts"] = shortcuts
    
    def _load_library_config_file(self, filename: str) -> dict:
        """Load configuration from library only (not HEAVEN_DATA_DIR)."""
        import os
        import json
        
        # Load from library's default config only
        current_dir = os.path.dirname(os.path.abspath(__file__))
        configs_dir = os.path.join(os.path.dirname(current_dir), "configs")
        file_path = os.path.join(configs_dir, filename)
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            print(f"Error loading library config from {filename}: {e}")
            return {}
    
    def _load_config_file(self, filename: str) -> dict:
        """Load configuration from a JSON file, checking HEAVEN_DATA_DIR first."""
        import os
        import json
        
        # First, try to load from user's HEAVEN_DATA_DIR
        heaven_data_dir = os.environ.get('HEAVEN_DATA_DIR')
        if heaven_data_dir:
            # Get version from zone config for directory name
            version = self._get_safe_version()
            app_data_dir = os.path.join(heaven_data_dir, f"{self.app_id}_{version}")
            user_config_path = os.path.join(app_data_dir, "configs", filename)
            
            if os.path.exists(user_config_path):
                try:
                    with open(user_config_path, 'r') as f:
                        return json.load(f)
                except Exception as e:
                    print(f"Error loading user config from {user_config_path}: {e}")
                    # Fall through to library default
        
        # Fall back to library's default config
        current_dir = os.path.dirname(os.path.abspath(__file__))
        configs_dir = os.path.join(os.path.dirname(current_dir), "configs")
        file_path = os.path.join(configs_dir, filename)
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            else:
                # print(f"Warning: Config file not found: {file_path}")
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
                # print(f"Warning: Shortcuts file not found: {file_path}")
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
        """Convert node config to coordinate-based addressing with family support."""
        # Check if we already have fully formed nodes (legacy system)
        if "nodes" in node_config and isinstance(node_config["nodes"], dict):
            nodes_dict = node_config["nodes"]
            # Check if this looks like coordinate-based nodes
            has_coordinate_nodes = any(
                key == "0" or "." in key 
                for key in nodes_dict.keys()
            )
            if has_coordinate_nodes:
                # Legacy system detected - return nodes as-is
                # The dependency injection in _get_current_node and _get_node_menu
                # will handle missing nodes by checking self.legacy_nodes
                return nodes_dict
        
        # NEW: Family-based system - load from family configs
        # print("Debug: Using new family-based node system")
        nodes = {}
        
        # Load base configuration for metadata and system family reference
        base_config = self._load_config_file("base_default_config_v2.json")
        system_family_name = "system"  # default
        if base_config and "system_family" in base_config:
            system_family_name = base_config["system_family"]
            # print(f"Debug: Base config specifies system family: {system_family_name}")
        
        # Create root node only - families will populate the rest
        nodes["0"] = {
            "type": "Menu",
            "prompt": "Main Menu", 
            "description": f"Root menu for {self.app_id}",
            "signature": "menu() -> navigation_options",
            "options": {}  # Will be auto-generated from families
        }
        # print("Debug: Created root node, families will populate the rest")
        
        # Load all family configurations and convert to coordinates
        families = self._load_family_configs()
        total_family_nodes = 0
        
        # Give ALL families their own semantic coordinate space
        for family_name, family_config in families.items():
            # Each family gets loaded into its own semantic space
            family_nodes = self._convert_family_to_coordinates(family_config, family_name, families)
            nodes.update(family_nodes)
            total_family_nodes += len(family_nodes)
            # print(f"Debug: Added {len(family_nodes)} nodes from '{family_name}' family")
        
        # print(f"Debug: Total family nodes loaded: {total_family_nodes}")
        
        # Add zone-based nodes for RPG theming
        if self.zone_mappings:
            # print("Debug: Creating zone-based nodes for RPG theming")
            for zone_name, zone_families in self.zone_mappings.items():
                # Create zone root node
                zone_node = {
                    "type": "Menu",
                    "prompt": f"Zone: {zone_name}",
                    "description": f"RPG Zone containing families: {', '.join(zone_families)}",
                    "signature": "zone_menu() -> zone_options",
                    "options": {}
                }
                nodes[zone_name] = zone_node
                
                # Create zone-scoped family references
                for family_ref in zone_families:
                    # For each zone family reference, create a zone.reference node
                    zone_ref_coord = f"{zone_name}.{family_ref}"
                    
                    # The zone node just holds the reference - resolution happens at jump time
                    zone_ref_node = {
                        "type": "Menu",
                        "prompt": f"{family_ref} (in {zone_name})",
                        "description": f"Zone-scoped access to {family_ref}",
                        "signature": "zone_ref() -> zone_options",
                        "options": {},
                        "zone_reference": family_ref  # Store the reference for later resolution
                    }
                    nodes[zone_ref_coord] = zone_ref_node
                    # print(f"Debug: Created zone node '{zone_ref_coord}' with reference '{family_ref}'")
        
        # Generate options from tree structure (auto-generate menu options)
        self._auto_generate_options(nodes)
        
        # Fallback: if no families loaded, try legacy domain conversion
        if not families and "nodes" in node_config and node_config["nodes"]:
            # print("Debug: No families found, falling back to legacy domain conversion")
            domain_nodes = self._convert_to_coordinates(node_config["nodes"], "0.1")
            nodes.update(domain_nodes)
        
        return self._process_and_return_nodes(nodes)
    
    def _auto_generate_options(self, nodes: dict) -> None:
        """Auto-generate menu options from tree structure."""
        # Build a hierarchy map
        hierarchy = {}
        for coord in nodes.keys():
            parts = coord.split('.')
            for i in range(len(parts) - 1):
                parent = '.'.join(parts[:i + 1])
                child = '.'.join(parts[:i + 2])
                if parent not in hierarchy:
                    hierarchy[parent] = []
                if child not in hierarchy[parent] and child in nodes:
                    hierarchy[parent].append(child)
        
        # Add options to menu nodes based on hierarchy
        for coord, node in nodes.items():
            if node.get("type") == "Menu" and coord in hierarchy:
                children = hierarchy[coord]
                # Sort children by coordinate for consistent ordering
                def sort_key(coord):
                    parts = coord.split('.')
                    result = []
                    for p in parts:
                        if p.isdigit():
                            result.append((0, int(p)))  # Numbers first, then by value
                        else:
                            result.append((1, p))  # Strings second, then alphabetically
                    return result
                children.sort(key=sort_key)
                
                options = {}
                for i, child_coord in enumerate(children, start=1):
                    options[str(i)] = child_coord
                
                node["options"] = options
                # print(f"Debug: Auto-generated {len(options)} options for menu node {coord}")
    
    def _process_and_return_nodes(self, nodes: dict) -> dict:
        """Process callable nodes and return the final node dictionary."""
        # Process all callable nodes to import external functions
        processed_count = 0
        for coordinate, node_data in nodes.items():
            if node_data.get("type") == "Callable":
                try:
                    result_detail, success = self._process_callable_node(node_data, coordinate)
                    if success:
                        processed_count += 1
                        # print(f"Debug: Successfully processed callable node {coordinate}: {result_detail}")
                    else:
                        # print(f"Warning: Failed to process callable node {coordinate}: {result_detail}")
                        pass
                except Exception as e:
                    # print(f"Error: Exception processing callable node {coordinate}: {e}")
                    import traceback
                    traceback.print_exc()
        # print(f"Debug: Processed {processed_count} callable nodes total")
        
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
        # Check family nodes first, then legacy nodes as fallback
        node = self.nodes.get(self.current_position)
        if node is None and hasattr(self, 'legacy_nodes'):
            node = self.legacy_nodes.get(self.current_position, {})
        return node or {}
    
    def _get_domain_chain(self) -> str:
        """Build domain chain by walking up the position hierarchy."""
        domains = [self.app_id]  # Start with app_id
        
        # Split current position into parts (e.g., "0.3.1.2" -> ["0", "3", "1", "2"])
        if self.current_position:
            parts = self.current_position.split('.')
            
            # Walk up the hierarchy, checking each level for domain
            for i in range(len(parts)):
                # Build position string for current level (e.g., "0", "0.3", "0.3.1", etc.)
                level_position = '.'.join(parts[:i+1])
                node = self.nodes.get(level_position, {})
                
                # If this node has a domain, add it to the chain
                if 'domain' in node:
                    domains.append(node['domain'])
        
        # Join with dots, avoiding duplicates
        return '.'.join(dict.fromkeys(domains))  # dict.fromkeys preserves order and removes dupes
    
    def _build_response(self, payload: dict) -> dict:
        """Build standard response with current state."""
        base = {
            "state_id": datetime.datetime.utcnow().isoformat(),
            "position": self.current_position,
            "stack": self.stack.copy(),
            "session_vars_keys": list(self.session_vars.keys()),
            "recording_pathway": self.recording_pathway,
            "app_id": self.app_id,
            "domain": self._get_domain_chain(),
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
    
    def _get_safe_version(self) -> str:
        """Get version string safe for directory names (convert dots to underscores)."""
        # Try to get version from zone_config first, fallback to default
        if hasattr(self, 'zone_config') and self.zone_config and "game_config" in self.zone_config:
            version = self.zone_config["game_config"].get("version", "1.0")
        else:
            version = "1.0"  # Default version
        
        # Convert dots to underscores for filesystem safety
        safe_version = f"v{version.replace('.', '_')}"
        return safe_version
    
    def _initialize_heaven_data_dir(self) -> bool:
        """Initialize user's HEAVEN_DATA_DIR structure if needed."""
        import os
        import shutil
        import json
        
        heaven_data_dir = os.environ.get('HEAVEN_DATA_DIR')
        if not heaven_data_dir:
            return False
        
        version = self._get_safe_version()
        app_data_dir = os.path.join(heaven_data_dir, f"{self.app_id}_{version}")
        
        # Check if directory already exists
        if os.path.exists(app_data_dir):
            return True  # Already initialized
        
        try:
            # Create directory structure
            os.makedirs(os.path.join(app_data_dir, "configs"), exist_ok=True)
            os.makedirs(os.path.join(app_data_dir, "configs", "families"), exist_ok=True)
            os.makedirs(os.path.join(app_data_dir, "shortcuts"), exist_ok=True)
            os.makedirs(os.path.join(app_data_dir, "data"), exist_ok=True)
            
            # Copy library's default configs to user directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            library_configs_dir = os.path.join(os.path.dirname(current_dir), "configs")
            
            # Copy main config files
            config_files = ["zone_config.json", "nav_config.json", "base_default_config_v2.json"]
            for config_file in config_files:
                src = os.path.join(library_configs_dir, config_file)
                dst = os.path.join(app_data_dir, "configs", config_file)
                if os.path.exists(src):
                    shutil.copy2(src, dst)
            
            # Copy families directory
            library_families_dir = os.path.join(library_configs_dir, "families")
            user_families_dir = os.path.join(app_data_dir, "configs", "families")
            if os.path.exists(library_families_dir):
                for family_file in os.listdir(library_families_dir):
                    if family_file.endswith("_family.json"):
                        src = os.path.join(library_families_dir, family_file)
                        dst = os.path.join(user_families_dir, family_file)
                        shutil.copy2(src, dst)
            
            # Copy shortcuts
            library_shortcuts_dir = os.path.join(os.path.dirname(current_dir), "shortcuts")
            user_shortcuts_dir = os.path.join(app_data_dir, "shortcuts")
            if os.path.exists(library_shortcuts_dir):
                for shortcut_file in os.listdir(library_shortcuts_dir):
                    if shortcut_file.endswith(".json"):
                        src = os.path.join(library_shortcuts_dir, shortcut_file)
                        dst = os.path.join(user_shortcuts_dir, shortcut_file)
                        shutil.copy2(src, dst)
            
            print(f"Initialized HEAVEN_DATA_DIR for {self.app_id}_{version} at {app_data_dir}")
            return True
            
        except Exception as e:
            print(f"Error initializing HEAVEN_DATA_DIR: {e}")
            return False
    
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
            sig = inspect.signature(function)
            signature_str = str(sig)
            
            # Check if we have args_schema with pre-filled values (starting with $)
            if node and "args_schema" in node:
                args_schema = node["args_schema"]
                prefilled_params = {k: v for k, v in args_schema.items() if isinstance(v, str) and v.startswith('$')}
                
                if prefilled_params:
                    # Parse and modify the signature to show SYSTEM_WILL_PREFILL
                    import re
                    
                    for param_name in prefilled_params:
                        # Replace parameter with SYSTEM_WILL_PREFILL marker
                        pattern = rf'\b{param_name}(?:\s*:\s*[^,)]+)?(?:\s*=\s*[^,)]+)?'
                        replacement = f'{param_name}=SYSTEM_WILL_PREFILL'
                        signature_str = re.sub(pattern, replacement, signature_str)
            
            signature = f"{function_name}{signature_str}"
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
        # Check family nodes first, then legacy nodes as fallback
        node = self.nodes.get(node_coord)
        if not node and hasattr(self, 'legacy_nodes'):
            node = self.legacy_nodes.get(node_coord)
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
        
        # Get description and signature with HEAVEN resolution
        raw_description = node.get("description", "No description available")
        # Import here to avoid circular imports
        from .renderer import resolve_description
        description = resolve_description(raw_description)
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
                    about_domain=self.about_domain,
                    zone_config=self.zone_config
                )
                description = display_brief.to_display_string()
            else:
                display_brief = DisplayBrief(
                    role=self.role,
                    app_id=self.app_id,
                    domain=self.domain,
                    about_app=self.about_app,
                    about_domain=self.about_domain,
                    zone_config=self.zone_config
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