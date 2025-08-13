#!/usr/bin/env python3
"""
Lark-based parser for TreeShell language.
"""
try:
    from lark import Lark, Transformer, v_args
    from lark.exceptions import LarkError
    LARK_AVAILABLE = True
except ImportError:
    LARK_AVAILABLE = False
    print("Warning: Lark not installed. Using fallback parser.")

import json
import re
from typing import Dict, List, Any, Optional


class TreeShellTransformer(Transformer):
    """Transform parse tree into execution plan."""
    
    @v_args(inline=True)
    def coordinate(self, coord):
        return {"type": "coordinate", "value": str(coord)}
    
    @v_args(inline=True) 
    def shortcut(self, name):
        return {"type": "shortcut", "value": str(name)}
    
    @v_args(inline=True)
    def variable(self, var):
        return {"type": "variable", "value": str(var)}
    
    @v_args(inline=True)
    def json_args(self, json_str):
        try:
            return {"type": "json", "value": json.loads(str(json_str))}
        except json.JSONDecodeError:
            return {"type": "json", "value": {}, "error": "Invalid JSON"}
    
    def no_args(self, _):
        return {"type": "no_args", "value": "()"}
    
    @v_args(inline=True)
    def template_args(self, template):
        return {"type": "template", "value": str(template)}
    
    @v_args(inline=True)
    def step(self, target, args=None):
        return {
            "type": "step",
            "target": target,
            "args": args or {"type": "json", "value": {}}
        }
    
    @v_args(inline=True)
    def single_step(self, step):
        return {"type": "single", "step": step}
    
    @v_args(inline=True)
    def sequential(self, left, right):
        return {"type": "sequential", "left": left, "right": right}
    
    @v_args(inline=True)
    def parallel(self, left, right):
        return {"type": "parallel", "left": left, "right": right, "operator": "and"}
    
    @v_args(inline=True)
    def alternative(self, left, right):
        return {"type": "alternative", "left": left, "right": right, "operator": "or"}
    
    def if_then_else(self, items):
        condition = items[0]
        then_branch = items[1]
        else_branch = items[2] if len(items) > 2 else None
        
        return {
            "type": "conditional",
            "condition": condition,
            "then_branch": then_branch,
            "else_branch": else_branch
        }
    
    @v_args(inline=True)
    def while_loop(self, condition, body):
        return {
            "type": "while_loop",
            "condition": condition,
            "body": body
        }
    
    @v_args(inline=True)
    def for_loop(self, loop_var, collection_var, body):
        return {
            "type": "for_loop",
            "loop_var": str(loop_var),
            "collection_var": str(collection_var),
            "body": body
        }
    
    @v_args(inline=True)
    def in_condition(self, item_var, collection_var):
        return {
            "type": "in_condition", 
            "item_var": str(item_var),
            "collection_var": str(collection_var)
        }
    
    def if_in_then_else(self, items):
        condition = items[0]
        then_branch = items[1]
        else_branch = items[2] if len(items) > 2 else None
        
        return {
            "type": "conditional_in",
            "condition": condition,
            "then_branch": then_branch,
            "else_branch": else_branch
        }
    
    @v_args(inline=True)
    def map_operation(self, target, source_var, result_var):
        return {
            "type": "map_operation",
            "target": target,
            "source_var": str(source_var),
            "result_var": str(result_var)
        }
    
    def give_operation(self, items):
        # Handle the list of parsed items from give expression
        alias = None
        item_var = None
        target = None
        
        # Process each item in the list  
        for item in items:
            if isinstance(item, dict):
                # This is our target (variable, coordinate, or shortcut)
                if item.get("type") in ["variable", "coordinate", "shortcut"]:
                    if target is None:
                        target = item
            elif hasattr(item, 'value'):
                # This is a token - check if it's our item variable
                if str(item.value).startswith('$'):
                    item_var = str(item.value)
                else:
                    # Could be our alias
                    alias = str(item.value)
        
        return {
            "type": "give_operation",
            "alias": alias,
            "item_var": item_var or "",
            "target": target or {"type": "unknown", "value": ""}
        }
    
    @v_args(inline=True)
    def grouped(self, expr):
        return expr
    
    @v_args(inline=True)
    def chain(self, expr):
        return {"type": "chain", "expression": expr}
    
    @v_args(inline=True)
    def jump_command(self, target, args=None):
        return {
            "type": "jump",
            "target": target,
            "args": args or {"type": "json", "value": {}}
        }
    
    def back_command(self, _):
        return {"type": "back"}
    
    def menu_command(self, _):
        return {"type": "menu"}
    
    def exit_command(self, _):
        return {"type": "exit"}
    
    def nav_command(self, _):
        return {"type": "nav"}
    
    def lang_command(self, _):
        return {"type": "lang"}
    
    @v_args(inline=True)
    def shortcut_exec(self, shortcut, args=None):
        return {
            "type": "shortcut_exec",
            "shortcut": shortcut,
            "args": args or {"type": "json", "value": {}}
        }
    
    @v_args(inline=True)
    def number_selection(self, number, args=None):
        return {
            "type": "number_selection",
            "number": int(str(number)),
            "args": args or {"type": "json", "value": {}}
        }
    
    @v_args(inline=True)
    def exec_command(self, target, args=None):
        return {
            "type": "exec_command",
            "target": target,
            "args": args or {"type": "json", "value": {}}
        }
    
    @v_args(inline=True)
    def exec_command_parens(self, target):
        return {
            "type": "exec_command",
            "target": target,
            "args": {"type": "json", "value": {}}
        }
    
    @v_args(inline=True)
    def jump_shortcut(self, alias, target):
        return {
            "type": "shortcut_definition",
            "subtype": "jump",
            "alias": str(alias),
            "target": target
        }
    
    @v_args(inline=True)
    def chain_shortcut(self, alias, template):
        return {
            "type": "shortcut_definition", 
            "subtype": "chain",
            "alias": str(alias),
            "template": str(template).strip('"')
        }
    
    def build_pathway(self, _):
        return {"type": "build_pathway"}
    
    @v_args(inline=True)
    def save_pathway(self, name):
        return {"type": "save_pathway", "name": str(name)}
    
    @v_args(inline=True)
    def follow_pathway(self, name, args=None):
        return {
            "type": "follow_pathway",
            "name": str(name),
            "args": args or {"type": "json", "value": {}}
        }
    
    def show_history(self, _):
        return {"type": "show_history"}
    
    def analyze_patterns(self, _):
        return {"type": "analyze_patterns"}
    
    def list_shortcuts(self, _):
        return {"type": "list_shortcuts"}


