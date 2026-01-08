#!/usr/bin/env python3
"""
Base TreeShell module - Core navigation and state management.
Part of HEAVEN (Hierarchical Embodied Autonomously Validating Evolution Network).
"""
import json
import datetime
import copy
import uuid
import os
from typing import Dict, List, Any, Optional, Tuple

from . import logger


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
        
        # Get zone config from graph_config if provided by SystemConfigLoader, otherwise load directly
        if 'zones' in graph_config:
            # Use zone config from SystemConfigLoader (preferred)
            self.zone_config = {'zones': graph_config['zones']}
        else:
            # Fallback to direct loading for backward compatibility
            self.zone_config = self._load_library_config_file("zone_config.json")
        
        # Initialize HEAVEN_DATA_DIR with correct version
        self._initialize_heaven_data_dir()
        
        # Get nav config from graph_config if provided, otherwise load directly
        if 'nav_config' in graph_config:
            self.nav_config = graph_config['nav_config']
        else:
            # Fallback to direct loading for backward compatibility
            self.nav_config = self._load_config_file("nav_config.json")
        
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
        
        # Build clean numeric-only map for nav display
        self.numeric_nodes = self._build_numeric_map()
        
        # Build combo address mapping for mixed coordinate resolution
        self.combo_nodes = self._resolve_combo_node_addresses()
        
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
        
        # Load session state after all initialization is complete
        self._load_session_state()
        
        # Load shortcuts AFTER session state so they don't get overridden
        self._load_shortcuts()
    
    def _build_family_mappings(self) -> None:
        """Build family name to coordinate mappings from nav config."""
        logger.debug(f"_build_family_mappings called, nav_config: {self.nav_config}")
        if self.nav_config and "nav_tree_order" in self.nav_config:
            nav_tree_order = self.nav_config["nav_tree_order"]
            
            # ALWAYS inject "system" at position 0 if not present
            if not nav_tree_order or nav_tree_order[0] != "system":
                nav_tree_order.insert(0, "system")
                # print("Debug: Injected 'system' family at position 0")
            
            # Build coordinate mappings: position in nav_tree_order maps to 0.X coordinate (starting from 1)
            for i, family_name in enumerate(nav_tree_order):
                coordinate = f"0.{i + 1}"  # Start from 1 to avoid 0.0
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
        
        # Check if families were pre-loaded by SystemConfigLoader (with dev customizations)
        if hasattr(self, 'graph') and '_loaded_families' in self.graph:
            # Use pre-loaded families with dev customizations applied
            families = self.graph['_loaded_families']
            return families
        
        # Fallback to direct library loading only (no HEAVEN_DATA_DIR family loading)
        families = {}
        
        # Load from library families directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        library_families_dir = os.path.join(os.path.dirname(current_dir), "configs", "families")
        
        if os.path.exists(library_families_dir):
            try:
                for filename in os.listdir(library_families_dir):
                    if filename.endswith("_family.json"):
                        family_name = filename.replace("_family.json", "")
                        family_path = os.path.join(library_families_dir, filename)
                        try:
                            with open(family_path, 'r') as f:
                                family_config = json.load(f)
                                families[family_name] = family_config
                                # print(f"Debug: Loaded library family '{family_name}' with {len(family_config.get('nodes', {}))} nodes")
                        except Exception as e:
                            logger.error(f"Error loading library family config {filename}: {e}")
            except Exception as e:
                logger.error(f"Error reading library families directory: {e}")
        
        return families
    
    def _resolve_family_nav_coordinate(self, family_name: str, family_config: dict, all_families: dict = None) -> str:
        """Resolve nav coordinate for family using parent chain traversal."""
        # First check if this family is directly in nav config
        nav_coord = self.family_mappings.get(family_name)
        if nav_coord:
            return nav_coord
        
        # Check if family has explicit parent field
        parent = family_config.get("parent")
        if parent is None:
            # No parent = top-level family, should be in nav_config
            # If not found, return family_name for semantic space
            return family_name
        
        if parent and all_families and parent in all_families:
            # Recursively resolve parent coordinate
            parent_config = all_families[parent]
            parent_coord = self._resolve_family_nav_coordinate(parent, parent_config, all_families)
            return parent_coord
        
        # Fallback: family exists in semantic space only
        return family_name
    
    def _convert_family_to_coordinates(self, family_config: dict, family_name: str, all_families: dict = None) -> dict:
        """Build address lookup for family nodes without duplicating data."""
        address_lookup = {}
        family_nodes = family_config.get("nodes", {})
        
        # Get the nav coordinate for this family, using parent chain resolution
        nav_coord = self._resolve_family_nav_coordinate(family_name, family_config, all_families)
        has_nav_coord = bool(nav_coord) and nav_coord in self.family_mappings.values()
        
        logger.debug(f"Family '{family_name}' - nav_coord: '{nav_coord}', has_nav_coord: {has_nav_coord}")
        logger.debug(f"family_mappings.values(): {list(self.family_mappings.values())}")
        
        # Process each node once and create address mappings
        for node_id, node_data in family_nodes.items():
            # Create a copy to avoid mutating the original data
            processed_node = node_data.copy()
            
            # Override prompt if title exists, otherwise ensure prompt exists
            if "title" in node_data:
                processed_node["prompt"] = node_data["title"]
            elif "prompt" not in processed_node:
                processed_node["prompt"] = f"Node {node_id}"
            
            # Ensure options exist for auto-generation
            if "options" not in processed_node:
                processed_node["options"] = {}
            
            # Copy family domain to each node if not already set
            if "domain" not in processed_node and "domain" in family_config:
                processed_node["domain"] = family_config["domain"]
            
            # Handle nested callable structure if it exists
            if "callable" in node_data:
                callable_info = node_data["callable"]
                processed_node.update({
                    "function_name": callable_info.get("function_name"),
                    "import_path": callable_info.get("import_path"),
                    "import_object": callable_info.get("import_object"),
                    "is_async": callable_info.get("is_async", False),
                    "args_schema": callable_info.get("args_schema", {})
                })
                del processed_node["callable"]
            
            # Create address mappings - all point to the same node object
            # 1. Primary semantic address (from JSON)
            address_lookup[node_id] = processed_node
            
            # 2. Legacy coordinate if specified (DISABLED - using semantic IDs only)
            # if "legacy_coordinate" in node_data:
            #     address_lookup[node_data["legacy_coordinate"]] = processed_node
            
            # 3. Nav coordinate for nav families only
            if has_nav_coord:
                if node_id == family_name:
                    # Root family node maps to nav coordinate
                    nav_address = nav_coord
                else:
                    # Sub-nodes get nav coordinate path
                    if node_id.startswith(f"{family_name}."):
                        relative_path = node_id[len(family_name) + 1:]
                        nav_address = f"{nav_coord}.{relative_path}"
                    else:
                        nav_address = f"{nav_coord}.{node_id}"
                
                address_lookup[nav_address] = processed_node
                logger.debug(f"Added nav coordinate '{nav_address}' for node '{node_id}'")
            else:
                logger.debug(f"SKIPPED nav coordinate for node '{node_id}' in family '{family_name}' (no nav coord)")
        
        return address_lookup
    
    def _build_numeric_map(self) -> dict:
        """Build clean numeric-only node map using proper parent hierarchy.
        
        Builds tree structure based on parent relationships:
        - Top-level families (parent: null) get nav coordinates: 0.1, 0.2, 0.3, ...
        - Child families get hierarchical coordinates based on parent chain
        """
        numeric_nodes = {}
        
        # Load all family configurations
        families = self._load_family_configs()
        
        # Build family tree structure using parent relationships
        family_tree = self._build_family_tree(families)
        
        # Assign coordinates to family tree recursively
        self._assign_family_coordinates(family_tree, families, numeric_nodes)
        
        return numeric_nodes
    
    def _build_family_tree(self, families: dict) -> dict:
        """Build hierarchical family tree using parent relationships."""
        tree = {}
        
        # First pass: identify top-level families (parent: null)
        top_level = []
        for family_name, family_config in families.items():
            parent = family_config.get("parent")
            if parent is None:
                # Check if this family is in nav_config
                nav_coord = self.family_mappings.get(family_name)
                if nav_coord:
                    top_level.append(family_name)
        
        # Sort top-level families by nav coordinate for consistent ordering
        top_level.sort(key=lambda f: self.family_mappings.get(f, "999"))
        
        # Build tree recursively
        for family_name in top_level:
            tree[family_name] = self._build_family_subtree(family_name, families)
        
        return tree
    
    def _build_family_subtree(self, parent_family: str, families: dict) -> dict:
        """Recursively build subtree for a family."""
        subtree = {"_family_config": families[parent_family], "_children": {}}
        
        # Find all children of this family
        for family_name, family_config in families.items():
            if family_config.get("parent") == parent_family:
                subtree["_children"][family_name] = self._build_family_subtree(family_name, families)
        
        return subtree
    
    def _assign_family_coordinates(self, family_tree: dict, families: dict, numeric_nodes: dict, base_coord: str = "0"):
        """Recursively assign coordinates to families in the tree."""
        child_index = 1
        
        for family_name, subtree in family_tree.items():
            family_config = subtree["_family_config"]
            
            # Determine coordinate for this family
            if base_coord == "0":
                # Top-level family - use nav coordinate
                nav_coord = self.family_mappings.get(family_name)
                if not nav_coord:
                    continue
                family_coord = nav_coord
            else:
                # Child family - extend parent coordinate
                family_coord = f"{base_coord}.{child_index}"
                child_index += 1
            
            # Process nodes in this family
            family_nodes = family_config.get("nodes", {})
            node_names = list(family_nodes.keys())
            
            for i, node_id in enumerate(node_names):
                node_data = family_nodes[node_id]
                
                if i == 0:
                    # First node gets the family coordinate
                    numeric_coord = family_coord
                else:
                    # Subsequent nodes get sub-coordinates
                    numeric_coord = f"{family_coord}.{i}"
                
                # Process node data
                processed_node = node_data.copy()
                if "title" in node_data:
                    processed_node["prompt"] = node_data["title"]
                if "options" not in processed_node:
                    processed_node["options"] = {}
                
                # Handle callable structure
                if "callable" in node_data:
                    callable_info = node_data["callable"]
                    processed_node.update({
                        "function_name": callable_info.get("function_name"),
                        "import_path": callable_info.get("import_path"),
                        "import_object": callable_info.get("import_object"),
                        "is_async": callable_info.get("is_async", False),
                        "args_schema": callable_info.get("args_schema", {})
                    })
                    del processed_node["callable"]

                numeric_nodes[numeric_coord] = processed_node
            
            # Recursively assign coordinates to children
            if subtree["_children"]:
                self._assign_family_coordinates(subtree["_children"], families, numeric_nodes, family_coord)

    def _resolve_combo_node_addresses(self) -> dict:
        """Build combo address mapping supporting mixed semantic/numeric coordinates.
        
        Creates all possible address combinations:
        - Pure semantic: system_omnitool_list_tools
        - Pure numeric: 0.0.0.1 
        - Mixed: 0.0.omnitool.1, 0.system.omnitool.list_tools
        - Any valid combination of numeric and semantic path components
        """
        combo_nodes = {}
        
        # Start with both base collections
        combo_nodes.update(self.nodes)
        combo_nodes.update(self.numeric_nodes)
        
        # TODO: Build mixed combinations
        # For now, return the union of semantic + numeric
        # Future: Generate all valid mixed coordinate combinations
        
        return combo_nodes

    def _load_shortcuts(self) -> None:
        """Load shortcuts from SystemConfigLoader only. Override in subclasses for different layers."""
        # Shortcuts are loaded directly from SystemConfigLoader when needed
        # They are NOT stored in session_vars as they come from JSON config files
        pass
    
    def get_shortcuts(self) -> dict:
        """Get shortcuts directly from SystemConfigLoader, not from session_vars."""
        if hasattr(self, 'system_config_loader'):
            return self.system_config_loader.load_shortcuts(dev_config_path=None)
        return {}
    
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
            logger.error(f"Error loading library config from {filename}: {e}")
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
                    logger.error(f"Error loading user config from {user_config_path}: {e}")
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
            logger.error(f"Error loading config from {filename}: {e}")
            return {}
    
    def _load_shortcuts_file(self, filename: str) -> dict:
        """Load shortcuts from a specific JSON file."""
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
                # print(f"Warning: Shortcuts file not found: {file_path}")
                return {}
        except Exception as e:
            logger.error(f"Error loading shortcuts from {filename}: {e}")
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
            logger.error(f"Error saving shortcut to {filename}: {e}")
    
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
        base_config = self._load_config_file("system_base_config.json")
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
            "domain": "main_menu",
            "options": {},  # Will be auto-generated from families
            "_source": "base.py:node_0_hardcoded"
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
            logger.debug(f"Added {len(family_nodes)} nodes from '{family_name}' family")
        
        logger.debug(f"Total family nodes loaded: {total_family_nodes}")
        
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
                "signature_override": node.get("signature_override"),  # Copy signature override
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
        # Check family nodes first, then numeric nodes, then legacy nodes as fallback
        node = self.nodes.get(self.current_position)
        if node is None and hasattr(self, 'numeric_nodes'):
            node = self.numeric_nodes.get(self.current_position)
        if node is None and hasattr(self, 'legacy_nodes'):
            node = self.legacy_nodes.get(self.current_position, {})
        return node or {}
    
    def _get_domain_chain(self) -> str:
        """Build domain chain by walking from root to current position, showing domain of each node."""
        domains = []
        
        # Split current position into parts (e.g., "0.3.1.2" -> ["0", "3", "1", "2"])
        if self.current_position:
            parts = self.current_position.split('.')
            
            # Walk from root to current position, checking each level for domain
            for i in range(len(parts)):
                # Build position string for current level (e.g., "0", "0.3", "0.3.1", etc.)
                level_position = '.'.join(parts[:i+1])
                
                # Check both nodes and numeric_nodes for domain
                node = self.nodes.get(level_position) or self.numeric_nodes.get(level_position, {})
                
                # Add domain or error message for missing domain
                if 'domain' in node:
                    domains.append(node['domain'])
                else:
                    domains.append(f"NO DOMAIN AT NODE {level_position}")
        
        # If no position, use root domain from config
        if not domains:
            domains.append(self.domain)
        
        # Join with dots, avoiding duplicates but preserving order
        return '.'.join(dict.fromkeys(domains))  # dict.fromkeys preserves order and removes dupes
    
    def _build_response(self, payload: dict) -> dict:
        """Build standard response with current state."""
        # Get _source from current node
        current_node = self._get_current_node()
        node_source = current_node.get("_source", f"coordinate:{self.current_position}") if current_node else f"coordinate:{self.current_position}"

        base = {
            "state_id": datetime.datetime.utcnow().isoformat(),
            "position": self.current_position,
            "stack": self.stack.copy(),
            "session_vars_keys": list(self.session_vars.keys()),
            "recording_pathway": self.recording_pathway,
            "app_id": self.app_id,
            "domain": self._get_domain_chain(),
            "role": self.role,
            "shortcuts": self.session_vars.get("_shortcuts", {}),  # Include shortcuts for game state
            "_source": node_source
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
        """Initialize user's HEAVEN_DATA_DIR structure for session data only."""
        import os
        import json
        import shutil
        
        heaven_data_dir = os.environ.get('HEAVEN_DATA_DIR')
        if not heaven_data_dir:
            return False
        
        version = self._get_safe_version()
        app_data_dir = os.path.join(heaven_data_dir, f"{self.app_id}_{version}")
        
        # Check if configs need to be copied (for upgrades from versions before config copying existed)
        target_configs_dir = os.path.join(app_data_dir, "configs")
        needs_config_copy = not os.path.exists(target_configs_dir)

        # If directory exists AND has configs, we're done
        if os.path.exists(app_data_dir) and not needs_config_copy:
            return True  # Already initialized

        try:
            # Create directory structure for session data only
            os.makedirs(os.path.join(app_data_dir, "sessions"), exist_ok=True)
            os.makedirs(os.path.join(app_data_dir, "pathways"), exist_ok=True)
            os.makedirs(os.path.join(app_data_dir, "data"), exist_ok=True)
            
            # Create dev config directory for user customizations
            dev_config_dir = os.path.join(app_data_dir, "dev_configs")
            os.makedirs(dev_config_dir, exist_ok=True)
            
            # Create empty dev config templates with correct schema
            user_config_template = {
                "override_nodes": {},
                "add_nodes": {},
                "exclude_nodes": []
            }
            
            # Create all dev config files as empty templates
            dev_configs = [
                "dev_base_config.json",
                "dev_agent_config.json", 
                "dev_user_config.json",
                "dev_base_shortcuts.json",
                "dev_agent_shortcuts.json",
                "dev_user_shortcuts.json",
                "dev_base_zone_config.json",
                "dev_agent_zone_config.json",
                "dev_user_zone_config.json"
            ]
            
            for config_file in dev_configs:
                config_path = os.path.join(dev_config_dir, config_file)
                if not os.path.exists(config_path):  # Don't overwrite existing dev configs
                    with open(config_path, 'w') as f:
                        json.dump(user_config_template, f, indent=2)

            # Copy system configs from library to HEAVEN_DATA_DIR
            # This makes configs "hot" (editable) while preserving per-version state
            current_dir = os.path.dirname(os.path.abspath(__file__))
            library_configs_dir = os.path.join(os.path.dirname(current_dir), "configs")

            if os.path.exists(library_configs_dir) and needs_config_copy:
                shutil.copytree(library_configs_dir, target_configs_dir)
                logger.info(f"Copied system configs to {target_configs_dir}")

            logger.info(f"Initialized HEAVEN_DATA_DIR for {self.app_id}_{version} at {app_data_dir}")
            logger.info(f"Created dev config templates in {dev_config_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing HEAVEN_DATA_DIR: {e}")
            return False
    
    def _process_callable_node(self, node_data: dict, coordinate: str) -> tuple:
        """
        Shared logic for processing callable nodes with imports/function_code.
        Used by both _build_coordinate_nodes and _meta_add_node.
        
        Returns: (result_detail_string, success_bool)
        """
        function_name = node_data.get("function_name")
        if not function_name:
            return "callable node without function_name", False
        
        is_async = node_data.get("is_async", False)
        
        # Approach 1: Import from external module
        if node_data.get("import_path") and node_data.get("import_object"):
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
            if node.get("import_path") and node.get("import_object"):
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
        
        # Extract docstring with HEAVEN tool schema fallback chain
        docstring = None
        
        # 1. Try HEAVEN tool generation for rich schema through agent initialization
        try:
            from heaven_base.make_heaven_tool_from_docstring import make_heaven_tool_from_docstring
            from heaven_base.baseheavenagent import BaseHeavenAgent, HeavenAgentConfig
            from heaven_base.unified_chat import UnifiedChat, ProviderEnum
            from heaven_base.memory.history import History
            
            # Generate HEAVEN tool from function
            heaven_tool_class = make_heaven_tool_from_docstring(function)
            
            # Create temporary agent to access tool schema properly
            config = HeavenAgentConfig(
                name="TempSchemaAgent",
                system_prompt="Temporary agent for schema extraction",
                tools=[heaven_tool_class],
                provider=ProviderEnum.OPENAI,
                model="gpt-4o-mini",
                temperature=0.7,
                max_tokens=1000
            )
            
            unified_chat = UnifiedChat()
            history = History(messages=[])
            agent = BaseHeavenAgent(config, unified_chat, history)
            
            # Find our tool in the agent's tools list
            for tool in agent.tools:
                tool_class_name = type(tool).__name__.lower()
                if function.__name__.replace('_', '').lower() in tool_class_name:
                    if hasattr(tool, 'args_schema') and tool.args_schema:
                        # Create instance to access arguments
                        schema_instance = tool.args_schema()
                        if hasattr(schema_instance, 'arguments'):
                            # Format the args_schema as readable documentation
                            docstring = self._format_heaven_tool_schema(schema_instance.arguments, function_name)
                    break
            
        except Exception:
            # Fall through to docstring extraction
            pass
        
        # 2. Fall back to raw docstring extraction
        if not docstring:
            try:
                raw_docstring = function.__doc__
                if raw_docstring and raw_docstring.strip():
                    docstring = raw_docstring.strip()
            except Exception:
                pass
        
        # 3. Final fallback to warning message
        if not docstring:
            docstring = f"⚠️ No docstring available for {function_name}"
        
        return signature, docstring
    
    def _format_heaven_tool_schema(self, schema_data, function_name: str) -> str:
        """Format HEAVEN tool args_schema into readable documentation."""
        try:
            if not schema_data or not isinstance(schema_data, dict):
                return f"Auto-generated tool for {function_name} (no parameters)"
            
            # Format each parameter
            formatted_lines = [f"📋 **Rich Schema for {function_name}()**", ""]
            
            for param_name, param_info in schema_data.items():
                param_type = param_info.get('type', 'unknown')
                description = param_info.get('description', f'Parameter {param_name}')
                required = param_info.get('required', True)
                
                # Format type information with rich details
                type_info = self._format_parameter_type(param_info, param_name)
                
                # Build parameter line
                req_marker = "**required**" if required else "*optional*"
                formatted_lines.append(f"• `{param_name}` ({type_info}) - {req_marker}")
                formatted_lines.append(f"  {description}")
                
                # Add nested object details
                if param_type == 'object' and 'nested' in param_info:
                    nested_info = param_info['nested']
                    formatted_lines.append("  Object fields:")
                    for field_name, field_data in nested_info.items():
                        if isinstance(field_data, dict) and field_name in field_data:
                            field_info = field_data[field_name]
                            field_type = field_info.get('type', 'unknown')
                            field_desc = field_info.get('description', f'{field_name} field')
                            field_req = field_info.get('required', True)
                            req_str = " *required*" if field_req else " *optional*"
                            formatted_lines.append(f"    - `{field_name}` ({field_type}){req_str}: {field_desc}")
                
                formatted_lines.append("")  # Empty line between parameters
            
            return "\n".join(formatted_lines)
            
        except Exception as e:
            return f"Auto-generated tool for {function_name} (schema parsing error: {str(e)})"
    
    def _format_parameter_type(self, param_info, param_name: str) -> str:
        """Format parameter type information with rich details."""
        param_type = param_info.get('type', 'unknown')
        
        if param_type == 'array':
            items_info = param_info.get('items', {})
            item_type = items_info.get('type', 'unknown')
            return f"List[{item_type}]"
        elif param_type == 'dict':
            if 'additionalProperties' in param_info:
                value_type = param_info['additionalProperties'].get('type', 'Any')
                return f"Dict[str, {value_type}]"
            else:
                return "Dict[str, Any]"
        elif param_type == 'object':
            return f"{param_name.title()}Object"
        else:
            return param_type

    def _get_node_menu(self, node_coord: str) -> dict:
        """Get menu display for a node."""
        # Use combo_nodes for unified address resolution
        node = self.combo_nodes.get(node_coord) if hasattr(self, 'combo_nodes') else None
        if not node:
            return {"error": f"Node {node_coord} not found"}
            
        menu_options = {}
        
        # For callable nodes, add exec option  
        if node.get("type") == "Callable" or "callable" in node:
            menu_options["exec"] = "execute"
        
        # Node-specific options
        options = node.get("options", {})
        for i, (key, target) in enumerate(options.items(), start=1):
            # Use combo_nodes for unified address resolution
            target_node = self.combo_nodes.get(target) if hasattr(self, 'combo_nodes') else None
            
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
        
        # For callable nodes, extract function documentation
        if node.get("type") == "Callable":
            function_name = node.get("function_name")
            if function_name:
                func_signature, func_docstring = self._get_function_docs(function_name, node)
                signature = func_signature
                # Don't override description - preserve original HEAVEN resolution protocol
                # The renderer will handle description resolution properly
            
            # Check for explicit signature override
            if "signature_override" in node:
                signature = node["signature_override"]
        
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
            "args_schema": node.get("args_schema", {}),
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
    
    def _get_session_directory(self):
        """Get the session directory path for this shell type."""
        import os
        from datetime import datetime
        
        heaven_data_dir = os.environ.get('HEAVEN_DATA_DIR', '/tmp/heaven_data')
        today = datetime.now().strftime('%Y-%m-%d')
        session_dir = os.path.join(heaven_data_dir, 'tmp', 'tree_shell_sessions', today)
        
        # Create directory if it doesn't exist
        os.makedirs(session_dir, exist_ok=True)
        
        return session_dir
    
    def _get_session_file_path(self, session_id=None):
        """Get the full path to the session file."""
        session_dir = self._get_session_directory()
        
        if session_id:
            # Agent shell with specific session_id
            filename = f"{session_id}.json"
        else:
            # User shell with default session
            filename = "user_session.json"
        
        return os.path.join(session_dir, filename)
    
    def _save_session_state(self, session_id=None):
        """Save current session state to pickle file for proper Python object preservation."""
        import pickle
        try:
            session_file = self._get_session_file_path(session_id).replace('.json', '.pkl')
            
            # Exclude config-based data that should reload from JSON every time
            session_vars_to_save = {k: v for k, v in self.session_vars.items() if k != '_shortcuts'}
            
            state_data = {
                "current_position": self.current_position,
                "stack": self.stack.copy(),
                "session_vars": session_vars_to_save,
                "execution_history": self.execution_history.copy(),
                "saved_pathways": self.saved_pathways.copy(),
                "saved_templates": self.saved_templates.copy(),
                "graph_ontology": self.graph_ontology.copy(),
                "chain_results": getattr(self, 'chain_results', {}),
                "step_counter": getattr(self, 'step_counter', 0),
                "app_id": self.app_id,
                "domain": self.domain,
                "role": self.role,
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
            
            with open(session_file, 'wb') as f:
                pickle.dump(state_data, f)
                
        except Exception as e:
            logger.warning(f"Could not save session state: {e}")
    
    def _load_session_state(self, session_id=None):
        """Load session state from pickle file if it exists, gracefully handling errors."""
        import pickle
        try:
            session_file = self._get_session_file_path(session_id).replace('.json', '.pkl')
            
            if not os.path.exists(session_file):
                # Check for old JSON format and migrate if exists
                json_file = self._get_session_file_path(session_id)
                if os.path.exists(json_file):
                    self._migrate_json_to_pickle(json_file, session_file)
                else:
                    return  # No previous session, start fresh
            
            with open(session_file, 'rb') as f:
                state_data = pickle.load(f)
            
            # Restore state
            self.current_position = state_data.get("current_position", "0")
            self.stack = state_data.get("stack", ["0"])
            self.execution_history = state_data.get("execution_history", [])
            self.saved_pathways = state_data.get("saved_pathways", {})
            self.saved_templates = state_data.get("saved_templates", {})
            self.graph_ontology.update(state_data.get("graph_ontology", {}))
            
            # Handle session_vars with error recovery, excluding config-based data
            raw_session_vars = state_data.get("session_vars", {})
            # Remove config-based data that should reload from JSON every time
            raw_session_vars.pop('_shortcuts', None)
            self.session_vars = self._clean_session_vars(raw_session_vars)
            
            # Optional chain state
            if hasattr(self, 'chain_results'):
                self.chain_results = state_data.get("chain_results", {})
            if hasattr(self, 'step_counter'):
                self.step_counter = state_data.get("step_counter", 0)
                
        except Exception as e:
            logger.warning(f"Could not load session state, starting fresh: {e}")
    
    def _clean_session_vars(self, raw_session_vars: dict) -> dict:
        """Clean session vars by removing any objects that can't be properly accessed."""
        import pickle
        cleaned_vars = {}
        removed_keys = []
        
        for key, value in raw_session_vars.items():
            try:
                # Test if we can access the object and pickle it again
                # This will fail if classes are missing or objects are corrupted
                pickle.dumps(value)
                repr(value)  # Test if object is accessible
                cleaned_vars[key] = value
            except Exception as e:
                removed_keys.append(key)
                logger.warning(f"Removed corrupted session variable '{key}': {e}")
        
        if removed_keys:
            logger.info(f"Session recovery: Removed {len(removed_keys)} corrupted variables, kept {len(cleaned_vars)} good ones")
        
        return cleaned_vars
    
    def _migrate_json_to_pickle(self, json_file: str, pickle_file: str):
        """Migrate existing JSON session file to pickle format."""
        import json
        import pickle
        try:
            with open(json_file, 'r') as f:
                json_data = json.load(f)
            
            with open(pickle_file, 'wb') as f:
                pickle.dump(json_data, f)
            
            # Remove old JSON file after successful migration
            os.remove(json_file)
            logger.info(f"Migrated session from JSON to pickle: {pickle_file}")
            
        except Exception as e:
            logger.warning(f"Could not migrate JSON session file: {e}")
    
    async def main(self):
        """
        Main entry point for TreeShell execution.
        
        This provides the same interface that was previously in default_chat_app.py
        but as a method on the TreeShell instance itself.
        
        Returns:
            self: The initialized TreeShell instance ready for command handling
        """
        return await self.run()