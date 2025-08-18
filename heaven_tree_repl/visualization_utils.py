#!/usr/bin/env python3
"""
Visualization utilities for TreeShell mathematical objects.

Generates mermaid diagrams for:
- Tree family structures
- Navigation coordinate mappings
- Zone relationships
- 3D address space visualization
"""

import json
from typing import Dict, List, Set, Optional, Any
from pathlib import Path
from .logger import debug, info


def generate_complete_tree_mermaid(combo_nodes: Dict[str, Any]) -> str:
    """
    Generate mermaid diagram showing THE COMPLETE node structure from combo_nodes.
    
    Args:
        combo_nodes: The actual combo_nodes dict from TreeShell instance
        
    Returns:
        Mermaid diagram showing ALL nodes and relationships
    """
    lines = ["graph TD"]
    
    # Process ALL nodes from combo_nodes - this is the COMPLETE structure
    for coord, node_data in combo_nodes.items():
        title = node_data.get("title", node_data.get("prompt", coord))
        node_type = node_data.get("type", "Unknown")
        
        # Clean up title for display
        if isinstance(title, list):
            title = str(title[0]) if title else coord
        title_clean = str(title).replace('"', "'")[:30]  # Limit length
        
        # Create styled node based on type and coordinate format
        if node_type == "Menu":
            lines.append(f'    {coord}(("{coord}<br/>{title_clean}"))')
        elif node_type == "Action":
            lines.append(f'    {coord}["{coord}<br/>{title_clean}"]')
        elif node_type == "Agent":
            lines.append(f'    {coord}{{{{🤖 {coord}<br/>{title_clean}}}}}')
        else:
            lines.append(f'    {coord}["{coord}<br/>{title_clean}"]')
        
        # Add parent relationships if they exist
        parent = node_data.get("parent")
        if parent and parent in combo_nodes:
            lines.append(f"    {parent} --> {coord}")
        
        # For hierarchical coordinates, connect to parent coordinate
        if "." in coord:
            parent_coord = ".".join(coord.split(".")[:-1])
            if parent_coord and parent_coord in combo_nodes:
                lines.append(f"    {parent_coord} --> {coord}")
    
    return "\n".join(lines)


def generate_navigation_flow_mermaid(nav_config: Dict[str, Any], families_data: Dict[str, Any]) -> str:
    """
    Generate mermaid diagram showing navigation coordinate mappings.
    
    Args:
        nav_config: Navigation configuration
        families_data: Family configurations
        
    Returns:
        Mermaid diagram showing coordinate flows
    """
    lines = ["graph LR"]
    
    family_mappings = nav_config.get("family_mappings", {})
    
    for family_name, nav_data in family_mappings.items():
        family_coord = nav_data.get("coordinate", "0")
        
        # Family entry point
        lines.append(f"    F{family_coord}[📁 {family_name}]")
        
        # Get nodes from family data
        if family_name in families_data:
            family_nodes = families_data[family_name].get("nodes", {})
            
            for node_id, node_data in family_nodes.items():
                # Generate coordinate for this node (simplified)
                node_coord = f"{family_coord}.{len(family_nodes)}"
                node_title = node_data.get("title", node_id)
                
                lines.append(f"    N{node_coord}[{node_title}]")
                lines.append(f"    F{family_coord} --> N{node_coord}")
    
    return "\n".join(lines)


def generate_zone_relationship_mermaid(zone_configs: Dict[str, Any]) -> str:
    """
    Generate mermaid diagram showing zone relationships and permissions.
    
    Args:
        zone_configs: Zone configuration data
        
    Returns:
        Mermaid diagram showing zone structure
    """
    lines = ["graph TB"]
    
    # Extract zones from configs
    zones = set()
    relationships = []
    
    for config_name, config_data in zone_configs.items():
        zone_name = config_data.get("zone", "default")
        zones.add(zone_name)
        
        # Add zone styling based on type
        if "agent" in config_name:
            lines.append(f"    {zone_name}{{{{🤖 {zone_name.title()} Zone}}}}")
        elif "user" in config_name:
            lines.append(f"    {zone_name}[👤 {zone_name.title()} Zone]")
        else:
            lines.append(f"    {zone_name}({zone_name.title()} Zone)")
        
        # Add permissions and capabilities
        permissions = config_data.get("permissions", {})
        if permissions:
            perm_node = f"{zone_name}_perms"
            lines.append(f"    {perm_node}[Permissions]")
            lines.append(f"    {zone_name} --> {perm_node}")
    
    return "\n".join(lines)


