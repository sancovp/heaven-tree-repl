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
        """Add a new node to the tree structure."""
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
            
        # Add the node
        self.nodes[coordinate] = node_data.copy()
        
        result = {
            "added": True,
            "coordinate": coordinate,
            "node_type": node_data["type"],
            "prompt": node_data["prompt"]
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