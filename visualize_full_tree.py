#!/usr/bin/env python3
"""
Generate full TreeShell mathematical structure visualization.
Shows the complete 3D address space with ALL nodes, coordinates, and zones.
"""

import sys
import os

# Add the package to path
sys.path.insert(0, '/home/GOD/heaven-tree-repl')

try:
    from heaven_tree_repl.shells import UserTreeShell
    
    print("Loading UserTreeShell with full configuration...")
    shell = UserTreeShell()
    
    print("Generating FULL mathematical visualization...")
    result, success = shell._meta_visualize_tree({})
    
    if success:
        print("\n" + "="*80)
        print("FULL TREESHELL MATHEMATICAL STRUCTURE")
        print("="*80 + "\n")
        
        print(result['full_mermaid_diagram'])
        
        print("\n" + "="*80)
        print("MATHEMATICAL STATISTICS")
        print("="*80)
        
        stats = result['mathematical_statistics']
        for key, value in stats.items():
            print(f"{key}: {value}")
        
        print(f"\nComplexity Level: {result['complexity_level']}")
        print(f"Address Space Dimensions: {result['address_dimensions']}")
        
    else:
        print("ERROR generating visualization:")
        print(result)
        
except Exception as e:
    print(f"FAILED to generate visualization: {e}")
    import traceback
    traceback.print_exc()