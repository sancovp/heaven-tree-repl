#!/usr/bin/env python3
"""
Command Handlers module - Navigation and interaction commands.
"""
import json
import datetime
from typing import Dict, List, Any, Optional, Tuple


class CommandHandlersMixin:
    """Mixin class providing command handling functionality."""
    
    async def _handle_numerical_selection(self, option: int, args_str: str) -> dict:
        """Handle numerical menu selection."""
        current_node = self._get_current_node()
        
        if option == 0:
            # Introspection
            return self._build_response({
                "action": "introspect",
                "description": current_node.get("description", "No description"),
                "signature": current_node.get("signature", "No signature"),
                "node_type": current_node.get("type"),
                "available_options": list(current_node.get("options", {}).keys())
            })
            
        elif option == 1:
            # Execute current node
            try:
                args = json.loads(args_str) if args_str else {}
            except json.JSONDecodeError:
                return {"error": "Invalid JSON arguments"}
                
            result, success = await self._execute_action(self.current_position, args)
            if success:
                return self._build_response({
                    "action": "execute",
                    **result,
                    "menu": self._get_node_menu(self.current_position)
                })
            else:
                return self._build_response({
                    "action": "execute",
                    **result
                })
                
        else:
            # Navigate to option or execute with args
            options = current_node.get("options", {})
            option_keys = list(options.keys())
            
            if option - 2 < len(option_keys):
                target_key = option_keys[option - 2]
                target_coord = options[target_key]
                
                # If args provided, execute at target
                if args_str:
                    try:
                        args = json.loads(args_str)
                        result, success = self._execute_action(target_coord, args)
                        if success:
                            return self._build_response({
                                "action": "execute_at_target",
                                "target": target_coord,
                                **result
                            })
                        else:
                            return self._build_response(result)
                    except json.JSONDecodeError:
                        return {"error": "Invalid JSON arguments"}
                else:
                    # Navigate to target
                    self.current_position = target_coord
                    self.stack.append(target_coord)
                    
                    return self._build_response({
                        "action": "navigate",
                        "target": target_coord,
                        "menu": self._get_node_menu(target_coord)
                    })
            else:
                return {"error": f"Invalid option: {option}"}
    
    def _handle_jump(self, args_str: str) -> dict:
        """Handle jump command."""
        parts = args_str.split(None, 1)
        if not parts:
            return {"error": "jump requires target coordinate"}
            
        target_coord = parts[0]
        args_str = parts[1] if len(parts) > 1 else ""
        
        if target_coord not in self.nodes:
            return {"error": f"Target coordinate {target_coord} not found"}
            
        # Jump to target
        self.current_position = target_coord
        self.stack.append(target_coord)
        
        # If args provided, execute immediately
        if args_str:
            try:
                args = json.loads(args_str)
                result, success = self._execute_action(target_coord, args)
                if success:
                    return self._build_response({
                        "action": "jump_execute", 
                        "target": target_coord,
                        **result,
                        "menu": self._get_node_menu(target_coord)
                    })
                else:
                    return self._build_response(result)
            except json.JSONDecodeError:
                return {"error": "Invalid JSON arguments"}
        else:
            return self._build_response({
                "action": "jump",
                "target": target_coord,
                "menu": self._get_node_menu(target_coord)
            })
    
    def _handle_chain(self, args_str: str) -> dict:
        """Handle chain command - sequential execution."""
        if not args_str:
            return {"error": "chain requires sequence specification"}
            
        # Parse chain sequence: node1 args1 -> node2 args2 -> node3 args3
        steps = args_str.split(" -> ")
        chain_results = []
        
        for i, step in enumerate(steps):
            step = step.strip()
            parts = step.split(None, 1)
            target_coord = parts[0]
            step_args_str = parts[1] if len(parts) > 1 else "{}"
            
            try:
                step_args = json.loads(step_args_str)
            except json.JSONDecodeError:
                return {"error": f"Invalid JSON in step {i+1}: {step_args_str}"}
                
            if target_coord not in self.nodes:
                return {"error": f"Target coordinate {target_coord} not found in step {i+1}"}
                
            # Execute step
            result, success = self._execute_action(target_coord, step_args)
            if not success:
                return {"error": f"Step {i+1} failed: {result}"}
                
            chain_results.append({
                "step": i+1,
                "target": target_coord,
                "args": step_args,
                "result": result
            })
            
            # Store chain step results for next steps
            self.chain_results[f"step{i+1}_result"] = result.get("result")
        
        # End at final step position
        final_target = steps[-1].split()[0]
        self.current_position = final_target
        self.stack.append(final_target)
        
        return self._build_response({
            "action": "chain",
            "steps_executed": len(steps),
            "chain_results": chain_results,
            "final_position": final_target,
            "menu": self._get_node_menu(final_target)
        })
    
    def _handle_build_pathway(self) -> dict:
        """Start recording pathway."""
        self.recording_pathway = True
        self.recording_start_position = self.current_position
        self.pathway_steps = []
        return self._build_response({
            "action": "build_pathway_start",
            "starting_position": self.recording_start_position,
            "message": "Pathway recording started"
        })
    
    def _handle_save_pathway(self, name: str) -> dict:
        """Save recorded pathway as template and create coordinate."""
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
            "coordinate": coordinate
        }
        
        self.saved_templates[name] = template
        
        # Create coordinate node
        self._create_pathway_node(coordinate, name, template)
        
        # Add to ontology
        self._add_pathway_to_ontology(name, template, coordinate, domain)
        
        # Update domain menu
        self._update_domain_menu(domain, name, coordinate)
        
        self.recording_pathway = False
        self.recording_start_position = None
        self.pathway_steps = []
        
        return self._build_response({
            "action": "save_pathway_template",
            "pathway_name": name,
            "template_type": template["type"],
            "entry_args": template["entry_args"],
            "coordinate": coordinate,
            "domain": domain,
            "steps_saved": len(self.saved_pathways[name]["steps"]),
            "message": f"Pathway template '{name}' saved as {coordinate} ({template['type']} type)"
        })
    
    def _handle_save_pathway_from_history(self, args_str: str) -> dict:
        """Save pathway template from execution history."""
        parts = args_str.split(None, 1)
        if not parts:
            return {"error": "Pathway name required"}
            
        name = parts[0]
        step_ids_str = parts[1] if len(parts) > 1 else ""
        
        # Parse step IDs
        if step_ids_str:
            try:
                # Handle ranges like [0,1,2] or [0-5] or just "0,1,2"
                step_ids_str = step_ids_str.strip("[]")
                if "-" in step_ids_str and "," not in step_ids_str:
                    # Range format: "0-5"
                    start, end = map(int, step_ids_str.split("-"))
                    step_ids = list(range(start, end + 1))
                else:
                    # List format: "0,1,2"
                    step_ids = [int(x.strip()) for x in step_ids_str.split(",")]
            except ValueError:
                return {"error": "Invalid step IDs format. Use: [0,1,2] or [0-5] or 0,1,2"}
        else:
            # Use all history if no specific steps given
            step_ids = list(range(len(self.execution_history)))
        
        # Validate step IDs
        if not all(0 <= sid < len(self.execution_history) for sid in step_ids):
            return {"error": f"Invalid step IDs. History has {len(self.execution_history)} steps (0-{len(self.execution_history)-1})"}
        
        # Create pathway steps from history
        pathway_steps = []
        for sid in step_ids:
            execution = self.execution_history[sid]
            # Reconstruct command from execution record
            node = execution["node"]
            args = execution["args"]
            command = f"jump {node} {json.dumps(args)}"
            
            pathway_steps.append({
                "command": command,
                "position": node,
                "timestamp": execution["timestamp"],
                "from_history": True,
                "history_step": sid
            })
        
        # Create template
        template = self._analyze_pathway_template(pathway_steps)
        
        self.saved_pathways[name] = {
            "steps": pathway_steps,
            "created": datetime.datetime.utcnow().isoformat(),
            "from_history": step_ids,
            "source": "execution_history"
        }
        
        self.saved_templates[name] = template
        
        return self._build_response({
            "action": "save_pathway_from_history",
            "pathway_name": name,
            "template_type": template["type"],
            "entry_args": template["entry_args"],
            "history_steps_used": step_ids,
            "steps_saved": len(pathway_steps),
            "message": f"Pathway template '{name}' created from history ({template['type']} type)"
        })
    
    def _handle_show_history(self) -> dict:
        """Show execution history."""
        history_display = []
        for i, execution in enumerate(self.execution_history):
            history_display.append({
                "step_id": i,
                "timestamp": execution["timestamp"],
                "node": execution["node"],
                "args": execution["args"],
                "result": execution["result"],
                "command": f"jump {execution['node']} {json.dumps(execution['args'])}"
            })
        
        return self._build_response({
            "action": "show_execution_history",
            "total_steps": len(self.execution_history),
            "history": history_display,
            "message": f"Showing {len(self.execution_history)} execution steps"
        })
    
    def _handle_follow_pathway(self, args_str: str) -> dict:
        """Follow established pathway template with arguments or query ontology."""
        if not args_str:
            # Show ontology overview
            ontology_summary = {
                "domains": {},
                "total_pathways": len(self.graph_ontology["pathway_index"]),
                "available_tags": list(self.graph_ontology["tags"].keys())
            }
            
            for domain, domain_data in self.graph_ontology["domains"].items():
                ontology_summary["domains"][domain] = {
                    "name": domain_data["name"],
                    "pathway_count": len(domain_data["pathways"]),
                    "pathways": list(domain_data["pathways"].keys())
                }
            
            return self._build_response({
                "action": "show_ontology",
                "ontology": ontology_summary,
                "message": "Graph ontology (use: follow_established_pathway <query> or <name> <args>)"
            })
        
        # Parse query or pathway execution
        if "=" in args_str:
            # Ontology query (e.g., domain=math, tags=arithmetic)
            return self._handle_ontology_query(args_str)
        elif args_str.startswith("{") or " {" in args_str:
            # Direct pathway execution with args
            parts = args_str.split(None, 1)
            pathway_name = parts[0]
            args_json = parts[1] if len(parts) > 1 else "{}"
            return self._execute_pathway_by_name(pathway_name, args_json)
        else:
            # Show specific pathway info
            pathway_name = args_str.strip()
            return self._show_pathway_info(pathway_name)
    
    def _handle_ontology_query(self, query_str: str) -> dict:
        """Handle ontology queries like domain=math, tags=arithmetic."""
        results = []
        
        # Parse query parameters
        params = {}
        for param in query_str.split(","):
            if "=" in param:
                key, value = param.split("=", 1)
                params[key.strip()] = value.strip()
        
        # Query by domain
        if "domain" in params:
            domain_query = params["domain"]
            for domain, domain_data in self.graph_ontology["domains"].items():
                if domain_query in domain or domain_query in domain_data["name"].lower():
                    for pathway_name, pathway_info in domain_data["pathways"].items():
                        results.append({
                            "name": pathway_name,
                            "coordinate": pathway_info["coordinate"],
                            "domain": domain,
                            "type": pathway_info["type"],
                            "entry_args": pathway_info["entry_args"]
                        })
        
        # Query by tags
        if "tags" in params:
            tag_query = params["tags"]
            for tag in tag_query.split("|"):  # Support OR with |
                tag = tag.strip()
                if tag in self.graph_ontology["tags"]:
                    for pathway_name in self.graph_ontology["tags"][tag]:
                        coordinate = self.graph_ontology["pathway_index"].get(pathway_name)
                        if coordinate and not any(r["name"] == pathway_name for r in results):
                            # Find domain info
                            domain_info = None
                            for domain, domain_data in self.graph_ontology["domains"].items():
                                if pathway_name in domain_data["pathways"]:
                                    domain_info = domain_data["pathways"][pathway_name]
                                    break
                            
                            if domain_info:
                                results.append({
                                    "name": pathway_name,
                                    "coordinate": coordinate,
                                    "type": domain_info["type"],
                                    "entry_args": domain_info["entry_args"],
                                    "tags": domain_info["tags"]
                                })
        
        return self._build_response({
            "action": "ontology_query",
            "query": params,
            "results": results,
            "count": len(results),
            "message": f"Found {len(results)} pathways matching query"
        })
    
    def _handle_back(self) -> dict:
        """Go back one level."""
        if len(self.stack) > 1:
            self.stack.pop()
            self.current_position = self.stack[-1]
        
        return self._build_response({
            "action": "back",
            "menu": self._get_node_menu(self.current_position)
        })
    
    def _handle_menu(self) -> dict:
        """Go to nearest menu node (find closest 0 node)."""
        # Find nearest 0 node at current depth
        current_parts = self.current_position.split(".")
        
        for i in range(len(current_parts) - 1, -1, -1):
            menu_coord = ".".join(current_parts[:i+1]) + ".0" if i > 0 else "0"
            if menu_coord in self.nodes:
                self.current_position = menu_coord
                self.stack.append(menu_coord)
                break
        else:
            # Fallback to root
            self.current_position = "0"
            self.stack = ["0"]
        
        return self._build_response({
            "action": "menu",
            "menu": self._get_node_menu(self.current_position)
        })
    
    def _handle_exit(self) -> dict:
        """Exit the shell."""
        return {
            "action": "exit",
            "message": "Exiting tree shell",
            "session_summary": {
                "total_executions": len(self.execution_history),
                "final_position": self.current_position,
                "saved_pathways": list(self.saved_pathways.keys()),
                "session_vars": list(self.session_vars.keys())
            }
        }