#!/usr/bin/env python3

import os
import sys
import json

# Set HEAVEN_DATA_DIR environment variable
os.environ['HEAVEN_DATA_DIR'] = '/tmp/heaven_data'

sys.path.insert(0, '/home/GOD/heaven-tree-repl')

from heaven_tree_repl.shells import UserTreeShell

def debug_family_loading():
    """Debug family loading in UserTreeShell"""
    print("=== CREATING USERTREESHELL ===")
    
    shell = UserTreeShell(user_config_path=None)
    
    print(f"Shell created successfully")
    print(f"Shell app_id: {shell.app_id}")
    print(f"Shell domain: {shell.domain}")
    print(f"Shell families in config: {shell.graph.get('families', 'NO FAMILIES KEY')}")
    
    print(f"\n=== NODES LOADED ===")
    print(f"Total nodes: {len(shell.nodes)}")
    print(f"Node keys (first 10): {list(shell.nodes.keys())[:10]}")
    
    # Check if root node exists
    if "0" in shell.nodes:
        root_node = shell.nodes["0"]
        print(f"\nRoot node:")
        print(f"  prompt: {root_node.get('prompt', 'NO PROMPT')}")
        print(f"  description: {root_node.get('description', 'NO DESCRIPTION')}")
        print(f"  options: {root_node.get('options', {})}")
    else:
        print("\nNO ROOT NODE!")
    
    # Check for family nodes
    print(f"\n=== FAMILY NODES ===")
    family_node_count = 0
    for key in shell.nodes.keys():
        if "system" in key or "agent" in key or "conversation" in key:
            family_node_count += 1
            if family_node_count <= 5:  # Show first 5
                print(f"  {key}: {shell.nodes[key].get('prompt', 'NO PROMPT')}")
    
    print(f"Total family-related nodes: {family_node_count}")

if __name__ == "__main__":
    debug_family_loading()