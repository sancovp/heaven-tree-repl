#!/usr/bin/env python3
"""
System Config Loader for HEAVEN TreeShell 17-Config Architecture

Loads all 17 system configs from library package and applies user customizations.
Implements the override/add/exclude pattern for all config types.
"""

import os
import json
from typing import Dict, List, Any, Optional


class SystemConfigLoader:
    """
    Loads all 17 system configurations from library package and applies user customizations.
    
    System configs are always loaded fresh from the library package to enable
    automatic updates. User configs are loaded from user_config_path and applied
    using the override/add/exclude pattern.
    """
    
    def __init__(self, config_types: List[str]):
        """
        Initialize config loader for specified config types.
        
        Args:
            config_types: List of config types to load (e.g., ["base", "agent"])
        """
        self.config_types = config_types
        self.library_configs_dir = self._get_library_configs_dir()
        self.library_shortcuts_dir = self._get_library_shortcuts_dir()
        
        # System config paths (hardcoded, always loaded from library)
        self.system_base_config = "base_default_config_v2.json"
        self.system_agent_config = "agent_default_config_v2.json" 
        self.system_user_config = "user_default_config_v2.json"
        
        # System shortcut paths
        self.system_base_shortcuts = "base_shortcuts.json"
        self.system_agent_shortcuts = "system_agent_shortcuts.json"
        self.system_user_shortcuts = "system_user_shortcuts.json"
        
        # System zone config paths
        self.system_agent_zone_config = "agent_zone_config.json"
        self.system_user_zone_config = "user_zone_config.json"
        
        # User config filenames (loaded from user_config_path if provided)
        self.user_base_config = "user_base_config.json"
        self.user_agent_config = "user_agent_config.json"
        self.user_user_config = "user_user_config.json"
        
        # User shortcut filenames
        self.user_base_shortcuts = "user_base_shortcuts.json"
        self.user_agent_shortcuts = "user_agent_shortcuts.json" 
        self.user_user_shortcuts = "user_user_shortcuts.json"
        
        # User zone config filenames
        self.user_agent_zone_config = "user_agent_zone_config.json"
        self.user_user_zone_config = "user_user_zone_config.json"
        
        # Navigation config (user controlled only)
        self.nav_config = "nav_config.json"
    
    def _get_library_configs_dir(self) -> str:
        """Get the library configs directory path."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(os.path.dirname(current_dir), "configs")
    
    def _get_library_shortcuts_dir(self) -> str:
        """Get the library shortcuts directory path.""" 
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(os.path.dirname(current_dir), "shortcuts")
    
    def _load_system_config_by_type(self, config_type: str) -> Dict[str, Any]:
        """Load a system config by type (base, agent, user)."""
        if config_type == "base":
            filename = self.system_base_config
        elif config_type == "agent":
            filename = self.system_agent_config
        elif config_type == "user":
            filename = self.system_user_config
        else:
            print(f"Unknown config type: {config_type}")
            return {}
            
        file_path = os.path.join(self.library_configs_dir, filename)
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            else:
                print(f"Warning: System config not found: {file_path}")
                return {}
        except Exception as e:
            print(f"Error loading system config {filename}: {e}")
            return {}
    
    def _load_user_config_by_type(self, config_type: str, user_config_path: str = None) -> Dict[str, Any]:
        """Load user config by type from user_config_path."""
        if config_type == "base":
            filename = self.user_base_config
        elif config_type == "agent":
            filename = self.user_agent_config
        elif config_type == "user":
            filename = self.user_user_config
        else:
            return {}
            
        if not user_config_path:
            return {}
            
        file_path = os.path.join(user_config_path, filename)
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            else:
                return {}  # User config doesn't exist - this is normal
        except Exception as e:
            print(f"Error loading user config {filename}: {e}")
            return {}
    
    def _load_system_shortcuts_by_type(self, config_type: str) -> Dict[str, Any]:
        """Load system shortcuts by type."""
        if config_type == "base":
            filename = self.system_base_shortcuts
        elif config_type == "agent":
            filename = self.system_agent_shortcuts
        elif config_type == "user":
            filename = self.system_user_shortcuts
        else:
            return {}
            
        file_path = os.path.join(self.library_shortcuts_dir, filename)
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            print(f"Error loading system shortcuts {filename}: {e}")
            return {}
    
    def _load_user_shortcuts_by_type(self, config_type: str, user_config_path: str = None) -> Dict[str, Any]:
        """Load user shortcuts by type from user_config_path."""
        if config_type == "base":
            filename = self.user_base_shortcuts
        elif config_type == "agent":
            filename = self.user_agent_shortcuts
        elif config_type == "user":
            filename = self.user_user_shortcuts
        else:
            return {}
            
        if not user_config_path:
            return {}
            
        file_path = os.path.join(user_config_path, filename)
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            print(f"Error loading user shortcuts {filename}: {e}")
            return {}
    
    def _load_system_zone_config_by_type(self, config_type: str) -> Dict[str, Any]:
        """Load system zone config by type."""
        if config_type == "agent":
            filename = self.system_agent_zone_config
        elif config_type == "user":
            filename = self.system_user_zone_config
        else:
            return {}
            
        file_path = os.path.join(self.library_configs_dir, filename)
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            print(f"Error loading system zone config {filename}: {e}")
            return {}
    
    def _load_user_zone_config_by_type(self, config_type: str, user_config_path: str = None) -> Dict[str, Any]:
        """Load user zone config by type from user_config_path."""
        if config_type == "agent":
            filename = self.user_agent_zone_config
        elif config_type == "user":
            filename = self.user_user_zone_config
        else:
            return {}
            
        if not user_config_path:
            return {}
            
        file_path = os.path.join(user_config_path, filename)
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            print(f"Error loading user zone config {filename}: {e}")
            return {}
    
    def _apply_user_customizations(self, system_config: Dict[str, Any], user_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply user customizations using override/add/exclude pattern."""
        if not user_config:
            return system_config
        
        final_config = system_config.copy()
        
        # Apply overrides
        if "override_nodes" in user_config:
            if "nodes" not in final_config:
                final_config["nodes"] = {}
            
            for node_id, node_overrides in user_config["override_nodes"].items():
                if node_id in final_config["nodes"]:
                    # Merge overrides into existing node
                    final_config["nodes"][node_id].update(node_overrides)
        
        # Add new nodes
        if "add_nodes" in user_config:
            if "nodes" not in final_config:
                final_config["nodes"] = {}
            
            for node_id, node_data in user_config["add_nodes"].items():
                final_config["nodes"][node_id] = node_data
        
        # Exclude nodes
        if "exclude_nodes" in user_config:
            if "nodes" in final_config:
                for node_id in user_config["exclude_nodes"]:
                    final_config["nodes"].pop(node_id, None)
        
        # Apply other config overrides (non-node fields)
        for key, value in user_config.items():
            if key not in ["override_nodes", "add_nodes", "exclude_nodes"]:
                final_config[key] = value
        
        return final_config
    
    def load_configs(self, user_config_path: str = None) -> Dict[str, Any]:
        """
        Load and merge system and user configs for all specified config types.
        
        Args:
            user_config_path: Optional path to user configs directory
            
        Returns:
            Merged configuration with user customizations applied
        """
        final_config = {}
        
        # Load and merge each config type
        for config_type in self.config_types:
            # Always load system config fresh from library
            system_config = self._load_system_config_by_type(config_type)
            
            # Load user config if it exists
            user_config = self._load_user_config_by_type(config_type, user_config_path)
            
            # Apply user customizations
            merged_config = self._apply_user_customizations(system_config, user_config)
            
            # Merge into final config
            if "nodes" in merged_config:
                if "nodes" not in final_config:
                    final_config["nodes"] = {}
                final_config["nodes"].update(merged_config["nodes"])
            
            # Merge other fields (non-nodes)
            for key, value in merged_config.items():
                if key != "nodes":
                    final_config[key] = value
        
        return final_config
    
    def load_shortcuts(self, user_config_path: str = None) -> Dict[str, Any]:
        """
        Load and merge shortcuts for all specified config types.
        
        Args:
            user_config_path: Optional path to user configs directory
            
        Returns:
            Merged shortcuts configuration
        """
        shortcuts = {}
        
        # Load shortcuts for each config type
        for config_type in self.config_types:
            # Load system shortcuts
            system_shortcuts = self._load_system_shortcuts_by_type(config_type)
            if system_shortcuts:
                shortcuts.update(system_shortcuts)
            
            # Load user shortcuts if they exist
            user_shortcuts = self._load_user_shortcuts_by_type(config_type, user_config_path)
            if user_shortcuts:
                shortcuts.update(user_shortcuts)
        
        return shortcuts
    
    def load_zone_configs(self, user_config_path: str = None) -> Dict[str, Any]:
        """
        Load and merge zone configs for all specified config types.
        
        Args:
            user_config_path: Optional path to user configs directory
            
        Returns:
            Merged zone configurations
        """
        zone_configs = {}
        
        # Load zone configs for each config type (only agent and user have zones)
        for config_type in self.config_types:
            if config_type in ["agent", "user"]:
                # Load system zone config
                system_zone = self._load_system_zone_config_by_type(config_type)
                
                # Load user zone config if it exists
                user_zone = self._load_user_zone_config_by_type(config_type, user_config_path)
                
                # Apply user customizations and merge
                merged_zone = self._apply_user_customizations(system_zone, user_zone)
                
                # Merge into final zone configs
                for key, value in merged_zone.items():
                    zone_configs[key] = value
        
        return zone_configs