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
    
    def _meta_add_node(self, final_args: dict) -> tuple:
        """Add a new node to the tree structure with multiple callable options."""
        coordinate = final_args.get("coordinate")
        node_data = final_args.get("node_data")
        
        if not coordinate:
            return {"error": "Node coordinate required"}, False
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
            
        # Handle Callable nodes with three different approaches
        if node_data["type"] == "Callable":
            function_name = node_data.get("function_name")
            is_async = node_data.get("is_async")
            
            if not function_name:
                return {"error": "Callable nodes require 'function_name' field"}, False
            if is_async is None:
                return {"error": "Callable nodes require 'is_async' field (true/false)"}, False
            
            # Approach 1: Import from existing module
            if "import_path" in node_data and "import_object" in node_data:
                import_path = node_data["import_path"]
                import_object = node_data["import_object"]
                
                try:
                    # Dynamic import: from import_path import import_object
                    module = __import__(import_path, fromlist=[import_object])
                    imported_func = getattr(module, import_object)
                    
                    # Register the imported function based on async flag
                    if is_async:
                        self.register_async_function(function_name, imported_func)
                    else:
                        setattr(self, function_name, imported_func)
                    
                    result_detail = f"imported {import_object} from {import_path} ({'async' if is_async else 'sync'})"
                    
                except ImportError as e:
                    return {"error": f"Failed to import {import_object} from {import_path}: {str(e)}"}, False
                except AttributeError as e:
                    return {"error": f"Object {import_object} not found in {import_path}: {str(e)}"}, False
                except Exception as e:
                    return {"error": f"Import failed: {str(e)}"}, False
            
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
                            setattr(self, function_name, exec_globals[function_name])
                        result_detail = f"compiled function code ({'async' if is_async else 'sync'})"
                    else:
                        return {"error": f"Function {function_name} not found in provided code"}, False
                        
                except Exception as e:
                    return {"error": f"Failed to compile function code: {str(e)}"}, False
            
            # Approach 3: Function name only (assumes function already exists)
            else:
                # Check if function already exists
                if is_async:
                    if function_name not in self.async_functions:
                        return {"error": f"Async function {function_name} not found in async registry. Provide 'import_path'+'import_object' or 'function_code'"}, False
                else:
                    if not hasattr(self, function_name):
                        return {"error": f"Function {function_name} not found. Provide either 'import_path'+'import_object' or 'function_code'"}, False
                
                result_detail = f"using existing function ({'async' if is_async else 'sync'})"
        else:
            result_detail = "static node"
        
        # Add the node
        self.nodes[coordinate] = node_data.copy()
        
        result = {
            "added": True,
            "coordinate": coordinate,
            "node_type": node_data["type"],
            "prompt": node_data["prompt"],
            "implementation": result_detail
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
            return {
                "error": f"Failed to list tools: {str(e)}",
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