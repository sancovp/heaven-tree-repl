#!/usr/bin/env python3
"""
Meta Operations module - Variable management and session operations.
"""
import json
import datetime
import sys


class MetaOperationsMixin:
    """Mixin class providing meta operations functionality."""
    
    def _meta_save_var(self, final_args: dict) -> tuple:
        """Save variable to session."""
        name = final_args.get("name")
        value = final_args.get("value")
        if not name:
            return {"error": "Variable name required"}, False
        self.session_vars[name] = value
        result = {"saved": True, "variable": name, "value": value}
        return result, True
        
    def _meta_get_var(self, final_args: dict) -> tuple:
        """Get variable from session."""
        name = final_args.get("name")
        if not name:
            return {"error": "Variable name required"}, False
        if name not in self.session_vars:
            return {"error": f"Variable '{name}' not found"}, False
        result = {"variable": name, "value": self.session_vars[name]}
        return result, True
        
    def _meta_append_to_var(self, final_args: dict) -> tuple:
        """Append to existing variable."""
        name = final_args.get("name")
        value = final_args.get("value")
        if not name:
            return {"error": "Variable name required"}, False
        if name not in self.session_vars:
            return {"error": f"Variable '{name}' not found"}, False
            
        current = self.session_vars[name]
        if isinstance(current, list):
            current.append(value)
        elif isinstance(current, str):
            self.session_vars[name] = current + str(value)
        else:
            return {"error": f"Cannot append to variable of type {type(current)}"}, False
        result = {"appended": True, "variable": name, "new_value": self.session_vars[name]}
        return result, True
        
    def _meta_delete_var(self, final_args: dict) -> tuple:
        """Delete variable from session."""
        name = final_args.get("name")
        if not name:
            return {"error": "Variable name required"}, False
        if name not in self.session_vars:
            return {"error": f"Variable '{name}' not found"}, False
        del self.session_vars[name]
        result = {"deleted": True, "variable": name}
        return result, True
        
    def _meta_list_vars(self, final_args: dict) -> tuple:
        """List all session variables."""
        result = {
            "variables": dict(self.session_vars),
            "count": len(self.session_vars)
        }
        return result, True
        
    def _meta_save_to_file(self, final_args: dict) -> tuple:
        """Save variable to file."""
        filename = final_args.get("filename")
        var_name = final_args.get("var_name")
        if not filename or not var_name:
            return {"error": "Both filename and var_name required"}, False
        if var_name not in self.session_vars:
            return {"error": f"Variable '{var_name}' not found"}, False
        
        try:
            with open(filename, 'w') as f:
                if isinstance(self.session_vars[var_name], (dict, list)):
                    json.dump(self.session_vars[var_name], f, indent=2)
                else:
                    f.write(str(self.session_vars[var_name]))
            result = {"saved": True, "filename": filename, "variable": var_name}
            return result, True
        except Exception as e:
            return {"error": f"Failed to save file: {e}"}, False
            
    def _meta_load_from_file(self, final_args: dict) -> tuple:
        """Load file content into variable."""
        filename = final_args.get("filename")
        var_name = final_args.get("var_name")
        if not filename or not var_name:
            return {"error": "Both filename and var_name required"}, False
            
        try:
            with open(filename, 'r') as f:
                content = f.read()
                # Try to parse as JSON first
                try:
                    value = json.loads(content)
                except json.JSONDecodeError:
                    # Fall back to string
                    value = content
            self.session_vars[var_name] = value
            result = {"loaded": True, "filename": filename, "variable": var_name, "value": value}
            return result, True
        except Exception as e:
            return {"error": f"Failed to load file: {e}"}, False
            
    def _meta_export_session(self, final_args: dict) -> tuple:
        """Export complete session state to file."""
        filename = final_args.get("filename")
        if not filename:
            return {"error": "Filename required"}, False
            
        session_data = {
            "session_vars": self.session_vars,
            "execution_history": self.execution_history,
            "saved_pathways": self.saved_pathways,
            "saved_templates": self.saved_templates,
            "graph_ontology": self.graph_ontology,
            "current_position": self.current_position,
            "stack": self.stack,
            "exported": datetime.datetime.utcnow().isoformat()
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(session_data, f, indent=2)
            result = {"exported": True, "filename": filename, "data_size": len(str(session_data))}
            return result, True
        except Exception as e:
            return {"error": f"Failed to export session: {e}"}, False
            
    def _meta_session_stats(self, final_args: dict) -> tuple:
        """Get session statistics."""
        stats = {
            "session_variables": len(self.session_vars),
            "execution_history_size": len(self.execution_history),
            "saved_pathways": len(self.saved_pathways),
            "ontology_domains": len(self.graph_ontology["domains"]),
            "ontology_pathways": len(self.graph_ontology["pathway_index"]),
            "current_position": self.current_position,
            "stack_depth": len(self.stack),
            "total_nodes": len(self.nodes),
            "recording_pathway": self.recording_pathway
        }
        
        # Memory usage (approximate)
        total_memory = 0
        for var_name, var_value in self.session_vars.items():
            total_memory += sys.getsizeof(var_value)
        stats["approximate_memory_bytes"] = total_memory
        
        result = {"session_stats": stats}
        return result, True
        
    # === Tree Structure CRUD Operations ===
    
    def _resolve_coordinate_to_semantic(self, coordinate: str) -> str:
        """Convert numeric coordinate to semantic name if needed."""
        if not coordinate:
            return coordinate
            
        # If coordinate is numeric (all digits and dots), try to resolve to semantic
        if coordinate.replace('.', '').isdigit():
            if hasattr(self, 'combo_nodes') and coordinate in self.combo_nodes:
                target_node = self.combo_nodes[coordinate]
                target_prompt = target_node.get('prompt', target_node.get('title', ''))
                
                # Find semantic name with matching prompt/title
                for addr, node_data in self.combo_nodes.items():
                    if not addr.replace('.', '').isdigit():  # semantic address
                        node_prompt = node_data.get('prompt', node_data.get('title', ''))
                        if target_prompt and target_prompt == node_prompt:
                            return addr  # Found semantic equivalent
                        
        # Return as-is if already semantic or no resolution found
        return coordinate

    def _meta_add_node(self, final_args: dict) -> tuple:
        """Add a new node to the tree structure with multiple callable options."""
        coordinate = final_args.get("coordinate")
        node_data = final_args.get("node_data")
        
        if not coordinate:
            return {"error": "Node coordinate required"}, False
            
        # Resolve numeric coordinates to semantic names before saving
        original_coordinate = coordinate
        coordinate = self._resolve_coordinate_to_semantic(coordinate)
        if not node_data or not isinstance(node_data, dict):
            return {"error": "Node data (dict) required"}, False
            
        if coordinate in self.nodes:
            return {"error": f"Node {coordinate} already exists"}, False
            
        # Validate required node fields
        required_fields = ["type", "prompt"]
        for field in required_fields:
            if field not in node_data:
                return {"error": f"Node data missing required field: {field}"}, False
        
        # Add default fields if missing
        if "description" not in node_data:
            node_data["description"] = f"Node at {coordinate}"
        if "signature" not in node_data:
            node_data["signature"] = f"execute() -> result"
        if "options" not in node_data:
            node_data["options"] = {}
        if "args_schema" not in node_data:
            node_data["args_schema"] = {}
            
        # Handle Callable nodes using shared processing logic
        if node_data["type"] == "Callable":
            function_name = node_data.get("function_name")
            is_async = node_data.get("is_async")
            
            if not function_name:
                return {"error": "Callable nodes require 'function_name' field"}, False
            if is_async is None:
                return {"error": "Callable nodes require 'is_async' field (true/false)"}, False
            
            # Use shared callable node processing function
            result_detail, success = self._process_callable_node(node_data, coordinate)
            if not success:
                return {"error": result_detail}, False
        else:
            result_detail = "static node"
        
        # Add the node to runtime
        self.nodes[coordinate] = node_data.copy()
        
        # Persist to HEAVEN_DATA_DIR if available
        persistence_result = self._persist_node_to_heaven_data_dir(coordinate, node_data)
        
        result = {
            "added": True,
            "coordinate": coordinate,
            "node_type": node_data["type"],
            "prompt": node_data["prompt"],
            "implementation": result_detail,
            "persistence": persistence_result
        }
        return result, True
    
    def _meta_update_node(self, final_args: dict) -> tuple:
        """Update an existing node in the tree."""
        coordinate = final_args.get("coordinate")
        updates = final_args.get("updates")
        
        if not coordinate:
            return {"error": "Node coordinate required"}, False
        if not updates or not isinstance(updates, dict):
            return {"error": "Updates (dict) required"}, False
            
        if coordinate not in self.nodes:
            return {"error": f"Node {coordinate} not found"}, False
            
        # Apply updates
        old_node = self.nodes[coordinate].copy()
        self.nodes[coordinate].update(updates)
        
        result = {
            "updated": True,
            "coordinate": coordinate,
            "old_data": old_node,
            "new_data": self.nodes[coordinate]
        }
        return result, True
    
    def _meta_delete_node(self, final_args: dict) -> tuple:
        """Delete a node from the tree structure."""
        coordinate = final_args.get("coordinate")
        
        if not coordinate:
            return {"error": "Node coordinate required"}, False
            
        if coordinate not in self.nodes:
            return {"error": f"Node {coordinate} not found"}, False
            
        # Don't allow deletion of core meta operations
        if coordinate.startswith("0.0.2."):
            return {"error": "Cannot delete core meta operations"}, False
            
        deleted_node = self.nodes[coordinate].copy()
        del self.nodes[coordinate]
        
        result = {
            "deleted": True,
            "coordinate": coordinate,
            "deleted_node": deleted_node
        }
        return result, True
    
    def _meta_list_nodes(self, final_args: dict) -> tuple:
        """List nodes in the tree structure."""
        pattern = final_args.get("pattern", "")
        
        if pattern:
            # Filter nodes by pattern
            matching_nodes = {}
            for coord, node in self.nodes.items():
                if pattern in coord or pattern in node.get("prompt", ""):
                    matching_nodes[coord] = {
                        "type": node.get("type"),
                        "prompt": node.get("prompt"),
                        "description": node.get("description", "")
                    }
        else:
            # Return all nodes
            matching_nodes = {}
            for coord, node in self.nodes.items():
                matching_nodes[coord] = {
                    "type": node.get("type"),
                    "prompt": node.get("prompt"),
                    "description": node.get("description", "")
                }
        
        result = {
            "total_nodes": len(self.nodes),
            "matching_nodes": len(matching_nodes),
            "pattern": pattern,
            "nodes": matching_nodes
        }
        return result, True
    
    def _meta_get_node(self, final_args: dict) -> tuple:
        """Get details of a specific node."""
        coordinate = final_args.get("coordinate")
        
        if not coordinate:
            return {"error": "Node coordinate required"}, False
            
        if coordinate not in self.nodes:
            return {"error": f"Node {coordinate} not found"}, False
            
        node = self.nodes[coordinate]
        result = {
            "coordinate": coordinate,
            "node_data": node.copy(),
            "exists": True
        }
        return result, True
    
    def _persist_node_to_heaven_data_dir(self, coordinate: str, node_data: dict) -> dict:
        """Persist a node to the appropriate family file in HEAVEN_DATA_DIR."""
        import os
        import json
        
        heaven_data_dir = os.environ.get('HEAVEN_DATA_DIR')
        if not heaven_data_dir:
            return {"status": "skipped", "reason": "HEAVEN_DATA_DIR not set"}
        
        try:
            # Get version for directory name
            version = self._get_safe_version()
            app_data_dir = os.path.join(heaven_data_dir, f"{self.app_id}_{version}")
            families_dir = os.path.join(app_data_dir, "configs", "families")
            
            # Determine which family this coordinate belongs to
            family_name = self._determine_family_for_coordinate(coordinate)
            if not family_name:
                return {"status": "error", "reason": f"Could not determine family for coordinate {coordinate}"}
            
            family_file = os.path.join(families_dir, f"{family_name}_family.json")
            
            # Load existing family config or create new one
            if os.path.exists(family_file):
                with open(family_file, 'r') as f:
                    family_config = json.load(f)
            else:
                family_config = {"nodes": {}}
            
            # Convert coordinate back to family-relative node ID
            family_node_id = self._coordinate_to_family_node_id(coordinate, family_name)
            
            # Create family node structure from coordinate node
            family_node = {
                "title": node_data["prompt"],
                "description": node_data["description"]
            }
            
            # Add callable information if present
            if node_data.get("type") == "Callable":
                family_node["callable"] = {
                    "function_name": node_data.get("function_name"),
                    "is_async": node_data.get("is_async", False),
                    "args_schema": node_data.get("args_schema", {})
                }
                
                # Include import information if available
                if "import_path" in node_data:
                    family_node["callable"]["import_path"] = node_data["import_path"]
                if "import_object" in node_data:
                    family_node["callable"]["import_object"] = node_data["import_object"]
            
            # Store the node in family config
            if "nodes" not in family_config:
                family_config["nodes"] = {}
            family_config["nodes"][family_node_id] = family_node
            
            # Save updated family config
            os.makedirs(families_dir, exist_ok=True)
            with open(family_file, 'w') as f:
                json.dump(family_config, f, indent=2)
            
            return {
                "status": "success", 
                "family": family_name,
                "family_file": family_file,
                "node_id": family_node_id
            }
            
        except Exception as e:
            return {"status": "error", "reason": str(e)}
    
    def _determine_family_for_coordinate(self, coordinate: str) -> str:
        """Determine which family a coordinate belongs to."""
        # Parse coordinate to determine family
        parts = coordinate.split('.')
        
        if coordinate == "0":
            return "system"  # Root belongs to system family
        
        # For coordinates like 0.0.15, check family mappings
        if len(parts) >= 2:
            nav_coord = f"{parts[0]}.{parts[1]}"  # e.g., "0.0"
            for family_name, family_coord in self.family_mappings.items():
                if family_coord == nav_coord:
                    return family_name
        
        # If it's a semantic coordinate like "system.meta.15", use the first part
        if not parts[0].isdigit():
            return parts[0]
        
        # Default to system for numeric coordinates
        return "system"
    
    def _coordinate_to_family_node_id(self, coordinate: str, family_name: str) -> str:
        """Convert coordinate back to family-relative node ID."""
        parts = coordinate.split('.')
        
        # If it's already semantic, use as-is
        if not parts[0].isdigit():
            return coordinate
        
        # For numeric coordinates like 0.0.15, convert to family.subnode format
        if len(parts) > 2:
            # Convert 0.0.15 to system.15 (remove nav coordinate prefix)
            relative_parts = parts[2:]  # Skip "0.0"
            return f"{family_name}.{'.'.join(relative_parts)}"
        else:
            # Root family node
            return family_name
    
    def _meta_show_config_paths(self, final_args: dict) -> tuple:
        """Display paths to all active configuration files organized by type."""
        import os
        
        heaven_data_dir = os.environ.get('HEAVEN_DATA_DIR')
        version = self._get_safe_version()
        
        config_paths = {
            "heaven_data_dir": heaven_data_dir,
            "app_data_directory": None,
            "configs": {},
            "families": {},
            "shortcuts": {},
            "data_directory": None
        }
        
        if heaven_data_dir:
            app_data_dir = os.path.join(heaven_data_dir, f"{self.app_id}_{version}")
            config_paths["app_data_directory"] = app_data_dir
            config_paths["data_directory"] = os.path.join(app_data_dir, "data")
            
            # Check main config files
            config_files = ["zone_config.json", "nav_config.json", "base_default_config_v2.json"]
            for config_file in config_files:
                user_path = os.path.join(app_data_dir, "configs", config_file)
                library_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "configs", config_file)
                
                config_paths["configs"][config_file] = {
                    "active_path": user_path if os.path.exists(user_path) else library_path,
                    "user_path": user_path,
                    "library_path": library_path,
                    "using_user_config": os.path.exists(user_path)
                }
            
            # Check family files
            families_dir = os.path.join(app_data_dir, "configs", "families")
            library_families_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "configs", "families")
            
            if os.path.exists(families_dir):
                for family_file in os.listdir(families_dir):
                    if family_file.endswith("_family.json"):
                        user_family_path = os.path.join(families_dir, family_file)
                        library_family_path = os.path.join(library_families_dir, family_file)
                        
                        config_paths["families"][family_file] = {
                            "active_path": user_family_path,
                            "user_path": user_family_path,
                            "library_path": library_family_path,
                            "using_user_config": True
                        }
            
            # Add any library families not in user directory
            if os.path.exists(library_families_dir):
                for family_file in os.listdir(library_families_dir):
                    if family_file.endswith("_family.json") and family_file not in config_paths["families"]:
                        library_family_path = os.path.join(library_families_dir, family_file)
                        user_family_path = os.path.join(families_dir, family_file)
                        
                        config_paths["families"][family_file] = {
                            "active_path": library_family_path,
                            "user_path": user_family_path,
                            "library_path": library_family_path,
                            "using_user_config": False
                        }
            
            # Check shortcuts
            shortcuts_dir = os.path.join(app_data_dir, "shortcuts")
            if os.path.exists(shortcuts_dir):
                for shortcut_file in os.listdir(shortcuts_dir):
                    if shortcut_file.endswith(".json"):
                        config_paths["shortcuts"][shortcut_file] = os.path.join(shortcuts_dir, shortcut_file)
        
        else:
            # No HEAVEN_DATA_DIR - using library defaults only
            library_configs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "configs")
            
            config_files = ["zone_config.json", "nav_config.json", "base_default_config_v2.json"]
            for config_file in config_files:
                library_path = os.path.join(library_configs_dir, config_file)
                config_paths["configs"][config_file] = {
                    "active_path": library_path,
                    "user_path": "N/A (HEAVEN_DATA_DIR not set)",
                    "library_path": library_path,
                    "using_user_config": False
                }
        
        result = {
            "config_paths": config_paths,
            "summary": {
                "heaven_data_dir_set": heaven_data_dir is not None,
                "total_configs": len(config_paths["configs"]),
                "total_families": len(config_paths["families"]),
                "total_shortcuts": len(config_paths["shortcuts"]),
                "using_user_configs": any(c["using_user_config"] for c in config_paths["configs"].values()) if config_paths["configs"] else False
            }
        }
        
        return result, True
    
    # === MCP Generator Operations ===
    
    def _meta_init_mcp_config(self, final_args: dict) -> tuple:
        """Initialize MCP generator configuration."""
        from .mcp_generator import TreeShellMCPConfig
        
        # Get current app details to pre-populate config
        app_name = final_args.get("app_name") or getattr(self, 'graph_config', {}).get('app_id', 'treeshell-app')
        import_path = final_args.get("import_path", "my_app")
        factory_function = final_args.get("factory_function", "main")
        description = final_args.get("description") or f"TreeShell MCP server for {app_name}"
        
        # Create default config
        config_dict = {
            "app_name": app_name,
            "import_path": import_path,
            "factory_function": factory_function,
            "description": description,
            "version": "0.1.0",
            "author": "TreeShell User",
            "author_email": "user@example.com"
        }
        
        # Store in session variables
        self.session_vars["mcp_config"] = config_dict
        
        result = {
            "initialized": True,
            "config": config_dict,
            "stored_in_session": "mcp_config"
        }
        return result, True
    
    def _meta_update_mcp_config(self, final_args: dict) -> tuple:
        """Update MCP generator configuration."""
        if "mcp_config" not in self.session_vars:
            return {"error": "MCP config not initialized. Run init_mcp_config first."}, False
        
        updates = final_args.get("updates", {})
        if not updates:
            return {"error": "Updates dictionary required"}, False
        
        # Apply updates
        self.session_vars["mcp_config"].update(updates)
        
        result = {
            "updated": True,
            "config": self.session_vars["mcp_config"],
            "applied_updates": updates
        }
        return result, True
    
    def _meta_show_mcp_config(self, final_args: dict) -> tuple:
        """Show current MCP generator configuration."""
        if "mcp_config" not in self.session_vars:
            return {"error": "MCP config not initialized. Run init_mcp_config first."}, False
        
        config = self.session_vars["mcp_config"]
        result = {
            "current_config": config,
            "ready_to_generate": self._meta_validate_mcp_config(config)
        }
        return result, True
    
    def _meta_generate_mcp_server(self, final_args: dict) -> tuple:
        """Generate complete MCP server package."""
        if "mcp_config" not in self.session_vars:
            return {"error": "MCP config not initialized. Run init_mcp_config first."}, False
        
        output_dir = final_args.get("output_dir", f"./{self.session_vars['mcp_config']['app_name']}-mcp")
        
        try:
            from .mcp_generator import TreeShellMCPConfig, MCPGenerator
            
            # Create config object
            config = TreeShellMCPConfig(**self.session_vars["mcp_config"])
            
            # Generate MCP server
            generator = MCPGenerator(config)
            generated_files = generator.generate_all(output_dir)
            
            result = {
                "generated": True,
                "output_directory": output_dir,
                "files_created": list(generated_files.keys()),
                "total_files": len(generated_files),
                "server_name": config.server_name,
                "tool_name": config.tool_name,
                "next_steps": [
                    f"cd {output_dir}",
                    "pip install -e .",
                    "Add to your MCP client configuration"
                ]
            }
            return result, True
            
        except Exception as e:
            return {"error": f"Failed to generate MCP server: {str(e)}"}, False
    
    def _meta_validate_mcp_config(self, config: dict) -> bool:
        """Validate MCP configuration is ready for generation."""
        required_fields = ["app_name", "import_path", "factory_function", "description"]
        return all(field in config and config[field] for field in required_fields)
    
    def _meta_get_mcp_example_config(self, final_args: dict) -> tuple:
        """Get example MCP configuration."""
        from .mcp_generator import TreeShellMCPConfig
        
        config_obj = TreeShellMCPConfig(
            app_name="example-app",
            import_path="my_example_app", 
            factory_function="main",
            description="Example TreeShell application"
        )
        
        example = config_obj.generate_example_config()
        
        result = {
            "example_config": example,
            "usage": "Use update_mcp_config with 'updates' parameter to modify current config"
        }
        return result, True
    
    # === OmniTool Operations ===
    
    async def _omni_list_tools(self, final_args: dict) -> tuple:
        """List all available HEAVEN tools through OmniTool."""
        print(f"DEBUG _omni_list_tools: final_args = {final_args}")
        try:
            # Import OmniTool from HEAVEN framework
            from heaven_base.utils.omnitool import omnitool
            
            # Get list of all available tools
            result_str = await omnitool(list_tools=True)
            
            # Parse the result (omnitool returns string representation of dict)
            import ast
            result_dict = ast.literal_eval(result_str)
            
            tools = result_dict.get('available_tools', [])
            
            return {
                "success": True,
                "total_tools": len(tools),
                "available_tools": sorted(tools),
                "usage": "Use get_tool_info to learn about specific tools"
            }, True
            
        except Exception as e:
            import traceback
            return {
                "error": f"Failed to list tools: {str(e)}",
                "exception_type": type(e).__name__,
                "traceback": traceback.format_exc(),
                "note": "Make sure HEAVEN framework is available"
            }, False
    
    async def _omni_get_tool_info(self, final_args: dict) -> tuple:
        """Get detailed information about a specific HEAVEN tool."""
        tool_name = final_args.get("tool_name")
        if not tool_name:
            return {"error": "tool_name parameter required"}, False
        
        try:
            from heaven_base.utils.omnitool import omnitool
            
            # Get tool information
            result_str = await omnitool(tool_name, get_tool_info=True)
            
            return {
                "success": True,
                "tool_name": tool_name,
                "tool_info": result_str
            }, True
            
        except Exception as e:
            return {
                "error": f"Failed to get tool info for '{tool_name}': {str(e)}",
                "available_actions": ["Check tool name spelling", "Use list_tools to see available tools"]
            }, False
    
    async def _omni_execute_tool(self, final_args: dict) -> tuple:
        """Execute a HEAVEN tool with parameters."""
        tool_name = final_args.get("tool_name")
        parameters = final_args.get("parameters", {})
        
        if not tool_name:
            return {"error": "tool_name parameter required"}, False
        
        try:
            from heaven_base.utils.omnitool import omnitool
            
            # Execute the tool with parameters
            result_str = await omnitool(tool_name, parameters=parameters)
            
            return {
                "success": True,
                "tool_name": tool_name,
                "parameters": parameters,
                "result": result_str
            }, True
            
        except Exception as e:
            return {
                "error": f"Failed to execute tool '{tool_name}': {str(e)}",
                "parameters_used": parameters,
                "suggestions": [
                    "Check tool name and parameters",
                    "Use get_tool_info to see correct parameter format"
                ]
            }, False

    def _generate_treeshell_tool(self, final_args: dict) -> tuple:
        """Generate HEAVEN agent tool from TreeShell class."""
        from .tool_generator import _generate_treeshell_tool
        return _generate_treeshell_tool(final_args)

    # === Brain Management Operations ===
    
    def _brain_setup_system_brains(self, final_args: dict) -> tuple:
        """Setup default system brains (local HEAVEN data + TreeShell source)."""
        try:
            import os
            import subprocess
            
            # Get HEAVEN_DATA_DIR from environment
            heaven_data_dir = os.environ.get('HEAVEN_DATA_DIR', '/tmp/heaven_data')
            
            results = []
            
            # 1. Register local HEAVEN data brain (filtered)
            if os.path.exists(heaven_data_dir):
                local_result = self._brain_register_local({
                    "directory_path": heaven_data_dir,
                    "brain_name": "heaven_local_data"
                })
                results.append(("heaven_local_data", local_result[0]))
            else:
                results.append(("heaven_local_data", {"error": f"HEAVEN_DATA_DIR not found: {heaven_data_dir}"}))
            
            # 2. Clone and register TreeShell source
            github_url = "https://github.com/heaven-framework/heaven-tree-repl"
            treeshell_result = self._brain_create_from_github({
                "github_url": github_url,
                "brain_name": "treeshell_source"
            })
            results.append(("treeshell_source", treeshell_result[0]))
            
            return {
                "setup_complete": True,
                "results": results,
                "heaven_data_dir": heaven_data_dir
            }, True
            
        except Exception as e:
            return {"error": f"Failed to setup system brains: {str(e)}"}, False
    
    def _brain_create_from_github(self, final_args: dict) -> tuple:
        """Clone GitHub repository and register as brain."""
        github_url = final_args.get("github_url")
        brain_name = final_args.get("brain_name")
        
        if not github_url or not brain_name:
            return {"error": "Both github_url and brain_name required"}, False
        
        try:
            import os
            import subprocess
            import sys
            
            # Get HEAVEN_DATA_DIR and create brains subdirectory
            heaven_data_dir = os.environ.get('HEAVEN_DATA_DIR', '/tmp/heaven_data')
            brains_dir = os.path.join(heaven_data_dir, 'brains')
            os.makedirs(brains_dir, exist_ok=True)
            
            # Clone repository
            clone_path = os.path.join(brains_dir, brain_name)
            if os.path.exists(clone_path):
                # Update existing clone
                result = subprocess.run(['git', 'pull'], cwd=clone_path, capture_output=True, text=True)
                action = "updated"
            else:
                # Fresh clone
                result = subprocess.run(['git', 'clone', github_url, clone_path], capture_output=True, text=True)
                action = "cloned"
            
            if result.returncode != 0:
                return {"error": f"Git operation failed: {result.stderr}"}, False
            
            # Import brain agent functions
            sys.path.insert(0, '/home/GOD/brain-agent')
            from brain_agent.brain_agent import register_brain
            
            # Register the brain
            register_brain(clone_path, brain_name)
            
            return {
                "success": True,
                "action": action,
                "brain_name": brain_name,
                "github_url": github_url,
                "local_path": clone_path
            }, True
            
        except Exception as e:
            return {"error": f"Failed to create brain from GitHub: {str(e)}"}, False
    
    def _brain_register_local(self, final_args: dict) -> tuple:
        """Register local directory as knowledge brain."""
        directory_path = final_args.get("directory_path")
        brain_name = final_args.get("brain_name")
        
        if not directory_path or not brain_name:
            return {"error": "Both directory_path and brain_name required"}, False
        
        try:
            import sys
            import os
            
            if not os.path.exists(directory_path):
                return {"error": f"Directory does not exist: {directory_path}"}, False
            
            # Import brain agent functions
            sys.path.insert(0, '/home/GOD/brain-agent')
            from brain_agent.brain_agent import register_brain
            
            # Register the brain (with filtering for history.md, history.json, __pycache__, etc.)
            register_brain(directory_path, brain_name)
            
            return {
                "success": True,
                "brain_name": brain_name,
                "directory_path": directory_path,
                "note": "Brain registered with automatic filtering (excludes history.*, __pycache__, .pyc files)"
            }, True
            
        except Exception as e:
            return {"error": f"Failed to register local brain: {str(e)}"}, False
    
    def _brain_list_all(self, final_args: dict) -> tuple:
        """Show all registered knowledge brains."""
        try:
            import sys
            
            # Import registry functions
            sys.path.insert(0, '/home/GOD/brain-agent')
            from heaven_base.tools.registry_tool import registry_util_func
            
            # List all brains from registry
            result = registry_util_func(operation="list", registry_name="brain_configs")
            
            return {
                "success": True,
                "registered_brains": result,
                "usage": "Use brain_agent_query to query any of these brains"
            }, True
            
        except Exception as e:
            return {"error": f"Failed to list brains: {str(e)}"}, False
    
    def _brain_remove(self, final_args: dict) -> tuple:
        """Remove brain from registry."""
        brain_name = final_args.get("brain_name")
        
        if not brain_name:
            return {"error": "brain_name required"}, False
        
        try:
            import sys
            
            # Import registry functions
            sys.path.insert(0, '/home/GOD/brain-agent')
            from heaven_base.tools.registry_tool import registry_util_func
            
            # Remove brain from registry
            result = registry_util_func(
                operation="remove",
                registry_name="brain_configs", 
                key=brain_name
            )
            
            return {
                "success": True,
                "brain_name": brain_name,
                "result": result
            }, True
            
        except Exception as e:
            return {"error": f"Failed to remove brain: {str(e)}"}, False
    
    # === Brain Agent Query Operations ===
    
    async def _brain_agent_fresh_query(self, final_args: dict) -> tuple:
        """Start new query to a knowledge brain."""
        brain_name = final_args.get("brain_name")
        query = final_args.get("query")
        
        if not brain_name or not query:
            return {"error": "Both brain_name and query required"}, False
        
        try:
            import sys
            
            # Import brain agent
            sys.path.insert(0, '/home/GOD/brain-agent')
            from brain_agent.brain_agent import BrainAgent
            
            # Create brain agent instance
            brain_agent = BrainAgent()
            
            # Query the brain
            instructions = await brain_agent.query(f"TargetBrain: {brain_name}\nQuery: {query}")
            
            # Store conversation in session for deepening
            if "brain_conversations" not in self.session_vars:
                self.session_vars["brain_conversations"] = {}
            
            self.session_vars["brain_conversations"][brain_name] = {
                "last_query": query,
                "last_answer": instructions,
                "history": [(query, instructions)]
            }
            
            return {
                "success": True,
                "brain_name": brain_name,
                "query": query,
                "instructions": instructions,
                "note": "Use deepen_query to get more detailed understanding"
            }, True
            
        except Exception as e:
            return {"error": f"Failed to query brain: {str(e)}"}, False
    
    async def _brain_agent_deepen_query(self, final_args: dict) -> tuple:
        """Deepen previous query for more detailed understanding using templated prompt."""
        previous_answer = final_args.get("previous_answer")
        original_query = final_args.get("original_query")
        brain_name = final_args.get("brain_name")
        
        if not previous_answer or not original_query or not brain_name:
            return {"error": "brain_name, previous_answer, and original_query all required"}, False
        
        # Template for deepening query - leverages domain jargon to activate more neurons
        deepening_template = """I know that {previous_answer} explains {original_query}, but I want to understand more deeply from here. 

Based on the terminology and concepts in that previous answer, what additional details, patterns, or advanced aspects should I know? Use the specific vocabulary and jargon from the previous answer to dig deeper into related neurons and knowledge areas."""
        
        # Format the deepening query with the template
        deepening_query = deepening_template.format(
            previous_answer=previous_answer[:300],  # Limit length but include key terms
            original_query=original_query
        )
        
        # Execute zero-shot fresh query with templated deepening prompt
        return await self._brain_agent_fresh_query({
            "brain_name": brain_name,
            "query": deepening_query
        })
    
    async def _brain_agent_continue(self, final_args: dict) -> tuple:
        """Continue brain agent conversation with follow-up."""
        brain_name = final_args.get("brain_name")
        follow_up = final_args.get("follow_up")
        
        if not brain_name or not follow_up:
            return {"error": "Both brain_name and follow_up required"}, False
        
        return await self._brain_agent_fresh_query({
            "brain_name": brain_name,
            "query": follow_up
        })
    
    def _brain_agent_show_history(self, final_args: dict) -> tuple:
        """Display brain agent conversation history."""
        if "brain_conversations" not in self.session_vars:
            return {"no_history": True, "message": "No brain conversations yet"}, True
        
        conversations = self.session_vars["brain_conversations"]
        
        formatted_history = {}
        for brain_name, conv_data in conversations.items():
            formatted_history[brain_name] = {
                "last_query": conv_data["last_query"],
                "total_exchanges": len(conv_data["history"]),
                "history": conv_data["history"]
            }
        
        return {
            "success": True,
            "brain_conversations": formatted_history,
            "total_brains_queried": len(conversations)
        }, True