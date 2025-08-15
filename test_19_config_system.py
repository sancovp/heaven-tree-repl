#!/usr/bin/env python3
"""
Test script for the 19-config system with Pydantic validation.
"""

import os
import sys
import json
from pathlib import Path

# Add the heaven_tree_repl module to the path
sys.path.insert(0, '/home/GOD/heaven-tree-repl')

from heaven_tree_repl.system_config_loader_v2 import SystemConfigLoader
from heaven_tree_repl.config_models import *


def test_pydantic_models():
    """Test that all Pydantic models can be instantiated."""
    print("Testing Pydantic models...")
    
    # Test system config models
    try:
        system_base = SystemBaseConfig(
            app_id="test_app",
            domain="test_domain", 
            role="test_role"
        )
        print("✓ SystemBaseConfig validation works")
    except Exception as e:
        print(f"✗ SystemBaseConfig validation failed: {e}")
    
    # Test dev config models
    try:
        dev_base = DevBaseConfig()
        print("✓ DevBaseConfig validation works")
    except Exception as e:
        print(f"✗ DevBaseConfig validation failed: {e}")
    
    # Test nav config
    try:
        nav = NavConfig(nav_tree_order=["system", "agent_management"])
        print("✓ NavConfig validation works")
    except Exception as e:
        print(f"✗ NavConfig validation failed: {e}")
    
    print()


def test_system_config_loader():
    """Test the SystemConfigLoader with different config types."""
    print("Testing SystemConfigLoader...")
    
    # Test base config loading
    try:
        loader = SystemConfigLoader(config_types=["base"])
        configs = loader.load_and_validate_configs()
        
        if configs:
            print("✓ Base config loading works")
            print(f"  App ID: {configs.get('app_id', 'NOT FOUND')}")
            print(f"  Domain: {configs.get('domain', 'NOT FOUND')}")
            print(f"  Role: {configs.get('role', 'NOT FOUND')}")
        else:
            print("✗ Base config loading returned empty")
        
        warnings = loader.get_validation_warnings()
        if warnings:
            print(f"  Validation warnings: {len(warnings)}")
            for warning in warnings[:3]:  # Show first 3
                print(f"    - {warning}")
    except Exception as e:
        print(f"✗ Base config loading failed: {e}")
    
    # Test agent config loading
    try:
        loader = SystemConfigLoader(config_types=["base", "agent"])
        configs = loader.load_and_validate_configs()
        
        if configs:
            print("✓ Base + Agent config loading works")
            print(f"  Families: {configs.get('families', 'NOT FOUND')}")
        
        warnings = loader.get_validation_warnings()
        if warnings:
            print(f"  Validation warnings: {len(warnings)}")
    except Exception as e:
        print(f"✗ Base + Agent config loading failed: {e}")
    
    print()


def test_family_loading():
    """Test family loading and validation."""
    print("Testing family loading...")
    
    try:
        loader = SystemConfigLoader(config_types=["base"])
        families = loader.load_families(["system", "agent_management"])
        
        if families:
            print(f"✓ Family loading works - loaded {len(families)} families")
            for family_name, family_data in families.items():
                nodes_count = len(family_data.get('nodes', {}))
                print(f"  {family_name}: {nodes_count} nodes")
        else:
            print("✗ Family loading returned empty")
        
        warnings = loader.get_validation_warnings()
        if warnings:
            print(f"  Family validation warnings: {len(warnings)}")
            for warning in warnings[:3]:  # Show first 3
                print(f"    - {warning}")
    except Exception as e:
        print(f"✗ Family loading failed: {e}")
    
    print()


def test_nav_config_loading():
    """Test navigation config loading."""
    print("Testing nav config loading...")
    
    try:
        loader = SystemConfigLoader(config_types=["base"])
        nav_config = loader.load_nav_config()
        
        if nav_config:
            print("✓ Nav config loading works")
            print(f"  Nav tree order: {nav_config.get('nav_tree_order', 'NOT FOUND')}")
            print(f"  Coordinate mapping: {nav_config.get('coordinate_mapping', 'NOT FOUND')}")
        else:
            print("✗ Nav config loading returned empty")
        
        warnings = loader.get_validation_warnings()
        if warnings:
            print(f"  Nav validation warnings: {len(warnings)}")
    except Exception as e:
        print(f"✗ Nav config loading failed: {e}")
    
    print()


def test_shell_initialization():
    """Test shell initialization with new config system."""
    print("Testing shell initialization...")
    
    try:
        from heaven_tree_repl.shells import TreeShell
        
        # Test basic shell creation
        shell = TreeShell(graph_config={
            "app_id": "test_shell",
            "domain": "test_domain",
            "role": "test_role"
        })
        
        print("✓ TreeShell initialization works")
        print(f"  App ID: {shell.app_id}")
        print(f"  Domain: {shell.domain}")
        print(f"  Role: {shell.role}")
        print(f"  Nodes loaded: {len(shell.nodes)}")
        
    except Exception as e:
        print(f"✗ TreeShell initialization failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()


def main():
    """Run all tests."""
    print("=" * 50)
    print("TESTING 19-CONFIG SYSTEM WITH PYDANTIC VALIDATION")
    print("=" * 50)
    print()
    
    test_pydantic_models()
    test_system_config_loader()
    test_family_loading()
    test_nav_config_loading()
    test_shell_initialization()
    
    print("=" * 50)
    print("TESTING COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    main()