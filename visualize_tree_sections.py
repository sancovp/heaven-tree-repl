#!/usr/bin/env python3
"""
Generate TreeShell visualization in manageable sections.
Shows the mathematical structure broken down into readable chunks.
"""

import sys
sys.path.insert(0, '/home/GOD/heaven-tree-repl')

try:
    from heaven_tree_repl.shells import UserTreeShell
    
    print("Loading UserTreeShell...")
    shell = UserTreeShell()
    
    # Section 1: Overview Statistics
    print("\n" + "="*60)
    print("TREESHELL MATHEMATICAL OVERVIEW")
    print("="*60)
    
    total_nodes = len(shell.nodes) if hasattr(shell, 'nodes') else 0
    total_nav_coords = len(shell.combo_nodes) if hasattr(shell, 'combo_nodes') else 0
    
    zone_roots = set()
    if hasattr(shell, 'zone_config'):
        for config_data in shell.zone_config.values():
            zone = config_data.get("zone", "default")
            zone_roots.add(zone)
    
    node_types = {}
    if hasattr(shell, 'nodes'):
        for node_data in shell.nodes.values():
            node_type = node_data.get("type", "Unknown")
            node_types[node_type] = node_types.get(node_type, 0) + 1
    
    print(f"Total Semantic Nodes: {total_nodes}")
    print(f"Total Numerical Coordinates: {total_nav_coords}")
    print(f"Total Zone Roots: {len(zone_roots)}")
    print(f"Node Types: {dict(node_types)}")
    print(f"Zone Roots: {list(zone_roots)}")
    
    # Section 2: Tree 0 (by node type)
    print("\n" + "="*60)
    print("TREE 0 - SEMANTIC FOREST (BY TYPE)")
    print("="*60)
    
    for node_type, count in node_types.items():
        print(f"\n{node_type} nodes ({count}):")
        type_nodes = [(nid, ndata) for nid, ndata in shell.nodes.items() 
                     if ndata.get("type") == node_type]
        for i, (node_id, node_data) in enumerate(type_nodes[:10]):  # First 10 of each type
            title = node_data.get("title", node_id)
            print(f"  - {node_id}: {title}")
        if len(type_nodes) > 10:
            print(f"  ... and {len(type_nodes) - 10} more")
    
    # Section 3: Navigation Tree (sample coordinates)
    print("\n" + "="*60)
    print("NAV TREE - NUMERICAL COORDINATES (SAMPLE)")
    print("="*60)
    
    if hasattr(shell, 'combo_nodes'):
        numerical_coords = [(coord, data) for coord, data in shell.combo_nodes.items() 
                           if coord.replace('.', '').replace('-', '').isdigit()]
        
        print(f"Sample numerical coordinates (showing 20 of {len(numerical_coords)}):")
        for coord, node_data in numerical_coords[:20]:
            title = node_data.get("title", node_data.get("prompt", coord))
            print(f"  {coord}: {title}")
        
        if len(numerical_coords) > 20:
            print(f"  ... and {len(numerical_coords) - 20} more coordinates")
    
    # Section 4: Zone Structure
    print("\n" + "="*60)
    print("ZONE/REALM DIGRAPH STRUCTURE")
    print("="*60)
    
    for zone_root in zone_roots:
        print(f"\n{zone_root.title()} Realm:")
        zone_nodes = []
        if hasattr(shell, 'nodes'):
            for node_id, node_data in shell.nodes.items():
                if zone_root.lower() in node_id.lower():
                    zone_nodes.append((node_id, node_data.get("title", node_id)))
        
        for node_id, title in zone_nodes[:5]:  # First 5 nodes per zone
            print(f"  - {node_id}: {title}")
        if len(zone_nodes) > 5:
            print(f"  ... and {len(zone_nodes) - 5} more nodes")
    
    print("\n" + "="*60)
    print("3D ADDRESS SPACE: Tree 0 → Nav → Zone/Realm")
    print("="*60)
    
    # Use whatever function exists
    print("\n```mermaid")
    print("graph TD")
    print("    subgraph Tree0 [\"🌲 Tree 0 (Semantic Forest)\"]")
    for i, (family_name, family_data) in enumerate(list(shell.families.items())[:3]):
        print(f"        {family_name}[{family_name}]")
        nodes = family_data.get('nodes', {})
        for j, (node_id, node_data) in enumerate(list(nodes.items())[:2]):
            title = node_data.get('title', node_id)
            print(f"        {node_id}[\"{title}\"]")
            print(f"        {family_name} --> {node_id}")
    print("    end")
    print("    subgraph NavTree [\"🔢 Nav Tree\"]")
    if hasattr(shell, 'combo_nodes'):
        coords = [(c, shell.combo_nodes[c]) for c in shell.combo_nodes.keys() if c.replace('.','').isdigit()]
        coords.sort(key=lambda x: [int(p) for p in x[0].split('.')])
        for coord, data in coords[:10]:
            title = data.get('title', data.get('prompt', coord))
            clean_coord = coord.replace('.','_').replace('-','_')
            print(f"        N{clean_coord}[\"{coord}: {title[:20]}\"]")
            # Show parent-child relationships
            parts = coord.split('.')
            if len(parts) > 1:
                parent_coord = '.'.join(parts[:-1])
                parent_clean = parent_coord.replace('.','_').replace('-','_')
                print(f"        N{parent_clean} --> N{clean_coord}")
    print("    end")
    print("    subgraph Zones [\"🏛️ Zones\"]")
    print("        SystemZone[System]")
    print("        AgentZone[Agent]")
    print("    end")
    print("    Tree0 --> NavTree")
    print("    NavTree --> Zones")
    print("```")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()