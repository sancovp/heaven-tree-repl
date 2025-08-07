#!/usr/bin/env python3
"""
Interactive REPL for HEAVEN TreeShell - Universal human interface.

Usage:
    python interactive_repl.py                    # UserTreeShell with default config
    python interactive_repl.py --shell-type user  # UserTreeShell 
    python interactive_repl.py --shell-type agent # AgentTreeShell
    python interactive_repl.py --shell-type full  # FullstackTreeShell
    python interactive_repl.py --config config.json # Custom config file
"""
import json
import sys
import argparse
import os
import asyncio
from heaven_tree_repl import TreeShell, AgentTreeShell, UserTreeShell, FullstackTreeShell, render_response


def get_default_config():
    """Get minimal default configuration for basic TreeShell functionality."""
    return {
        "app_id": "interactive_repl",
        "domain": "user_interface",
        "role": "human_interface",
        "nodes": {}  # Will use default nodes from base TreeShell
    }


def load_config_file(config_path: str) -> dict:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Config file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in config file: {e}")
        sys.exit(1)


def create_shell(shell_type: str, config: dict):
    """Create the appropriate TreeShell instance."""
    if shell_type == "basic":
        return TreeShell(config)
    elif shell_type == "agent":
        return AgentTreeShell(config)
    elif shell_type == "user":
        return UserTreeShell(config)
    elif shell_type == "full":
        return FullstackTreeShell(config)
    else:
        print(f"❌ Unknown shell type: {shell_type}")
        print("Valid types: basic, agent, user, full")
        sys.exit(1)


async def async_main():
    """Async main interactive REPL entry point."""
    parser = argparse.ArgumentParser(description="Interactive REPL for HEAVEN TreeShell")
    parser.add_argument("--shell-type", "-t", 
                        choices=["basic", "agent", "user", "full"],
                        default="user",
                        help="Type of TreeShell to create (default: user)")
    parser.add_argument("--config", "-c",
                        help="Path to JSON configuration file")
    parser.add_argument("--quiet", "-q",
                        action="store_true",
                        help="Suppress welcome banner")
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config:
        config = load_config_file(args.config)
    else:
        config = get_default_config()
    
    if not args.quiet:
        print("🔮🌳 HEAVEN TreeShell Interactive REPL")
        print("=" * 50)
        print(f"Shell Type: {args.shell_type.title()}TreeShell")
        print(f"Config: {'Custom' if args.config else 'Default'}")
        if args.config:
            print(f"Config File: {args.config}")
        print("=" * 50)
        print("Commands: Type numbers, 'jump X.Y.Z', 'chain', 'exit', etc.")
        print("Help: Navigate to 0.2 (docs) for full command reference")
        print("Exit: Type 'exit', 'quit', or Ctrl+C")
        print()
    
    # Create TreeShell instance
    try:
        shell = create_shell(args.shell_type, config)
    except Exception as e:
        print(f"❌ Error creating {args.shell_type} shell: {e}")
        sys.exit(1)
    
    # Show initial menu
    try:
        response = await shell.handle_command("")
        print(render_response(response))
    except Exception as e:
        print(f"❌ Error showing initial menu: {e}")
        sys.exit(1)
    
    # Interactive loop
    try:
        while True:
            try:
                command = input("🌳 >>> ").strip()
            except EOFError:
                # Handle Ctrl+D gracefully
                break
                
            if command.lower() in ['exit', 'quit', 'q']:
                break
            
            try:
                response = await shell.handle_command(command)
                print(render_response(response))
            except Exception as e:
                print(f"❌ Error executing command: {e}")
                print("Use 'menu' to return to nearest menu or 'jump 0' for root")
                
    except KeyboardInterrupt:
        pass
    
    print("\n👋 Goodbye! TreeShell session ended.")


def main():
    """Sync wrapper for async main."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()