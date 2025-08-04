#!/usr/bin/env python3
"""
Pathway Management module - Recording, saving, and template analysis.
"""
import json
import datetime
from typing import Dict, List, Any, Optional, Tuple


class PathwayManagementMixin:
    """Mixin class providing pathway management functionality."""
    
    def _analyze_pathway_template(self, steps: list) -> dict:
        """Analyze pathway steps to create executable template."""
        template = {
            "steps": steps,
            "created": datetime.datetime.utcnow().isoformat(),
            "type": "unconstrained",  # Default assumption
            "entry_args": set(),
            "trace_flow": {},
            "step_templates": []
        }
        
        has_variable_refs = False
        
        # Analyze each step for arguments and variable references
        for i, step in enumerate(steps):
            step_template = {
                "step_num": i + 1,
                "command": step.get("command", ""),
                "node": None,
                "args_template": {},
                "has_variables": False
            }
            
            # Parse command to extract node and args
            cmd_parts = step.get("command", "").split(None, 1)
            if len(cmd_parts) >= 2:
                cmd_type = cmd_parts[0]
                if cmd_type == "jump":
                    # Extract node and args from jump command
                    node_and_args = cmd_parts[1]
                    args_start = node_and_args.find("{")
                    if args_start != -1:
                        node_part = node_and_args[:args_start].strip()
                        args_str = node_and_args[args_start:]
                        step_template["node"] = node_part
                        
                        try:
                            args = json.loads(args_str)
                            
                            # Analyze each argument
                            for arg_key, arg_value in args.items():
                                if isinstance(arg_value, str) and arg_value.startswith("$"):
                                    # This is a variable reference
                                    has_variable_refs = True
                                    step_template["has_variables"] = True
                                    step_template["args_template"][arg_key] = arg_value
                                else:
                                    # This is a literal value that should be parameterized
                                    # Create a unique parameter name for this step
                                    param_name = f"step{i+1}_{arg_key}"
                                    template["entry_args"].add(param_name)
                                    step_template["args_template"][arg_key] = f"${param_name}"
                                    
                        except json.JSONDecodeError:
                            pass
            
            template["step_templates"].append(step_template)
        
        # Determine template type
        if has_variable_refs:
            template["type"] = "constrained"
        else:
            template["type"] = "unconstrained"
            
        template["entry_args"] = list(template["entry_args"])
        
        return template
    
    def _get_domain_root(self, position: str) -> str:
        """Extract domain root from position (e.g., 0.1.2.3 -> 0.1)."""
        parts = position.split(".")
        if len(parts) >= 2:
            return ".".join(parts[:2])  # 0.1, 0.2, etc.
        return "0"  # Root domain
    
    def _get_next_coordinate_in_domain(self, domain: str) -> str:
        """Get next available coordinate in domain."""
        if domain not in self.graph_ontology["next_coordinates"]:
            # Find existing coordinates in domain
            existing_coords = []
            for coord in self.nodes.keys():
                if coord.startswith(domain + ".") and coord.count(".") == domain.count(".") + 1:
                    try:
                        coord_num = int(coord.split(".")[-1])
                        existing_coords.append(coord_num)
                    except ValueError:
                        pass
            
            # Start from max + 1, or 1 if none exist
            next_num = max(existing_coords) + 1 if existing_coords else 1
            self.graph_ontology["next_coordinates"][domain] = next_num
        
        coord = f"{domain}.{self.graph_ontology['next_coordinates'][domain]}"
        self.graph_ontology["next_coordinates"][domain] += 1
        return coord
    
    def _add_pathway_to_ontology(self, pathway_name: str, template: dict, coordinate: str, domain: str, description: str = "", tags: list = None) -> None:
        """Add pathway to the graph ontology."""
        if tags is None:
            tags = []
            
        # Initialize domain if not exists
        if domain not in self.graph_ontology["domains"]:
            domain_node = self.nodes.get(domain, {})
            self.graph_ontology["domains"][domain] = {
                "name": domain_node.get("prompt", f"Domain {domain}"),
                "description": domain_node.get("description", ""),
                "pathways": {}
            }
        
        # Add pathway to domain
        self.graph_ontology["domains"][domain]["pathways"][pathway_name] = {
            "type": template["type"],
            "description": description,
            "coordinate": coordinate,
            "tags": tags,
            "entry_args": template["entry_args"],
            "created": template["created"]
        }
        
        # Add to pathway index
        self.graph_ontology["pathway_index"][pathway_name] = coordinate
        
        # Add to tag index
        for tag in tags:
            if tag not in self.graph_ontology["tags"]:
                self.graph_ontology["tags"][tag] = []
            if pathway_name not in self.graph_ontology["tags"][tag]:
                self.graph_ontology["tags"][tag].append(pathway_name)
    
    def _create_pathway_node(self, coordinate: str, pathway_name: str, template: dict) -> None:
        """Create a new node in the tree for the pathway."""
        self.nodes[coordinate] = {
            "type": "Callable",
            "prompt": f"Execute {pathway_name}",
            "description": f"Pathway template: {pathway_name} ({template['type']} type)",
            "signature": f"{pathway_name}({', '.join(template['entry_args'])}) -> result",
            "function_name": "_execute_pathway_template",
            "pathway_name": pathway_name,
            "template": template,
            "args_schema": {arg: "any" for arg in template["entry_args"]}
        }
    
    def _update_domain_menu(self, domain: str, pathway_name: str, coordinate: str) -> None:
        """Add pathway as option to domain menu."""
        domain_node = self.nodes.get(domain)
        if domain_node and domain_node.get("type") == "Menu":
            # Find next option number
            existing_options = domain_node.get("options", {})
            next_option = len(existing_options) + 1
            
            # Add pathway as menu option
            domain_node["options"][str(next_option)] = coordinate
    
    def _execute_pathway_template(self, final_args: dict, node: dict) -> tuple:
        """Execute saved pathway template."""
        pathway_name = node.get("pathway_name")
        template = node.get("template")
        
        if not pathway_name or not template:
            return {"error": "Invalid pathway template node"}, False
            
        # Execute template using existing logic
        template_session_vars = {}
        pathway_results = []
        
        for step_template in template["step_templates"]:
            step_num = step_template["step_num"]
            step_node = step_template["node"]
            args_template = step_template["args_template"]
            
            if not step_node:
                continue
            
            # Substitute arguments
            substituted_args = {}
            for arg_key, arg_template in args_template.items():
                if arg_template.startswith("$"):
                    var_name = arg_template[1:]
                    if var_name in template_session_vars:
                        substituted_args[arg_key] = template_session_vars[var_name]
                    elif var_name in final_args:
                        substituted_args[arg_key] = final_args[var_name]
                    else:
                        return {"error": f"Template variable ${var_name} not found"}, False
                else:
                    substituted_args[arg_key] = arg_template
            
            # Execute step
            step_result, step_success = self._execute_action(step_node, substituted_args)
            if not step_success:
                return {"error": f"Pathway step {step_num} failed: {step_result}"}, False
            
            # Store result for next steps
            template_session_vars[f"step{step_num}_result"] = step_result.get("result")
            template_session_vars["last_result"] = step_result.get("result")
            
            pathway_results.append({
                "step": step_num,
                "node": step_node,
                "args": substituted_args,
                "result": step_result.get("result")
            })
        
        result = {
            "pathway_executed": pathway_name,
            "steps": pathway_results,
            "final_result": pathway_results[-1]["result"] if pathway_results else None
        }
        
        return result, True
    
    def _execute_pathway_by_name(self, pathway_name: str, args_json: str) -> dict:
        """Execute pathway by name with arguments."""
        coordinate = self.graph_ontology["pathway_index"].get(pathway_name)
        if not coordinate:
            return {"error": f"Pathway '{pathway_name}' not found in ontology"}
        
        try:
            args = json.loads(args_json)
            result, success = self._execute_action(coordinate, args)
            if success:
                return self._build_response({
                    "action": "execute_pathway_by_name",
                    "pathway_name": pathway_name,
                    "coordinate": coordinate,
                    "result": result,
                    "success": True
                })
            else:
                return {"error": f"Pathway execution failed: {result}"}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON arguments"}
    
    def _show_pathway_info(self, pathway_name: str) -> dict:
        """Show detailed info about a pathway."""
        coordinate = self.graph_ontology["pathway_index"].get(pathway_name)
        if not coordinate:
            return {"error": f"Pathway '{pathway_name}' not found"}
        
        # Find pathway in domains
        pathway_info = None
        domain = None
        for dom, domain_data in self.graph_ontology["domains"].items():
            if pathway_name in domain_data["pathways"]:
                pathway_info = domain_data["pathways"][pathway_name]
                domain = dom
                break
        
        if not pathway_info:
            return {"error": f"Pathway info for '{pathway_name}' not found"}
        
        template = self.saved_templates.get(pathway_name, {})
        
        return self._build_response({
            "action": "show_pathway_info",
            "pathway_name": pathway_name,
            "coordinate": coordinate,
            "domain": domain,
            "info": pathway_info,
            "template_details": {
                "type": template.get("type"),
                "entry_args": template.get("entry_args", []),
                "step_count": len(template.get("step_templates", []))
            },
            "usage": f"jump {coordinate} {{args}} or follow_established_pathway {pathway_name} {{args}}"
        })