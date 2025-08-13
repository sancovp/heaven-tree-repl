#!/usr/bin/env python3
"""
Execution Engine module - Core action execution and command processing.
"""
import json
import datetime
import asyncio
import re
from typing import Dict, List, Any, Optional, Tuple


class ExecutionEngineMixin:
    """Mixin class providing execution engine functionality."""
    
    def _call_function_intelligently(self, function, args):
        """Call function using signature inspection to determine calling convention."""
        import inspect
        
        # Handle explicit no-args case first
        if args == "()":
            return function()
        
        try:
            sig = inspect.signature(function)
            params = sig.parameters
            
            # Filter out 'self' parameter for methods
            param_names = [name for name in params.keys() if name != 'self']
            
            if not param_names:
                # Function takes no arguments
                return function()
            elif len(param_names) == 1 and not any(p.kind == p.VAR_KEYWORD for p in params.values()):
                # Function takes exactly one argument
                param_name = param_names[0]
                if isinstance(args, dict) and param_name in args and len(args) == 1:
                    # Dict has exactly the parameter name as key - unpack it
                    return function(args[param_name])
                else:
                    # Otherwise pass dict as single argument
                    return function(args)
            else:
                # Function takes multiple arguments or **kwargs - unpack dict
                if isinstance(args, dict):
                    return function(**args)
                else:
                    return function(args)
        except Exception:
            # Fallback to legacy behavior if signature inspection fails
            if isinstance(args, dict) and args:
                return function(**args)
            else:
                return function(args)
    
    async def _call_function_intelligently_async(self, function, args):
        """Call async function using signature inspection to determine calling convention."""
        import inspect
        
        # Handle explicit no-args case first  
        if args == "()":
            return await function()
        
        try:
            sig = inspect.signature(function)
            params = sig.parameters
            
            # Filter out 'self' parameter for methods
            param_names = [name for name in params.keys() if name != 'self']
            
            if not param_names:
                # Function takes no arguments
                return await function()
            elif len(param_names) == 1 and not any(p.kind == p.VAR_KEYWORD for p in params.values()):
                # Function takes exactly one argument
                param_name = param_names[0]
                if isinstance(args, dict) and param_name in args and len(args) == 1:
                    # Dict has exactly the parameter name as key - unpack it
                    return await function(args[param_name])
                else:
                    # Otherwise pass dict as single argument
                    return await function(args)
            else:
                # Function takes multiple arguments or **kwargs - unpack dict
                if isinstance(args, dict):
                    return await function(**args)
                else:
                    return await function(args)
        except Exception:
            # Fallback to legacy behavior if signature inspection fails
            if isinstance(args, dict) and args:
                return await function(**args)
            else:
                return await function(args)
    
    async def _execute_action(self, node_coord: str, args: dict = None) -> Tuple[dict, bool]:
        """Execute action at given coordinate."""
        if args is None:
            args = {}
            
        # Resolve coordinate using semantic address resolution
        resolved_coord = self._resolve_semantic_address(node_coord)
        
        # Check combo_nodes first (contains all possible address combinations)
        node = None
        if hasattr(self, 'combo_nodes'):
            node = self.combo_nodes.get(resolved_coord)
        
        # Fallback to individual collections if combo_nodes doesn't exist
        if not node:
            node = self.nodes.get(resolved_coord)
        if not node and hasattr(self, 'numeric_nodes'):
            node = self.numeric_nodes.get(resolved_coord)
        if not node and hasattr(self, 'legacy_nodes'):
            node = self.legacy_nodes.get(resolved_coord)
        if not node:
            return {"error": f"Node {resolved_coord} not found"}, False
            
        # Merge args_schema template with user args, then substitute variables
        args_schema = node.get("args_schema", {})
        merged_args = args.copy()
        
        # Add any schema args that aren't provided by user (only $variable tokens)
        for key, value in args_schema.items():
            if isinstance(value, str) and value.startswith("$"):
                merged_args[key] = value
        
        # Substitute variables in merged arguments
        final_args = self._substitute_variables(merged_args)
        
        # Store execution in history
        execution_record = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "node": node_coord,
            "args": final_args,
            "step": self.step_counter
        }
        
        # Execute based on function_name with proper exception handling
        function_name = node.get("function_name")
        result = None
        success = True
        
        try:
            # Check if function needs to be imported on-demand
            async_function = self._get_async_function(function_name)
            sync_function = self._get_sync_function(function_name) if hasattr(self, '_get_sync_function') else None
            
            # If function not found in registries, try to import it
            if not async_function and not sync_function:
                if "import_path" in node and "import_object" in node:
                    result_detail, import_success = self._process_callable_node(node, node_coord)
                    if not import_success:
                        return {"error": f"Failed to import function: {result_detail}"}, False
                    
                    # Re-check registries after import
                    async_function = self._get_async_function(function_name)
                    sync_function = self._get_sync_function(function_name) if hasattr(self, '_get_sync_function') else None
            
            # Check if this is an async function and handle accordingly
            if async_function:
                # Handle explicit no-args case for chains, otherwise use intelligent calling
                if final_args == "()":
                    result = await async_function()
                else:
                    # Use intelligent calling based on actual function signature
                    result = await self._call_function_intelligently_async(async_function, final_args)
            # Check if this is a sync function in the registry  
            elif sync_function:
                # Use intelligent calling for sync functions
                result = self._call_function_intelligently(sync_function, final_args)
            elif function_name == "_test_add":
                result, success = self._test_add(final_args)
            elif function_name == "_test_multiply":
                result, success = self._test_multiply(final_args)
            elif function_name == "_execute_pathway_template":
                result, success = self._execute_pathway_template(final_args, node)
            # Meta Operations
            elif function_name == "_meta_save_var":
                result, success = self._meta_save_var(final_args)
            elif function_name == "_meta_get_var":
                result, success = self._meta_get_var(final_args)
            elif function_name == "_meta_append_to_var":
                result, success = self._meta_append_to_var(final_args)
            elif function_name == "_meta_delete_var":
                result, success = self._meta_delete_var(final_args)
            elif function_name == "_meta_list_vars":
                result, success = self._meta_list_vars(final_args)
            elif function_name == "_meta_save_to_file":
                result, success = self._meta_save_to_file(final_args)
            elif function_name == "_meta_load_from_file":
                result, success = self._meta_load_from_file(final_args)
            elif function_name == "_meta_export_session":
                result, success = self._meta_export_session(final_args)
            elif function_name == "_meta_session_stats":
                result, success = self._meta_session_stats(final_args)
            elif function_name == "_meta_list_shortcuts":
                result, success = self._meta_list_shortcuts(final_args)
            # Tree Structure CRUD Operations
            elif function_name == "_meta_add_node":
                result, success = self._meta_add_node(final_args)
            elif function_name == "_meta_update_node":
                result, success = self._meta_update_node(final_args)
            elif function_name == "_meta_delete_node":
                result, success = self._meta_delete_node(final_args)
            elif function_name == "_meta_list_nodes":
                result, success = self._meta_list_nodes(final_args)
            elif function_name == "_meta_get_node":
                result, success = self._meta_get_node(final_args)
            # MCP Generator Operations
            elif function_name == "_meta_init_mcp_config":
                result, success = self._meta_init_mcp_config(final_args)
            elif function_name == "_meta_show_mcp_config":
                result, success = self._meta_show_mcp_config(final_args)
            elif function_name == "_meta_update_mcp_config":
                result, success = self._meta_update_mcp_config(final_args)
            elif function_name == "_meta_generate_mcp_server":
                result, success = self._meta_generate_mcp_server(final_args)
            elif function_name == "_meta_get_mcp_example_config":
                result, success = self._meta_get_mcp_example_config(final_args)
            # OmniTool Operations (async)
            elif function_name == "_omni_list_tools":
                result, success = await self._omni_list_tools(final_args)
            elif function_name == "_omni_get_tool_info":
                result, success = await self._omni_get_tool_info(final_args)
            elif function_name == "_omni_execute_tool":
                result, success = await self._omni_execute_tool(final_args)
            elif function_name == "_generate_treeshell_tool":
                result, success = self._generate_treeshell_tool(final_args)
            else:
                # Check if function exists as instance attribute
                if function_name and hasattr(self, function_name):
                    func = getattr(self, function_name)
                    if callable(func):
                        # Check if user wants no-args execution with "()" string syntax
                        if final_args == "()":
                            result = func()  # Call with no arguments
                        else:
                            result = func(final_args)  # Call with arguments (dict)
                    else:
                        result = {"error": f"Function {function_name} is not callable"}
                        success = False
                else:
                    # Function not found - return error instead of fake success
                    result = {"error": f"Function {function_name} not found in registries or as instance method"}
                    success = False
                    
        except Exception as e:
            # Capture any unhandled exceptions and return as error result
            import traceback
            error_details = {
                "error": f"Function execution failed: {str(e)}",
                "function_name": function_name,
                "exception_type": type(e).__name__,
                "traceback": traceback.format_exc(),
                "args": final_args
            }
            result = error_details
            success = False
        
        # Handle single return value (assume success unless already set to False)
        if not isinstance(result, tuple):
            # Only assume success if success wasn't already set to False (e.g., by exception handler)
            if success is True:
                success = True
        else:
            result, success = result
        
        # Store result in session
        execution_record["result"] = result
        self.execution_history.append(execution_record)
        
        # Store in session variables for chain access
        step_result_key = f"step{self.step_counter}_result"
        self.session_vars[step_result_key] = result
        self.session_vars["last_result"] = result
        
        # Store individual args for reference (only if final_args is a dict)
        if isinstance(final_args, dict):
            for arg_key, arg_value in final_args.items():
                self.session_vars[f"step{self.step_counter}_{arg_key}"] = arg_value
            
        self.step_counter += 1
        
        return {"result": result, "execution": execution_record}, success
    
    def _test_add(self, final_args: dict) -> tuple:
        """Test addition function."""
        try:
            a = int(final_args.get('a', 0))
            b = int(final_args.get('b', 0))
            result = a + b
            return result, True
        except (ValueError, TypeError):
            return {"error": "Invalid arguments for add"}, False
    
    def _test_multiply(self, final_args: dict) -> tuple:
        """Test multiplication function."""
        try:
            a = int(final_args.get('a', 0))
            b = int(final_args.get('b', 0))
            result = a * b
            return result, True
        except (ValueError, TypeError):
            return {"error": "Invalid arguments for multiply"}, False
    
    async def handle_command(self, command: str) -> dict:
        """Main command handler - process any input."""
        command = command.strip()
        if not command:
            menu = self._get_node_menu(self.current_position)
            return self._build_response(menu)
            
        # Record pathway if active
        if self.recording_pathway:
            self.pathway_steps.append({
                "command": command,
                "position": self.current_position,
                "timestamp": datetime.datetime.utcnow().isoformat()
            })
        
        # Parse command - handle both "3" and "3, args={...}" formats
        if "args=" in command:
            # Handle "3, args={...}" format
            parts = command.split("args=", 1)
            cmd_part = parts[0].strip().rstrip(",").strip()
            args_str = parts[1].strip()
            
            if cmd_part.isdigit():
                return await self._handle_numerical_selection(int(cmd_part), args_str)
            else:
                return {"error": f"Invalid command format: {command}"}
        
        # Handle regular commands
        parts = command.split(None, 1)
        cmd = parts[0].lower()
        args_str = parts[1] if len(parts) > 1 else ""
        
        # Handle numerical menu selection
        if cmd.isdigit():
            return await self._handle_numerical_selection(int(cmd), args_str)
        
        # Handle .exec() notation: coordinate.exec or coordinate.exec()
        if ".exec" in cmd:
            if cmd.endswith(".exec()"):
                # coordinate.exec() format
                coord_part = cmd[:-7]  # Remove ".exec()"
                exec_args = "{}"  # Empty args for exec()
            elif cmd.endswith(".exec"):
                # coordinate.exec format 
                coord_part = cmd[:-5]  # Remove ".exec"
                exec_args = args_str if args_str else "{}"
            else:
                return {"error": f"Invalid .exec format: {command}"}
            
            # Jump to coordinate then execute (like option 1)
            jump_result = await self._handle_jump(coord_part)
            if "error" in jump_result:
                return jump_result
            
            # Execute at the new position
            return await self._handle_numerical_selection(1, exec_args)
            
        # Handle universal commands
        if cmd == "jump":
            return await self._handle_jump(args_str)
        elif cmd == "chain":
            return await self._handle_chain(args_str)
        elif cmd == "build_pathway":
            return self._handle_build_pathway()
        elif cmd == "save_emergent_pathway":
            return self._handle_save_pathway(args_str)
        elif cmd == "save_emergent_pathway_from_history":
            return self._handle_save_pathway_from_history(args_str)
        elif cmd == "follow_established_pathway":
            return self._handle_follow_pathway(args_str)
        elif cmd == "show_execution_history":
            return self._handle_show_history()
        elif cmd == "analyze_patterns":
            return self._handle_analyze_patterns()
        elif cmd == "crystallize_pattern":
            return self._handle_crystallize_pattern(args_str)
        elif cmd == "rsi_insights":
            return self._handle_rsi_insights()
        elif cmd == "back":
            return self._handle_back()
        elif cmd == "menu":
            return self._handle_menu()
        elif cmd == "nav":
            return self._handle_nav()
        elif cmd == "shortcut":
            return self._handle_shortcut(args_str)
        elif cmd == "shortcuts":
            return self._handle_list_shortcuts()
        elif cmd == "exit":
            return self._handle_exit()
        elif cmd == "set":
            return self._handle_set(args_str)
        else:
            # Check if this is a shortcut command
            shortcuts = self.session_vars.get("_shortcuts", {})
            if cmd in shortcuts:
                shortcut = shortcuts[cmd]
                
                if isinstance(shortcut, str):
                    # Legacy format - simple coordinate
                    return await self._handle_jump(shortcut + (" " + args_str if args_str else ""))
                elif isinstance(shortcut, dict):
                    shortcut_type = shortcut.get("type", "jump")
                    
                    if shortcut_type == "jump":
                        # Simple jump shortcut
                        coordinate = shortcut["coordinate"]
                        return await self._handle_jump(coordinate + (" " + args_str if args_str else ""))
                    
                    elif shortcut_type == "chain":
                        # Chain template shortcut
                        template = shortcut["template"]
                        analysis = shortcut.get("analysis", {})
                        
                        # If template needs args but none provided, show error
                        if analysis.get("entry_args") and not args_str:
                            required_args = ", ".join(analysis["entry_args"])
                            return {"error": f"Chain shortcut '{cmd}' requires arguments: {required_args}"}
                        
                        # Execute chain with template substitution
                        if args_str:
                            # Parse args and substitute into template
                            try:
                                args_dict = json.loads(args_str)
                                # Substitute variables in template
                                substituted_template = self._substitute_template_vars(template, args_dict)
                                return await self._handle_chain(substituted_template)
                            except json.JSONDecodeError:
                                return {"error": "Invalid JSON arguments for chain shortcut"}
                        else:
                            # Execute unconstrained template
                            return await self._handle_chain(template)
            
            # Check if this looks like a coordinate pattern (helpful suggestion)
            import re
            if re.match(r'^[0-9]+(\.[0-9]+)*$', cmd):
                return {"error": f"Sounds like you might want to go somewhere else. Did you mean `jump {cmd}`?"}
                            
            return {"error": f"Unknown command: {cmd}"}
    
    def _substitute_template_vars(self, template: str, args_dict: dict) -> str:
        """Substitute variables in chain template with provided arguments."""
        substituted = template
        for var_name, value in args_dict.items():
            # Replace $var_name with the actual value
            pattern = f"\\${var_name}\\b"
            # The template already has quotes around the variable, just replace with the raw value
            if isinstance(value, str):
                replacement = value  # Don't add extra quotes - template already has them
            else:
                replacement = str(value)
            substituted = re.sub(pattern, replacement, substituted)
        return substituted