#!/usr/bin/env python3

import os
import sys
import json

# Set HEAVEN_DATA_DIR environment variable
os.environ['HEAVEN_DATA_DIR'] = '/tmp/heaven_data'

sys.path.insert(0, '/home/GOD/heaven-tree-repl')

from heaven_tree_repl.system_config_loader_v2 import SystemConfigLoader

def debug_what_gets_loaded():
    """Debug exactly what config gets passed to TreeShellBase.__init__"""
    print("=== WHAT USERTREESHELL LOADS ===")
    
    # This is exactly what UserTreeShell does
    loader = SystemConfigLoader(config_types=["base", "user"])
    final_config = loader.load_and_validate_configs(dev_config_path=None)
    
    print("Final config passed to TreeShellBase.__init__:")
    print(json.dumps(final_config, indent=2))
    
    print(f"\n=== DOES IT HAVE 'families'? ===")
    print(f"families key exists: {'families' in final_config}")
    print(f"families value: {final_config.get('families', 'MISSING')}")

if __name__ == "__main__":
    debug_what_gets_loaded()