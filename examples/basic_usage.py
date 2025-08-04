#!/usr/bin/env python3
"""
Basic usage example for HEAVEN Tree REPL.
"""
from heaven_tree_repl import TreeShell, render_response


def main():
    # Create a simple tree configuration
    config = {
        "app_id": "example_app",
        "domain": "demo",
        "role": "assistant",
        "nodes": {
            "root": {
                "type": "Menu",
                "prompt": "Example Menu",
                "description": "A simple example tree",
                "options": {
                    "1": "greet",
                    "2": "math"
                }
            },
            "greet": {
                "type": "Callable",
                "prompt": "Greeting",
                "description": "Say hello to someone",
                "function_name": "_greet",
                "args_schema": {"name": "str"}
            },
            "math": {
                "type": "Callable", 
                "prompt": "Add Numbers",
                "description": "Add two numbers",
                "function_name": "_test_add",
                "args_schema": {"a": "int", "b": "int"}
            }
        }
    }
    
    # Initialize TreeShell
    shell = TreeShell(config)
    
    # Add custom function
    def _greet(args):
        name = args.get("name", "World")
        return f"Hello, {name}!", True
    
    shell._greet = _greet
    
    print("=== HEAVEN Tree REPL Example ===\n")
    
    # Show main menu
    response = shell.handle_command("")
    print(render_response(response))
    
    # Navigate to greeting
    response = shell.handle_command("1")
    print(render_response(response))
    
    # Execute greeting with argument
    response = shell.handle_command('1 {"name": "HEAVEN"}')
    print(render_response(response))
    
    # Go back and try math
    response = shell.handle_command("back")
    print(render_response(response))
    
    response = shell.handle_command("2")
    print(render_response(response))
    
    response = shell.handle_command('1 {"a": 42, "b": 13}')
    print(render_response(response))


if __name__ == "__main__":
    main()