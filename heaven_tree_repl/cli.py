#!/usr/bin/env python3
"""
CLI entry point for heaven-tree-repl.
"""
import json
import sys
from . import TreeShell
from .renderer import render_response


def get_example_config():
    """Get example configuration for demonstration."""
    return {
        "app_id": "heaven_tree_demo",
        "domain": "example",
        "role": "assistant",
        "nodes": {
            "root": {
                "type": "Menu",
                "prompt": "Demo Menu",
                "description": "HEAVEN Tree REPL Demo",
                "options": {
                    "1": "math_ops",
                    "2": "echo_test"
                }
            },
            "math_ops": {
                "type": "Menu",
                "prompt": "Math Operations",
                "description": "Mathematical operations",
                "options": {
                    "1": "add",
                    "2": "multiply"
                }
            },
            "add": {
                "type": "Callable",
                "prompt": "Add Numbers",
                "description": "Add two numbers together",
                "function_name": "_test_add",
                "args_schema": {"a": "int", "b": "int"}
            },
            "multiply": {
                "type": "Callable", 
                "prompt": "Multiply Numbers",
                "description": "Multiply two numbers",
                "function_name": "_test_multiply",
                "args_schema": {"a": "int", "b": "int"}
            },
            "echo_test": {
                "type": "Callable",
                "prompt": "Echo Test",
                "description": "Echo back the input",
                "function_name": "_echo_test",
                "args_schema": {"message": "str"}
            }
        }
    }


async def main_async():
    """Async main CLI entry point."""
    print("🔮🌳 HEAVEN Tree REPL Demo")
    print("=" * 40)
    
    # Initialize shell with example config
    config = get_example_config()
    shell = TreeShell(config)
    
    # Add echo test function
    def _echo_test(args):
        message = args.get("message", "Hello World!")
        return f"Echo: {message}", True
    
    shell._echo_test = _echo_test
    
    # Show initial menu
    response = await shell.handle_command("")
    print(render_response(response))
    
    # Interactive loop
    try:
        while True:
            command = input(">>> ").strip()
            if command.lower() in ['exit', 'quit']:
                break
            
            response = await shell.handle_command(command)
            print(render_response(response))
            
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    import asyncio
    asyncio.run(main_async())


if __name__ == "__main__":
    main()