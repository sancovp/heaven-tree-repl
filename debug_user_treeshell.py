#!/usr/bin/env python3

import os
import sys
import json

# Set HEAVEN_DATA_DIR environment variable
os.environ['HEAVEN_DATA_DIR'] = '/tmp/heaven_data'

sys.path.insert(0, '/home/GOD/heaven-tree-repl')

from heaven_tree_repl.system_config_loader_v2 import SystemConfigLoader

def debug_config_loading():
    """Debug what configs actually get loaded."""
    print("Testing UserTreeShell config loading...")
    
    # Test the same config loading that UserTreeShell does
    loader = SystemConfigLoader(config_types=["base", "user"])
    final_config = loader.load_and_validate_configs(dev_config_path=None)
    
    print("\n=== FINAL CONFIG ===")
    print(json.dumps(final_config, indent=2))
    
    print(f"\n=== KEY VALUES ===")
    print(f"app_id: {final_config.get('app_id', 'MISSING')}")
    print(f"domain: {final_config.get('domain', 'MISSING')}")
    print(f"role: {final_config.get('role', 'MISSING')}")
    print(f"families: {final_config.get('families', 'MISSING')}")
    
    print(f"\n=== VALIDATION WARNINGS ===")
    warnings = loader.get_validation_warnings()
    if warnings:
        for warning in warnings:
            print(f"  - {warning}")
    else:
        print("  No warnings")
    
    # Test family loading
    print(f"\n=== FAMILY LOADING ===")
    families_list = final_config.get('families', [])
    if families_list:
        families = loader.load_families(families_list, dev_config_path=None)
        print(f"Loaded {len(families)} families: {list(families.keys())}")
        
        for family_name, family_data in families.items():
            nodes_count = len(family_data.get('nodes', {}))
            print(f"  {family_name}: {nodes_count} nodes")
    else:
        print("No families to load")

if __name__ == "__main__":
    debug_config_loading()