class LarkTreeShellParser:
    """Lark-based parser for TreeShell commands."""
    
    def __init__(self):
        if not LARK_AVAILABLE:
            raise ImportError("Lark parser requires: pip install lark")
            
        # Load grammar from file
        import os
        grammar_file = os.path.join(os.path.dirname(__file__), "treeshell_grammar.lark")
        
        with open(grammar_file, 'r') as f:
            grammar = f.read()
        
        self.parser = Lark(grammar, parser='lalr')
        self.transformer = TreeShellTransformer()
    
    def parse(self, command_str: str) -> Dict[str, Any]:
        """Parse TreeShell command into AST."""
        try:
            tree = self.parser.parse(command_str.strip())
            result = self.transformer.transform(tree)
            
            # Extract the actual command from the tree structure
            if hasattr(result, 'children') and result.children:
                # Navigate: start -> command -> actual_command
                command_tree = result.children[0]
                if hasattr(command_tree, 'children') and command_tree.children:
                    actual_result = command_tree.children[0]
                else:
                    actual_result = result
            else:
                actual_result = result
            
            return {
                "success": True,
                "ast": actual_result,
                "original": command_str
            }
        except LarkError as e:
            return {
                "success": False,
                "error": str(e),
                "original": command_str,
                "fallback_needed": True
            }
    
    def to_execution_plan(self, ast: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert AST to execution plan compatible with current system."""
        plan = []
        self._ast_to_plan(ast, plan)
        return plan
    
    def _ast_to_plan(self, node, plan: List[Dict[str, Any]]):
        """Recursively convert AST nodes to execution steps."""
        # Handle Tree objects from Lark
        if hasattr(node, 'data') and hasattr(node, 'children'):
            # This is a Lark Tree, extract the transformed data
            if node.children and isinstance(node.children[0], dict):
                node = node.children[0]
            else:
                return
        
        if not isinstance(node, dict):
            return
            
        node_type = node.get("type")
        
        if node_type == "step":
            target = node["target"]
            args = node["args"]
            
            plan.append({
                "type": "execution",
                "target": target["value"], 
                "target_type": target["type"],
                "args": args["value"] if args["type"] == "json" else args["value"],
                "args_type": args["type"]
            })
            
        elif node_type == "sequential":
            self._ast_to_plan(node["left"], plan)
            self._ast_to_plan(node["right"], plan)
            # Mark right side as sequential
            if plan:
                plan[-1]["sequence"] = True
                
        elif node_type == "parallel":
            self._ast_to_plan(node["left"], plan)
            self._ast_to_plan(node["right"], plan)
            # Mark right side as parallel
            if plan:
                plan[-1]["operator"] = "and"
                
        elif node_type == "alternative":
            self._ast_to_plan(node["left"], plan)
            self._ast_to_plan(node["right"], plan)
            # Mark right side as alternative
            if plan:
                plan[-1]["operator"] = "or"
                
        elif node_type == "conditional":
            # Add condition step
            self._ast_to_plan(node["condition"], plan)
            if plan:
                plan[-1]["role"] = "condition"
            
            # Add then branch
            then_start = len(plan)
            self._ast_to_plan(node["then_branch"], plan)
            for i in range(then_start, len(plan)):
                plan[i]["branch"] = "then"
                plan[i]["condition_ref"] = then_start - 1
                
            # Add else branch if exists
            if node["else_branch"]:
                else_start = len(plan)
                self._ast_to_plan(node["else_branch"], plan)
                for i in range(else_start, len(plan)):
                    plan[i]["branch"] = "else"
                    plan[i]["condition_ref"] = then_start - 1
                    
        elif node_type == "while_loop":
            # Add condition step
            self._ast_to_plan(node["condition"], plan)
            if plan:
                plan[-1]["role"] = "while_condition"
                
            # Add body
            body_start = len(plan)
            self._ast_to_plan(node["body"], plan)
            for i in range(body_start, len(plan)):
                plan[i]["loop"] = "while_body"
                plan[i]["condition_ref"] = body_start - 1
                
        elif node_type == "for_loop":
            # Add for loop setup - this needs special handling to validate collection
            plan.append({
                "type": "for_loop_setup",
                "loop_var": node["loop_var"],
                "collection_var": node["collection_var"],
                "role": "for_condition"
            })
            
            # Add body
            body_start = len(plan)
            self._ast_to_plan(node["body"], plan)
            for i in range(body_start, len(plan)):
                plan[i]["loop"] = "for_body"
                plan[i]["loop_var"] = node["loop_var"]
                plan[i]["condition_ref"] = body_start - 1
                
        elif node_type == "conditional_in":
            # Add in-condition check - this needs to validate collection
            condition = node["condition"]
            plan.append({
                "type": "in_condition_check",
                "item_var": condition["item_var"],
                "collection_var": condition["collection_var"],
                "role": "in_condition"
            })
            
            # Add then branch
            then_start = len(plan)
            self._ast_to_plan(node["then_branch"], plan)
            for i in range(then_start, len(plan)):
                plan[i]["branch"] = "then"
                plan[i]["condition_ref"] = then_start - 1
                
            # Add else branch if exists
            if node["else_branch"]:
                else_start = len(plan)
                self._ast_to_plan(node["else_branch"], plan)
                for i in range(else_start, len(plan)):
                    plan[i]["branch"] = "else"
                    plan[i]["condition_ref"] = then_start - 1
                    
        elif node_type == "map_operation":
            # Add map operation - needs special handling to validate collection and execute mapping
            target = node["target"]
            plan.append({
                "type": "map_execution",
                "target": target["value"],
                "target_type": target["type"],
                "source_var": node["source_var"],
                "result_var": node["result_var"],
                "role": "map_operation"
            })
            
        elif node_type == "give_operation":
            # Add give operation - mutates target with item using type-based semantics
            target = node["target"]
            plan.append({
                "type": "give_execution",
                "target": target["value"],
                "target_type": target["type"], 
                "item_var": node["item_var"],
                "alias": node["alias"],
                "role": "give_operation"
            })
                
        elif node_type == "single":
            self._ast_to_plan(node["step"], plan)
            
        elif node_type == "chain":
            self._ast_to_plan(node["expression"], plan)
            
        elif node_type == "exec_command":
            target = node["target"]
            args = node["args"]
            
            plan.append({
                "type": "exec_execution",
                "target": target["value"],
                "target_type": target["type"],
                "args": args["value"] if args["type"] == "json" else args["value"],
                "args_type": args["type"]
            })


def create_lark_parser() -> Optional[LarkTreeShellParser]:
    """Create Lark parser if available."""
    if not LARK_AVAILABLE:
        return None
        
    try:
        return LarkTreeShellParser()
    except Exception as e:
        print(f"Failed to create Lark parser: {e}")
        return None


# Example usage and testing
if __name__ == "__main__":
    parser = create_lark_parser()
    if not parser:
        print("Lark parser not available")
        exit(1)
    
    test_commands = [
        "jump 0.1.2",
        "brain {}",
        "chain settings {} -> docs {}",
        "chain brain {} and save {} and docs {}",
        "chain if 0.5.1 {} then settings {} else docs {}",
        "shortcut test 0.1.2",
        "shortcut workflow \"step1 {} -> step2 {}\"",
        "while counter {} x increment {}"
    ]
    
    for cmd in test_commands:
        print(f"\nParsing: {cmd}")
        result = parser.parse(cmd)
        if result["success"]:
            print(f"✓ Parsed successfully")
            print(f"  AST: {result['ast']}")
            try:
                plan = parser.to_execution_plan(result["ast"])
                for i, step in enumerate(plan):
                    print(f"  Step {i}: {step}")
            except Exception as e:
                print(f"  Plan generation error: {e}")
        else:
            print(f"✗ Error: {result['error']}")