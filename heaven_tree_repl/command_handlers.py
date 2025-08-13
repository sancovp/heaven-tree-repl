#!/usr/bin/env python3
"""
Command Handlers module - Navigation and interaction commands.
"""
import json
import datetime
from typing import Dict, List, Any, Optional, Tuple


class CommandHandlersMixin:
    """Mixin class providing command handling functionality."""
    
    def _resolve_semantic_address(self, target_coord: str) -> str:
        """Auto-resolve family.node.subnode addresses to coordinates.
        
        Resolution Priority:
        1. Node name resolution: equipment_selection → search all families for matching node name
        2. Partial path resolution: equipment.tools → resolve within families
        3. Full family resolution: agent_management.equipment.tools → 0.1.equipment.tools
        4. System family resolution: system.workflows → 0.0.workflows
        5. Legacy coordinates: 0.1.2 (exact numeric matches)
        6. Manual shortcuts: brain → existing shortcut system
        """
        original_target = target_coord
        
        
        # Check existing shortcuts first
        shortcuts = self.session_vars.get("_shortcuts", {})
        if target_coord in shortcuts:
            shortcut = shortcuts[target_coord]
            if isinstance(shortcut, dict) and shortcut.get("type") == "jump":
                return shortcut.get("coordinate", target_coord)
            elif isinstance(shortcut, str):
                return shortcut  # Legacy shortcut format
        
        # Resolution 1: Node name resolution (search all nodes for exact match)
        if "." not in target_coord:
            for coord, node in self.nodes.items():
                node_id = node.get("id", "")
                if node_id and node_id.endswith(f".{target_coord}"):
                    # print(f"Debug: Resolved node name '{target_coord}' to coordinate '{coord}'")
                    return coord
                # Also check if the coordinate itself ends with the target
                if coord.split(".")[-1] == target_coord:
                    # print(f"Debug: Resolved node name '{target_coord}' to coordinate '{coord}'")
                    return coord
        
        # Resolution 2 & 3: Family path resolution
        if "." in target_coord:
            parts = target_coord.split(".")
            family_name = parts[0]
            
            # Check if first part is a known family
            if hasattr(self, 'family_mappings') and family_name in self.family_mappings:
                nav_coord = self.family_mappings[family_name]
                if len(parts) == 1:
                    # Just family name: agent_management → 0.1
                    resolved = nav_coord
                else:
                    # Family path: agent_management.equipment.tools → 0.1.equipment.tools
                    relative_path = ".".join(parts[1:])
                    resolved = f"{nav_coord}.{relative_path}"
                
                if resolved in self.nodes:
                    # print(f"Debug: Resolved family path '{target_coord}' to coordinate '{resolved}'")
                    return resolved
        
        # Resolution 4: System family resolution
        if target_coord.startswith("system."):
            relative_path = target_coord[7:]  # Remove "system."
            resolved = f"0.0.{relative_path}"
            if resolved in self.nodes:
                # print(f"Debug: Resolved system path '{target_coord}' to coordinate '{resolved}'")
                return resolved
        
        # Resolution 5: Partial path search (search for paths ending with the target)
        if "." in target_coord:
            for coord in self.nodes.keys():
                if coord.endswith(f".{target_coord}") or coord.endswith(target_coord):
                    # print(f"Debug: Resolved partial path '{target_coord}' to coordinate '{coord}'")
                    return coord
        
        # print(f"Debug: Could not resolve semantic address '{target_coord}', trying as-is")
        return target_coord
    
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
                if args_str == "()":
                    args = "()"  # Special case: () means no-args
                else:
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
                        if args_str == "()":
                            args = "()"  # Special case: () means no-args
                        else:
                            args = json.loads(args_str)
                        result, success = await self._execute_action(target_coord, args)
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
    
    async def _handle_jump(self, args_str: str) -> dict:
        """Handle jump command with semantic resolution."""
        parts = args_str.split(None, 1)
        if not parts:
            return {"error": "jump requires target coordinate"}
            
        original_target = parts[0]
        args_str = parts[1] if len(parts) > 1 else ""
        
        # Apply semantic resolution
        target_coord = self._resolve_semantic_address(original_target)
        
        if target_coord not in self.nodes and target_coord not in self.numeric_nodes:
            return {"error": f"Target coordinate '{original_target}' not found (resolved to '{target_coord}')"}
            
        # Jump to target
        self.current_position = target_coord
        self.stack.append(target_coord)
        
        # If args provided, execute immediately
        if args_str:
            try:
                if args_str == "()":
                    args = "()"  # Special case: () means no-args
                else:
                    args = json.loads(args_str)
                result, success = await self._execute_action(target_coord, args)
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
    
    def _parse_chain_with_operands(self, chain_str: str) -> list:
        """Parse chain string with operands into execution plan.
        
        Uses improved operand parser with Lark validation.
        """
        # Try to validate with Lark for better error messages
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from lark_parser import create_lark_parser
            
            lark_parser = create_lark_parser()
            if lark_parser:
                # Validate syntax with Lark
                result = lark_parser.parse(f"chain {chain_str}")
                if not result["success"]:
                    # Return error with better Lark message
                    return [{"error": f"Syntax error: {result['error']}"}]
        except:
            pass  # Lark not available, continue with manual parsing
        
        # Use our working operand parser 
        try:
            from operand_parser import OperandParser
            
            # Check if chain has operands
            has_operands = any(op in chain_str for op in [' and ', ' or ', ' if ', ' while '])
            
            if has_operands:
                parser = OperandParser()
                return parser.parse_chain(chain_str)
        except:
            pass  # Fall back to simple parsing
        
        # Simple sequential parsing fallback
        steps = chain_str.split(" -> ")
        execution_plan = []
        for i, step in enumerate(steps):
            execution_plan.append({
                "type": "sequential",
                "step": step.strip(), 
                "target": step.strip().split(None, 1)[0],
                "args_str": step.strip().split(None, 1)[1] if len(step.strip().split(None, 1)) > 1 else "{}",
                "index": i,
                "segment": 0
            })
        return execution_plan
    
    async def _handle_chain(self, args_str: str) -> dict:
        """Handle chain command - with control flow operands support."""
        if not args_str:
            return {"error": "chain requires sequence specification"}
            
        # Parse chain with operand support
        execution_plan = self._parse_chain_with_operands(args_str)
        
        # Check if we have operands
        has_operands = any(step.get('operator') or step.get('branch') or step.get('loop') 
                          for step in execution_plan)
        
        if has_operands:
            # Use operand executor for complex chains
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from operand_executor import OperandExecutor
            
            executor = OperandExecutor(self)
            result = await executor.execute_plan(execution_plan)
            
            # Format results for display
            chain_results = []
            for i, res in enumerate(result['results']):
                chain_results.append({
                    "step": i + 1,
                    "target": res.get('target'),
                    "resolved": res.get('resolved'),
                    "success": res.get('success'),
                    "operator": res.get('operator'),
                    "branch": res.get('step', {}).get('branch'),
                    "result": res.get('data')
                })
            
            return self._build_response({
                "action": "chain_with_operands",
                "execution_plan": execution_plan,
                "chain_results": chain_results,
                "total_steps": result['total_steps'],
                "executed_steps": result['executed_steps']
            })
        
        # Original sequential chain logic for backward compatibility
        steps = args_str.split(" -> ")
        chain_results = []
        
        for i, step in enumerate(steps):
            step = step.strip()
            parts = step.split(None, 1)
            target_coord = parts[0]
            step_args_str = parts[1] if len(parts) > 1 else "{}"
            
            try:
                if step_args_str == "()":
                    step_args = "()"  # Special case: () means no-args
                else:
                    step_args = json.loads(step_args_str)
            except json.JSONDecodeError:
                return {"error": f"Invalid JSON in step {i+1}: {step_args_str}"}
                
            # Check if target is a shortcut first, then resolve to coordinate
            final_coord = target_coord
            shortcuts = self.session_vars.get("_shortcuts", {})
            
            if target_coord in shortcuts:
                shortcut = shortcuts[target_coord]
                if isinstance(shortcut, dict):
                    if shortcut.get("type") == "jump":
                        final_coord = shortcut["coordinate"]
                    elif shortcut.get("type") == "chain":
                        # Chain shortcuts in chains need special handling
                        return {"error": f"Cannot use chain shortcut '{target_coord}' inside chain command at step {i+1}"}
                else:
                    # Legacy shortcut format
                    final_coord = shortcut
            
            if final_coord not in self.nodes:
                # Check legacy nodes as fallback
                if not (hasattr(self, 'legacy_nodes') and final_coord in self.legacy_nodes):
                    return {"error": f"Target coordinate {final_coord} not found in step {i+1} (resolved from '{target_coord}')"}
                
            # Execute step
            result, success = await self._execute_action(final_coord, step_args)
            if not success:
                return {"error": f"Step {i+1} failed: {result}"}
                
            chain_results.append({
                "step": i+1,
                "target": target_coord,  # Keep original shortcut name for display
                "resolved_coord": final_coord if target_coord != final_coord else None,  # Show resolution only if different
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
    
    def _handle_nav(self) -> dict:
        """Show complete tree navigation overview."""
        tree_structure = {}
        
        # Build hierarchical structure from clean numeric nodes
        for coordinate, node in self.numeric_nodes.items():
                
            parts = coordinate.split(".")
            current = tree_structure
            
            # Navigate/create nested structure
            for i, part in enumerate(parts):
                coord_so_far = ".".join(parts[:i+1])
                
                if part not in current:
                    current[part] = {
                        "coordinate": coord_so_far,
                        "node": self.nodes.get(coord_so_far, {}),
                        "children": {}
                    }
                
                if i == len(parts) - 1:
                    # This is the final node, update its info
                    current[part]["node"] = node
                else:
                    # Navigate deeper
                    current = current[part]["children"]
        
        # Format tree structure for display
        def format_tree_level(level_dict, depth=0, prefix="", is_last=True):
            lines = []
            # Sort keys numerically by coordinate parts, not alphabetically
            def sort_key(x):
                parts = x.split('.')
                # Convert all parts to strings with numeric padding for proper sorting
                padded_parts = []
                for p in parts:
                    if p.isdigit():
                        padded_parts.append(f"{int(p):08d}")  # Pad numbers to 8 digits
                    else:
                        padded_parts.append(p)
                return (len(parts), padded_parts)
            
            sorted_keys = sorted(level_dict.keys(), key=sort_key)
            
            for i, key in enumerate(sorted_keys):
                is_last_item = (i == len(sorted_keys) - 1)
                item = level_dict[key]
                node = item["node"]
                coordinate = item["coordinate"]
                
                # Get node info
                node_type = node.get("type", "Unknown")
                prompt = node.get("prompt", "No prompt")
                description = node.get("description", "")
                
                # Ontological emoji DSL - each emoji represents a semantic category
                if node_type == "Menu":
                    # Domain-specific navigation classifiers
                    if depth == 0:  # Root
                        icon = "🔮"  # Root crystal (special case)
                    elif "Brain" in prompt:
                        icon = "🧠"  # Brain/AI/knowledge domain
                    elif "Doc" in prompt or "Help" in prompt:
                        icon = "📜"  # Documentation/help domain  
                    elif "MCP" in prompt or "Generator" in prompt:
                        icon = "🚀"  # Generation/creation domain
                    elif "OmniTool" in prompt or "Tool" in prompt:
                        icon = "🛠️"  # Tools/utilities domain
                    elif "Meta" in prompt or "Operations" in prompt:
                        icon = "🌀"  # Meta/system operations domain
                    elif "Agent" in prompt:
                        icon = "🤖"  # Agent systems domain
                    else:
                        icon = "🗺️"  # General navigation hub
                    options_count = len(node.get("options", {}))
                    info = f"({options_count} paths)"
                elif node_type == "Callable":
                    # Universal executable classifier
                    icon = "⚙️"  # All executable functions use gear
                    function_name = node.get("function_name", "")
                    info = f"({function_name})" if function_name else ""
                else:
                    icon = "❔"  # Unknown type
                    info = f"({node_type})"
                
                # ASCII tree structure
                if depth == 0:
                    # Root node - no prefix
                    current_prefix = ""
                    line_prefix = ""
                else:
                    # Branch characters
                    branch = "└── " if is_last_item else "├── "
                    line_prefix = prefix + branch
                
                # Build line with ASCII tree structure
                line = f"{line_prefix}{icon} {coordinate}: {prompt} {info}"
                if description and len(description) < 50:
                    line += f" - {description}"
                
                lines.append(line)
                
                # Add children with proper prefix continuation
                if item["children"]:
                    if depth == 0:
                        # Root level - children start with empty prefix but get tree structure
                        child_prefix = ""
                    else:
                        # Add vertical continuation or spaces
                        continuation = "│   " if not is_last_item else "    "
                        child_prefix = prefix + continuation
                    
                    lines.extend(format_tree_level(item["children"], depth + 1, child_prefix, is_last_item))
            
            return lines
        
        tree_lines = format_tree_level(tree_structure, 0, "", True)
        tree_display = "\n".join(tree_lines)
        
        # Add summary stats
        summary = {
            "total_nodes": len(self.nodes),
            "menu_nodes": len([n for n in self.nodes.values() if n.get("type") == "Menu"]),
            "callable_nodes": len([n for n in self.nodes.values() if n.get("type") == "Callable"]),
            "current_position": self.current_position,
            "max_depth": max(len(coord.split(".")) for coord in self.nodes.keys()) if self.nodes else 0
        }
        
        return self._build_response({
            "action": "navigation_overview",
            "tree_structure": tree_display,
            "summary": summary,
            "usage": "Use 'jump <coordinate>' to navigate directly to any node",
            "message": f"Navigation overview: {summary['total_nodes']} total nodes"
        })
    
    def _handle_shortcut(self, args_str: str) -> dict:
        """Create semantic shortcut for jump commands or chain templates."""
        if not args_str:
            return {"error": "Usage: shortcut <alias> <coordinate|\"chain_template\"> - e.g., shortcut brain 0.0.6 or shortcut workflow \"0.1.1 {} -> 0.1.2 {\\\"data\\\": \\\"$step1_result\\\"}\""}
        
        # Handle quoted chain templates vs simple coordinates
        if args_str.count('"') >= 2:
            # Chain template format: shortcut alias "chain template"
            first_quote = args_str.find('"')
            alias = args_str[:first_quote].strip()
            chain_template = args_str[first_quote+1:]
            if chain_template.endswith('"'):
                chain_template = chain_template[:-1]
            
            if not alias:
                return {"error": "Alias cannot be empty"}
                
            # Validate chain template by parsing it
            try:
                # Simple validation - chain can be single step or multiple with ->
                if not chain_template.strip():
                    return {"error": "Chain template cannot be empty"}
                
                # Analyze template for constraints (like pathway analysis)
                template_analysis = self._analyze_chain_template_simple(chain_template)
                
                # Initialize shortcuts storage if not exists
                if "_shortcuts" not in self.session_vars:
                    self.session_vars["_shortcuts"] = {}
                
                # Store as chain shortcut
                shortcut_data = {
                    "type": "chain",
                    "template": chain_template,
                    "analysis": template_analysis
                }
                self.session_vars["_shortcuts"][alias] = shortcut_data
                
                # Save to appropriate JSON file
                self._save_shortcut_to_file(alias, shortcut_data)
                
                return self._build_response({
                    "action": "create_shortcut",
                    "alias": alias,
                    "type": "chain",
                    "template": chain_template,
                    "required_args": template_analysis.get("entry_args", []),
                    "usage": f"Use '{alias} {{args}}' to execute chain template" + (f" (requires: {', '.join(template_analysis.get('entry_args', []))})" if template_analysis.get('entry_args') else ""),
                    "message": f"Chain shortcut '{alias}' created ({template_analysis.get('type', 'unconstrained')} template)"
                })
                
            except Exception as e:
                return {"error": f"Invalid chain template: {str(e)}"}
        
        else:
            # Simple coordinate format: shortcut alias coordinate
            parts = args_str.split(None, 1)
            if len(parts) != 2:
                return {"error": "Usage: shortcut <alias> <coordinate> - e.g., shortcut brain 0.0.6"}
            
            alias, coordinate = parts
            
            # Validate coordinate exists
            if coordinate not in self.nodes:
                return {"error": f"Coordinate '{coordinate}' not found. Use 'nav' to see all available nodes."}
            
            # Get node info for display
            node = self.nodes[coordinate]
            node_prompt = node.get("prompt", "Unknown")
            
            # Initialize shortcuts storage if not exists
            if "_shortcuts" not in self.session_vars:
                self.session_vars["_shortcuts"] = {}
            
            # Store as simple jump shortcut
            shortcut_data = {
                "type": "jump",
                "coordinate": coordinate
            }
            self.session_vars["_shortcuts"][alias] = shortcut_data
            
            # Save to appropriate JSON file
            self._save_shortcut_to_file(alias, shortcut_data)
            
            return self._build_response({
                "action": "create_shortcut",
                "alias": alias,
                "type": "jump",
                "coordinate": coordinate,
                "target": node_prompt,
                "usage": f"Use '{alias}' to jump to {coordinate} ({node_prompt})",
                "message": f"Jump shortcut '{alias}' → {coordinate} ({node_prompt}) created"
            })
    
    def _analyze_chain_template_simple(self, chain_template: str) -> dict:
        """Simple analysis of chain template for variable constraints."""
        import re
        
        # Find all variables in the template (format: $variable_name)
        variables = set(re.findall(r'\$(\w+)', chain_template))
        # Remove step result variables (generated automatically)
        entry_args = [var for var in variables if not var.startswith('step') and var != 'last_result']
        
        template_type = "constrained" if entry_args else "unconstrained"
        
        return {
            "type": template_type,
            "entry_args": entry_args,
            "total_variables": list(variables)
        }
    
    def _handle_list_shortcuts(self) -> dict:
        """List all active shortcuts."""
        shortcuts = self.session_vars.get("_shortcuts", {})
        
        if not shortcuts:
            return self._build_response({
                "action": "list_shortcuts",
                "shortcuts": {},
                "count": 0,
                "message": "No shortcuts defined. Create one with: shortcut <alias> <coordinate>"
            })
        
        # Build shortcut info with target details
        shortcut_info = {}
        for alias, shortcut in shortcuts.items():
            if isinstance(shortcut, str):
                # Legacy format - simple coordinate
                node = self.nodes.get(shortcut, {})
                shortcut_info[alias] = {
                    "shortcut_type": "jump",
                    "coordinate": shortcut,
                    "target": node.get("prompt", "Unknown"),
                    "description": node.get("description", ""),
                    "type": node.get("type", "Unknown")
                }
            elif isinstance(shortcut, dict):
                shortcut_type = shortcut.get("type", "jump")
                
                if shortcut_type == "jump":
                    coordinate = shortcut["coordinate"]
                    node = self.nodes.get(coordinate, {})
                    shortcut_info[alias] = {
                        "shortcut_type": "jump",
                        "coordinate": coordinate,
                        "target": node.get("prompt", "Unknown"),
                        "description": node.get("description", ""),
                        "type": node.get("type", "Unknown")
                    }
                elif shortcut_type == "chain":
                    analysis = shortcut.get("analysis", {})
                    shortcut_info[alias] = {
                        "shortcut_type": "chain",
                        "template": shortcut["template"],
                        "template_type": analysis.get("type", "unconstrained"),
                        "required_args": analysis.get("entry_args", []),
                        "target": "Chain Template"
                    }
        
        return self._build_response({
            "action": "list_shortcuts",
            "shortcuts": shortcut_info,
            "count": len(shortcuts),
            "usage": "Type any alias to jump to its target, or 'shortcut <alias> <coordinate>' to create new ones",
            "message": f"{len(shortcuts)} shortcuts defined"
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
    
    def _handle_set(self, args_str: str) -> dict:
        """Handle set command for variable assignment."""
        if not args_str:
            return {"error": "Usage: set $variable_name to value"}
        
        # Parse: set $var_name to value
        parts = args_str.split(" to ", 1)
        if len(parts) != 2:
            return {"error": "Usage: set $variable_name to value"}
        
        var_name_part = parts[0].strip()
        value_part = parts[1].strip()
        
        # Extract variable name (remove $ if present)
        if var_name_part.startswith("$"):
            var_name = var_name_part[1:]
        else:
            var_name = var_name_part
        
        if not var_name:
            return {"error": "Variable name cannot be empty"}
        
        # Try to parse value as JSON, fall back to string
        try:
            value = json.loads(value_part)
        except json.JSONDecodeError:
            value = value_part
        
        # Store in session variables
        self.session_vars[var_name] = value
        
        return self._build_response({
            "action": "set_variable",
            "variable": var_name,
            "value": value,
            "value_type": type(value).__name__,
            "message": f"Set ${var_name} = {value}"
        })
    