def generate_full_treeshell_structure_mermaid(treeshell_instance) -> str:
    """
    Generate the 3D mathematical structure: ROOT 0 with three sibling dimensions.
    
    ROOT 0
    ├── Tree 0 (semantic)
    ├── Nav (numerical) 
    └── Zone (meaning-based)
    """
    lines = ["graph TD"]
    
    # ROOT 0
    lines.append("    Root0((\"ROOT 0<br/>3D Address Space\"))")
    lines.append("")
    
    # Get actual data
    nodes = getattr(treeshell_instance, 'nodes', {})
    combo_nodes = getattr(treeshell_instance, 'combo_nodes', {})
    zone_config = getattr(treeshell_instance, 'zone_config', {})
    
    # DIMENSION 1: Tree 0 - Semantic Forest
    lines.append("    subgraph Tree0[\"🌲 TREE 0 - Semantic Forest\"]")
    lines.append("        direction TB")
    lines.append("        Tree0Root[\"Families (Semantic Labels)\"]")
    
    # Show actual semantic nodes by type
    node_types = {}
    for node_id, node_data in nodes.items():
        node_type = node_data.get("type", "Unknown")
        if node_type not in node_types:
            node_types[node_type] = []
        node_types[node_type].append((node_id, node_data))
    
    # Show ALL nodes of ALL types
    for node_type, nodes_of_type in node_types.items():  # ALL types
        for node_id, node_data in nodes_of_type:  # ALL nodes
            title = node_data.get("title", node_id)[:25]  # Truncate
            if node_type == "Menu":
                lines.append(f"        {node_id}_sem({title})")
            elif node_type == "Action":
                lines.append(f"        {node_id}_sem[{title}]")
            elif node_type == "Agent":
                lines.append(f"        {node_id}_sem{{{{{title}}}}}")
            else:
                lines.append(f"        {node_id}_sem[\"{title}\"]")
            
            lines.append(f"        Tree0Root --> {node_id}_sem")
    
    lines.append("    end")
    lines.append("")
    
    # DIMENSION 2: Nav - Numerical Tree
    lines.append("    subgraph NavTree[\"🔢 NAV - Numerical Tree\"]")
    lines.append("        direction TB")
    lines.append("        NavRoot[\"Filtered Coordinates\"]")
    
    # Show numerical coordinates
    numerical_coords = [(coord, data) for coord, data in combo_nodes.items() 
                       if coord.replace('.', '').replace('-', '').isdigit()]
    
    for coord, node_data in numerical_coords:  # ALL coordinates
        title = node_data.get("title", node_data.get("prompt", coord))[:20]
        coord_clean = coord.replace('.', '_').replace('-', '_')
        lines.append(f"        N{coord_clean}[\"{coord}<br/>{title}\"]")
        lines.append(f"        NavRoot --> N{coord_clean}")
    
    lines.append("    end")
    lines.append("")
    
    # DIMENSION 3: Zone - Meaning-based Digraph
    lines.append("    subgraph ZoneRealm[\"🏛️ ZONE - Realm Digraph\"]")
    lines.append("        direction TB")
    lines.append("        ZoneRoot[\"Grouped by Meaning\"]")
    
    # Show actual zones
    zones = set()
    for config_data in zone_config.values():
        zone = config_data.get("zone", "default")
        zones.add(zone)
    
    for zone in zones:  # ALL zones
        zone_clean = zone.replace('-', '_')
        lines.append(f"        Zone_{zone_clean}{{{{{zone.title()} Realm}}}}")
        lines.append(f"        ZoneRoot --> Zone_{zone_clean}")
    
    # Show zone relationships (digraph nature)
    zone_list = list(zones)
    for i in range(len(zone_list) - 1):
        zone1 = zone_list[i].replace('-', '_')
        zone2 = zone_list[i + 1].replace('-', '_')
        lines.append(f"        Zone_{zone1} -.-> Zone_{zone2}")
    
    lines.append("    end")
    lines.append("")
    
    # CONNECT ROOT 0 TO THREE DIMENSIONS
    lines.append("    Root0 --> Tree0")
    lines.append("    Root0 --> NavTree") 
    lines.append("    Root0 --> ZoneRealm")
    lines.append("")
    
    # MATHEMATICAL RELATIONSHIPS BETWEEN DIMENSIONS
    lines.append("    Tree0 -.->|\"nav_config filter\"| NavTree")
    lines.append("    Tree0 -.->|\"grouped by meaning\"| ZoneRealm")
    lines.append("    NavTree -.->|\"grouped by meaning\"| ZoneRealm")
    
    # Styling
    lines.append("")
    lines.append("    classDef root fill:#ffeb3b,stroke:#f57f17,stroke-width:4px")
    lines.append("    classDef tree0 fill:#e1f5fe,stroke:#01579b,stroke-width:2px")
    lines.append("    classDef nav fill:#fff3e0,stroke:#e65100,stroke-width:2px")
    lines.append("    classDef zone fill:#f3e5f5,stroke:#4a148c,stroke-width:2px")
    lines.append("    class Root0 root")
    lines.append("    class Tree0 tree0")
    lines.append("    class NavTree nav")
    lines.append("    class ZoneRealm zone")
    
    return "\n".join(lines)


