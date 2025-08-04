#!/usr/bin/env python3
"""
Execution Engine module - Core action execution and command processing.
"""
import json
import datetime
import asyncio
from typing import Dict, List, Any, Optional, Tuple


class ExecutionEngineMixin:
    """Mixin class providing execution engine functionality."""
    
    def _execute_action(self, node_coord: str, args: dict = None) -> Tuple[dict, bool]:
        """Execute action at given coordinate."""
        if args is None:
            args = {}
            
        node = self.nodes.get(node_coord)
        if not node:
            return {"error": f"Node {node_coord} not found"}, False
            
        # Substitute variables in arguments
        final_args = self._substitute_variables(args)
        
        # Store execution in history
        execution_record = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "node": node_coord,
            "args": final_args,
            "step": self.step_counter
        }
        
        # Execute based on function_name
        function_name = node.get("function_name")
        result = None
        
        # Check if this is an async function and handle accordingly
        async_function = self._get_async_function(function_name)
        if async_function:
            result = asyncio.run(async_function(final_args))
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
        else:
            # Generic execution - store args as result for now
            result = f"Executed {function_name or 'action'} with {final_args}"
            success = True
        
        # Handle single return value (assume success)
        if not isinstance(result, tuple):
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
        
        # Store individual args for reference
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
    
    def handle_command(self, command: str) -> dict:
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
                return self._handle_numerical_selection(int(cmd_part), args_str)
            else:
                return {"error": f"Invalid command format: {command}"}
        
        # Handle regular commands
        parts = command.split(None, 1)
        cmd = parts[0].lower()
        args_str = parts[1] if len(parts) > 1 else ""
        
        # Handle numerical menu selection
        if cmd.isdigit():
            return self._handle_numerical_selection(int(cmd), args_str)
            
        # Handle universal commands
        if cmd == "jump":
            return self._handle_jump(args_str)
        elif cmd == "chain":
            return self._handle_chain(args_str)
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
        elif cmd == "exit":
            return self._handle_exit()
        else:
            return {"error": f"Unknown command: {cmd}"}