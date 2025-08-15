#!/usr/bin/env python3
"""
Test script for file-path-based semantic addressing in the 19-config system.
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add the heaven_tree_repl module to the path
sys.path.insert(0, '/home/GOD/heaven-tree-repl')

from heaven_tree_repl.system_config_loader_v2 import SystemConfigLoader


def create_test_dev_config():
    """Create a temporary dev config directory with semantic addressing examples."""
    temp_dir = tempfile.mkdtemp()
    
    # Create dev config with file-path-based semantic addressing
    dev_base_config = {
        "override_nodes": {
            "configs/families/system_family.json:system": {
                "prompt": "OVERRIDDEN: My Custom System Menu",
                "description": "This prompt was overridden by dev config"
            }
        },
        "add_nodes": {
            "configs/families/system_family.json:my_custom_tool": {
                "type": "Callable",
                "prompt": "My Custom Tool",
                "description": "A tool I added via dev config",
                "function_name": "my_custom_function"
            }
        },
        "exclude_nodes": [
            "configs/families/agent_management_family.json:sessions"
        ]
    }
    
    # Save dev config
    with open(os.path.join(temp_dir, "dev_base_config.json"), 'w') as f:
        json.dump(dev_base_config, f, indent=2)
    
    return temp_dir


def test_semantic_addressing():
    """Test the complete file-path-based semantic addressing system."""
    print("Testing file-path-based semantic addressing...")
    
    # Create temporary dev config
    temp_dev_dir = create_test_dev_config()
    
    try:
        # Test config loader with dev customizations
        loader = SystemConfigLoader(config_types=["base"])
        
        # Load families with dev customizations applied
        families = loader.load_families(["system", "agent_management"], temp_dev_dir)
        
        if families:
            print(f"✓ Loaded {len(families)} families with dev customizations")
            
            # Check if override worked
            if "system" in families:
                system_family = families["system"]
                system_nodes = system_family.get("nodes", {})
                
                if "system" in system_nodes:
                    system_node = system_nodes["system"]
                    if "OVERRIDDEN" in system_node.get("prompt", ""):
                        print("✓ Override worked: system node prompt was customized")
                    else:
                        print(f"✗ Override failed: system node prompt = '{system_node.get('prompt')}'")
                
                # Check if addition worked
                if "my_custom_tool" in system_nodes:
                    custom_tool = system_nodes["my_custom_tool"]
                    print("✓ Add worked: custom tool was added")
                    print(f"  Custom tool prompt: {custom_tool.get('prompt')}")
                else:
                    print("✗ Add failed: custom tool not found")
            
            # Check if exclusion worked
            if "agent_management" in families:
                agent_family = families["agent_management"]
                agent_nodes = agent_family.get("nodes", {})
                
                if "sessions" not in agent_nodes:
                    print("✓ Exclude worked: sessions node was removed")
                else:
                    print("✗ Exclude failed: sessions node still exists")
        
        # Check validation warnings
        warnings = loader.get_validation_warnings()
        if warnings:
            print(f"\nValidation warnings ({len(warnings)}):")
            for warning in warnings:
                print(f"  - {warning}")
        else:
            print("\n✓ No validation warnings")
        
    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dev_dir)
    
    print()


def test_semantic_address_parsing():
    """Test the semantic address parsing logic."""
    print("Testing semantic address parsing...")
    
    loader = SystemConfigLoader(config_types=["base"])
    
    # Test valid addresses
    test_cases = [
        ("configs/families/system_family.json:system_meta", "configs/families/system_family.json", "system_meta"),
        ("my_custom/path.json:my_node", "my_custom/path.json", "my_node"),
        ("relative/path/file.json:node.with.dots", "relative/path/file.json", "node.with.dots")
    ]
    
    for full_address, expected_file, expected_node in test_cases:
        try:
            file_path, node_id = loader._parse_semantic_address(full_address)
            if file_path == expected_file and node_id == expected_node:
                print(f"✓ Parsed '{full_address}' correctly")
            else:
                print(f"✗ Parse error: got ({file_path}, {node_id}), expected ({expected_file}, {expected_node})")
        except Exception as e:
            print(f"✗ Parse failed for '{full_address}': {e}")
    
    # Test invalid addresses
    invalid_cases = [
        "no_colon_separator",
        "configs/file.json",  # Missing colon
        ":just_node_id"       # Missing file path
    ]
    
    for invalid_address in invalid_cases:
        try:
            loader._parse_semantic_address(invalid_address)
            print(f"✗ Should have failed: '{invalid_address}'")
        except ValueError:
            print(f"✓ Correctly rejected invalid address: '{invalid_address}'")
        except Exception as e:
            print(f"✗ Wrong error type for '{invalid_address}': {e}")
    
    print()


def test_file_matching():
    """Test the file path matching logic."""
    print("Testing file path matching...")
    
    loader = SystemConfigLoader(config_types=["base"])
    
    # Test file matching cases
    test_cases = [
        ("configs/families/system_family.json", "/home/GOD/heaven-tree-repl/configs/families/system_family.json", True),
        ("system_family.json", "/home/GOD/heaven-tree-repl/configs/families/system_family.json", True),
        ("configs/families/system_family.json", "/home/GOD/heaven-tree-repl/configs/families/agent_management_family.json", False),
        ("different_file.json", "/home/GOD/heaven-tree-repl/configs/families/system_family.json", False)
    ]
    
    for target_file, actual_file, expected_match in test_cases:
        result = loader._file_matches(target_file, actual_file)
        if result == expected_match:
            print(f"✓ File match '{target_file}' vs '{os.path.basename(actual_file)}': {result}")
        else:
            print(f"✗ File match error: '{target_file}' vs '{os.path.basename(actual_file)}' expected {expected_match}, got {result}")
    
    print()


def main():
    """Run all semantic addressing tests."""
    print("=" * 60)
    print("TESTING FILE-PATH-BASED SEMANTIC ADDRESSING")
    print("=" * 60)
    print()
    
    test_semantic_address_parsing()
    test_file_matching()
    test_semantic_addressing()
    
    print("=" * 60)
    print("SEMANTIC ADDRESSING TESTS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()