# Function removed - using the earlier definition above


def print_tree_structure(base_path: str, output_file: Optional[str] = None) -> str:
    """
    Generate complete tree structure visualization from config files.
    
    Args:
        base_path: Path to heaven-tree-repl directory
        output_file: Optional file to write mermaid diagram to
        
    Returns:
        Complete mermaid diagram
    """
    base_path = Path(base_path)
    configs_dir = base_path / "configs"
    
    # Load all family configs
    families_data = {}
    families_dir = configs_dir / "families"
    
    if families_dir.exists():
        for family_file in families_dir.glob("*_family.json"):
            try:
                with open(family_file, 'r') as f:
                    family_data = json.load(f)
                    family_name = family_file.stem.replace("_family", "")
                    families_data[family_name] = family_data
            except Exception as e:
                debug(f"Error loading family {family_file}: {e}")
    
    # Load nav config
    nav_config = {}
    nav_config_file = configs_dir / "nav_config.json"
    if nav_config_file.exists():
        try:
            with open(nav_config_file, 'r') as f:
                nav_config = json.load(f)
        except Exception as e:
            debug(f"Error loading nav config: {e}")
    
    # Generate comprehensive diagram
    sections = [
        "# TreeShell Structure Visualization",
        "",
        "## Family Tree Structure",
        "```mermaid",
        generate_family_tree_mermaid(families_data),
        "```",
        "",
        "## Navigation Flow",
        "```mermaid", 
        generate_navigation_flow_mermaid(nav_config, families_data),
        "```",
        "",
        "## 3D Address Space",
        "```mermaid",
        generate_3d_address_space_mermaid(families_data, nav_config),
        "```"
    ]
    
    complete_diagram = "\n".join(sections)
    
    # ALWAYS PRINT the mermaid code
    print(complete_diagram)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(complete_diagram)
        info(f"Tree structure diagram written to {output_file}")
    
    return complete_diagram


def print_node_statistics(families_data: Dict[str, Any]) -> str:
    """
    Generate statistics about the tree structure.
    
    Args:
        families_data: Family configuration data
        
    Returns:
        Formatted statistics string
    """
    total_families = len(families_data)
    total_nodes = 0
    node_types = {}
    
    for family_name, family_config in families_data.items():
        family_nodes = family_config.get("nodes", {})
        total_nodes += len(family_nodes)
        
        for node_id, node_data in family_nodes.items():
            node_type = node_data.get("type", "Unknown")
            node_types[node_type] = node_types.get(node_type, 0) + 1
    
    stats = [
        "# TreeShell Statistics",
        f"- **Total Families**: {total_families}",
        f"- **Total Nodes**: {total_nodes}",
        "",
        "## Node Type Distribution",
    ]
    
    for node_type, count in sorted(node_types.items()):
        stats.append(f"- **{node_type}**: {count}")
    
    return "\n".join(stats)


# Convenience function for shell integration
def visualize_tree(base_path: str = "/home/GOD/heaven-tree-repl") -> None:
    """
    Print ONLY mermaid diagrams to console.
    
    Args:
        base_path: Path to heaven-tree-repl directory
    """
    try:
        # Load data
        base_path_obj = Path(base_path)
        configs_dir = base_path_obj / "configs"
        
        families_data = {}
        families_dir = configs_dir / "families"
        if families_dir.exists():
            for family_file in families_dir.glob("*_family.json"):
                try:
                    with open(family_file, 'r') as f:
                        family_data = json.load(f)
                        family_name = family_file.stem.replace("_family", "")
                        families_data[family_name] = family_data
                except Exception:
                    pass
        
        nav_config = {}
        nav_config_file = configs_dir / "nav_config.json"
        if nav_config_file.exists():
            try:
                with open(nav_config_file, 'r') as f:
                    nav_config = json.load(f)
            except Exception:
                pass
        
        # Print ONLY the 3D address space mermaid
        print("```mermaid")
        print(generate_3d_address_space_mermaid(families_data, nav_config))
        print("```")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Demo usage
    visualize_tree()