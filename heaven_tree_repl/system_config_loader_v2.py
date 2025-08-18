#!/usr/bin/env python3
"""
Enhanced System Config Loader for TreeShell 19-Config Architecture

Loads all 19 system configurations with Pydantic validation and applies dev customizations.
Implements the override/add/exclude pattern with proper validation error collection.
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple
from pydantic import ValidationError

from .config_models import (
    SYSTEM_CONFIG_MODELS, DEV_CONFIG_MODELS, NODE_MODELS,
    NavConfig, FamilyConfig, SystemBaseShortcuts
)


class SystemConfigLoader:
    """
    Enhanced config loader with Pydantic validation for all 19 configurations.
    
    Loads system configs fresh from library and applies dev customizations
    using the override/add/exclude pattern with comprehensive validation.
    """
    
    def __init__(self, config_types: List[str]):
        """
        Initialize config loader for specified config types.
        
        Args:
            config_types: List of config types to load (e.g., ["base", "agent"])
        """
        self.config_types = config_types
        self.validation_warnings: List[str] = []
        self.library_configs_dir = self._get_library_configs_dir()
        
        # System config file mappings (always loaded from library)
        self.system_config_files = {
            "base": "system_base_config.json",
            "agent": "system_agent_config.json",
            "user": "system_user_config.json",
            "base_shortcuts": "system_base_shortcuts.json",
            "agent_shortcuts": "system_agent_shortcuts.json",
            "user_shortcuts": "system_user_shortcuts.json",
            "base_zone_config": "system_base_zone_config.json",
            "agent_zone_config": "system_agent_zone_config.json",
            "user_zone_config": "system_user_zone_config.json",
        }
        
        # Dev config file mappings (loaded from dev_config_path if provided)
        self.dev_config_files = {
            "base": "dev_base_config.json",
            "agent": "dev_agent_config.json",
            "user": "dev_user_config.json",
            "base_shortcuts": "dev_base_shortcuts.json",
            "agent_shortcuts": "dev_agent_shortcuts.json",
            "user_shortcuts": "dev_user_shortcuts.json",
            "base_zone_config": "dev_base_zone_config.json",
            "agent_zone_config": "dev_agent_zone_config.json",
            "user_zone_config": "dev_user_zone_config.json",
        }
    
    def _get_library_configs_dir(self) -> str:
        """Get the library configs directory path."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(os.path.dirname(current_dir), "configs")
    
    def _load_and_validate_system_config(self, config_type: str) -> Optional[Dict[str, Any]]:
        """Load and validate a system config with Pydantic model."""
        if config_type not in self.system_config_files:
            self.validation_warnings.append(f"Unknown system config type: {config_type}")
            return None
        
        filename = self.system_config_files[config_type]
        file_path = os.path.join(self.library_configs_dir, filename)
        
        try:
            if not os.path.exists(file_path):
                self.validation_warnings.append(f"System config file not found: {file_path}")
                return None
            
            with open(file_path, 'r') as f:
                raw_data = json.load(f)
            
            # Add path info for tracking
            raw_data['path'] = file_path
            
            # Validate with appropriate Pydantic model
            model_class = SYSTEM_CONFIG_MODELS[config_type]
            
            # Special handling for shortcuts (they can be in different formats)
            if 'shortcuts' in config_type:
                # Skip Pydantic validation for shortcuts - just use raw JSON
                return raw_data
            else:
                validated_config = model_class(**raw_data)
                return validated_config.dict()
            
        except ValidationError as e:
            self.validation_warnings.append(f"Validation error in {filename}: {e}")
            return None
        except Exception as e:
            self.validation_warnings.append(f"Error loading system config {filename}: {e}")
            return None
    
    def _load_and_validate_dev_config(self, config_type: str, dev_config_path: str = None) -> Optional[Dict[str, Any]]:
        """Load and validate a dev config with Pydantic model."""
        if not dev_config_path or config_type not in self.dev_config_files:
            return None
        
        filename = self.dev_config_files[config_type]
        file_path = os.path.join(dev_config_path, filename)
        
        try:
            if not os.path.exists(file_path):
                return None  # Dev config doesn't exist - this is normal
            
            with open(file_path, 'r') as f:
                raw_data = json.load(f)
            
            # Add path info for tracking
            raw_data['path'] = file_path
            
            # Validate with appropriate Pydantic model
            model_class = DEV_CONFIG_MODELS[config_type]
            validated_config = model_class(**raw_data)
            
            return validated_config.dict()
            
        except ValidationError as e:
            self.validation_warnings.append(f"Validation error in dev config {filename}: {e}")
            return None
        except Exception as e:
            self.validation_warnings.append(f"Error loading dev config {filename}: {e}")
            return None
    
    def _validate_shortcuts_config(self, raw_data: Dict[str, Any], model_class, filename: str) -> Any:
        """Handle special validation for shortcuts configs which can be in different formats."""
        try:
            # Try direct validation first
            return model_class(**raw_data)
        except ValidationError:
            # If direct validation fails, try converting to nested format
            if 'shortcuts' not in raw_data and any(key != 'path' for key in raw_data.keys()):
                # Convert direct format to nested format
                shortcuts = {}
                for key, value in raw_data.items():
                    if key != 'path' and isinstance(value, dict):
                        shortcuts[key] = value
                converted_data = {'shortcuts': shortcuts, 'path': raw_data.get('path')}
                return model_class(**converted_data)
            else:
                raise  # Re-raise if conversion doesn't help
    
    def _merge_configs(self, system_config: Dict[str, Any], dev_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Merge system and dev configs - main configs only contain metadata, not nodes."""
        if not dev_config:
            return system_config
        
        final_config = system_config.copy()
        
        # Apply direct field overrides (skip override/add/exclude - those are for family nodes)
        for key, value in dev_config.items():
            if key not in ["override_nodes", "add_nodes", "exclude_nodes", "path"] and value is not None:
                final_config[key] = value
        
        return final_config
    
    
    def load_and_validate_configs(self, dev_config_path: str = None) -> Dict[str, Any]:
        """
        Load, validate, and merge all configs for specified config types.
        
        Args:
            dev_config_path: Optional path to dev configs directory
            
        Returns:
            Merged configuration with dev customizations applied
        """
        final_config = {}
        
        # Load and merge each config type
        for config_type in self.config_types:
            # Load system config with validation
            system_config = self._load_and_validate_system_config(config_type)
            if not system_config:
                continue
            
            # Load dev config with validation (if exists)
            dev_config = self._load_and_validate_dev_config(config_type, dev_config_path)
            
            # Merge configs (dev overrides system)
            merged_config = self._merge_configs(system_config, dev_config)
            
            # Add to final config, merging carefully
            self._merge_into_final_config(final_config, merged_config, config_type)
        
        # Load referenced nav_config and zone_config files
        self._load_referenced_configs(final_config)
        
        return final_config
    
    def _load_referenced_configs(self, final_config: Dict[str, Any]) -> None:
        """Load nav_config and zone_config files that are referenced by filename."""
        import os
        import json
        
        # Load nav_config if it's a filename reference
        if 'nav_config' in final_config and isinstance(final_config['nav_config'], str):
            nav_config_file = final_config['nav_config']
            nav_config_path = os.path.join(self.library_configs_dir, nav_config_file)
            try:
                if os.path.exists(nav_config_path):
                    with open(nav_config_path, 'r') as f:
                        nav_config_data = json.load(f)
                        final_config['nav_config'] = nav_config_data
                else:
                    self.validation_warnings.append(f"Referenced nav config file not found: {nav_config_path}")
            except Exception as e:
                self.validation_warnings.append(f"Error loading nav config {nav_config_file}: {e}")
        
        # Load zone_config if it's a filename reference  
        if 'zone_config' in final_config and isinstance(final_config['zone_config'], str):
            zone_config_file = final_config['zone_config']
            zone_config_path = os.path.join(self.library_configs_dir, zone_config_file)
            try:
                if os.path.exists(zone_config_path):
                    with open(zone_config_path, 'r') as f:
                        zone_config_data = json.load(f)
                        # Merge zone config data into existing zones
                        if 'zones' not in final_config:
                            final_config['zones'] = {}
                        if 'zones' in zone_config_data:
                            final_config['zones'].update(zone_config_data['zones'])
                else:
                    self.validation_warnings.append(f"Referenced zone config file not found: {zone_config_path}")
            except Exception as e:
                self.validation_warnings.append(f"Error loading zone config {zone_config_file}: {e}")
    
    def _merge_into_final_config(self, final_config: Dict[str, Any], merged_config: Dict[str, Any], config_type: str) -> None:
        """Merge a config into the final config, handling different merge strategies."""
        # For shortcuts and zone configs, merge the data directly
        if 'shortcuts' in config_type:
            shortcuts = merged_config.get('shortcuts', merged_config)
            if 'shortcuts' not in final_config:
                final_config['shortcuts'] = {}
            final_config['shortcuts'].update(shortcuts)
        elif 'zone_config' in config_type:
            zones = merged_config.get('zones', {})
            if 'zones' not in final_config:
                final_config['zones'] = {}
            final_config['zones'].update(zones)
        else:
            # For main configs, merge nodes separately and overwrite other fields
            if "nodes" in merged_config:
                if "nodes" not in final_config:
                    final_config["nodes"] = {}
                final_config["nodes"].update(merged_config["nodes"])
            
            # Merge other fields (non-nodes)
            for key, value in merged_config.items():
                if key not in ["nodes", "path"]:
                    final_config[key] = value
    
    def load_families(self, dev_config_path: str = None) -> Dict[str, Any]:
        """
        Load and validate ALL families from both library and dev directories with dev customizations.
        Base TreeShell loads every single family that exists.
        
        Args:
            dev_config_path: Optional path to dev configs directory
            
        Returns:
            Dictionary of ALL validated family configurations with dev customizations applied
        """
        families = {}
        
        # Collect all dev node customizations from all dev config files
        dev_customizations = self._collect_dev_node_customizations(dev_config_path)
        
        # Load ALL system families from library package (scan entire directory)
        families_dir = os.path.join(self.library_configs_dir, "families")
        if os.path.exists(families_dir):
            for family_file in os.listdir(families_dir):
                if family_file.endswith("_family.json"):
                    family_name = family_file.replace("_family.json", "")
                    try:
                        system_family, family_file_path = self._load_system_family_with_path(family_name)
                        if system_family:
                            # Apply dev customizations to this family
                            self._apply_dev_customizations_to_family(system_family, family_file_path, dev_customizations)
                            
                            # Validate the final family (after customizations)
                            validated_family = self._validate_family(system_family, family_name)
                            if validated_family:
                                families[family_name] = validated_family
                    except Exception as e:
                        self.validation_warnings.append(f"Failed to load system family '{family_name}': {e}")
        
        # Load custom dev families from dev directory (complete family files)
        dev_families_dir = os.path.join(dev_config_path, "families") if dev_config_path else None
        if dev_families_dir and os.path.exists(dev_families_dir):
            for family_file in os.listdir(dev_families_dir):
                if family_file.endswith("_family.json"):
                    family_name = family_file.replace("_family.json", "")
                    try:
                        dev_family = self._load_dev_family(dev_families_dir, family_file)
                        if dev_family:
                            validated_family = self._validate_family(dev_family, family_name)
                            if validated_family:
                                families[family_name] = validated_family  # Dev families can override system
                    except Exception as e:
                        self.validation_warnings.append(f"Failed to load dev family '{family_name}': {e}")
        
        return families
    
    def _load_system_family(self, family_name: str) -> Optional[Dict[str, Any]]:
        """Load a system family from the library families directory."""
        families_dir = os.path.join(self.library_configs_dir, "families")
        family_file = f"{family_name}_family.json"
        family_path = os.path.join(families_dir, family_file)
        
        try:
            if os.path.exists(family_path):
                with open(family_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            self.validation_warnings.append(f"Error loading system family {family_name}: {e}")
            return None
    
    def _load_system_family_with_path(self, family_name: str) -> Tuple[Optional[Dict[str, Any]], str]:
        """Load a system family and return both data and file path."""
        families_dir = os.path.join(self.library_configs_dir, "families")
        family_file = f"{family_name}_family.json"
        family_path = os.path.join(families_dir, family_file)
        
        try:
            if os.path.exists(family_path):
                with open(family_path, 'r') as f:
                    return json.load(f), family_path
            return None, family_path
        except Exception as e:
            self.validation_warnings.append(f"Error loading system family {family_name}: {e}")
            return None, family_path
    
    def _load_dev_family(self, dev_families_dir: str, family_file: str) -> Optional[Dict[str, Any]]:
        """Load a dev family from the dev families directory."""
        family_path = os.path.join(dev_families_dir, family_file)
        
        try:
            with open(family_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.validation_warnings.append(f"Error loading dev family {family_file}: {e}")
            return None
    
    def _validate_family(self, family_data: Dict[str, Any], family_name: str) -> Optional[Dict[str, Any]]:
        """Validate family configuration and its nodes with Pydantic models."""
        try:
            # Validate the family structure
            validated_family = FamilyConfig(**family_data)
            family_dict = validated_family.dict()
            
            # Validate individual nodes and filter out bad ones
            validated_nodes = {}
            for node_id, node_data in family_dict.get("nodes", {}).items():
                try:
                    validated_node = self._validate_node(node_data, node_id, family_name)
                    if validated_node:
                        validated_nodes[node_id] = validated_node
                except Exception as e:
                    # Bad node filtered out, warning collected
                    self.validation_warnings.append(f"Invalid node '{node_id}' in family '{family_name}': {e}")
                    continue
            
            # Update family with validated nodes
            family_dict["nodes"] = validated_nodes
            return family_dict if validated_nodes else None
            
        except ValidationError as e:
            self.validation_warnings.append(f"Invalid family structure '{family_name}': {e}")
            return None
        except Exception as e:
            self.validation_warnings.append(f"Error validating family '{family_name}': {e}")
            return None
    
    def _validate_node(self, node_data: Dict[str, Any], node_id: str, family_name: str) -> Optional[Dict[str, Any]]:
        """Validate individual node with appropriate Pydantic model."""
        try:
            node_type = node_data.get("type", "Menu")
            
            if node_type in NODE_MODELS:
                model_class = NODE_MODELS[node_type]
                validated_node = model_class(**node_data)
                return validated_node.dict()
            else:
                # Unknown node type - use base model
                from .config_models import BaseNode
                validated_node = BaseNode(**node_data)
                return validated_node.dict()
        except ValidationError as e:
            self.validation_warnings.append(f"Pydantic validation failed for node '{node_id}' in family '{family_name}': {e}")
            return None
        except Exception as e:
            self.validation_warnings.append(f"Error validating node '{node_id}' in family '{family_name}': {e}")
            return None
    
    def load_nav_config(self, dev_config_path: str = None) -> Dict[str, Any]:
        """
        Load and validate navigation config.
        
        Args:
            dev_config_path: Path to dev config directory (nav config is user-controlled)
            
        Returns:
            Validated navigation configuration
        """
        # Nav config is user-controlled, so check dev path first, then fall back to library
        nav_file = "nav_config.json"
        
        # Try dev path first
        if dev_config_path:
            nav_path = os.path.join(dev_config_path, nav_file)
            if os.path.exists(nav_path):
                try:
                    with open(nav_path, 'r') as f:
                        raw_data = json.load(f)
                    raw_data['path'] = nav_path
                    validated_nav = NavConfig(**raw_data)
                    return validated_nav.dict()
                except Exception as e:
                    self.validation_warnings.append(f"Error loading dev nav config: {e}")
        
        # Fall back to library nav config
        nav_path = os.path.join(self.library_configs_dir, nav_file)
        try:
            if os.path.exists(nav_path):
                with open(nav_path, 'r') as f:
                    raw_data = json.load(f)
                raw_data['path'] = nav_path
                validated_nav = NavConfig(**raw_data)
                return validated_nav.dict()
            else:
                self.validation_warnings.append(f"Nav config not found: {nav_path}")
                return {}
        except Exception as e:
            self.validation_warnings.append(f"Error loading library nav config: {e}")
            return {}
    
    def get_validation_warnings(self) -> List[str]:
        """Get all validation warnings collected during loading."""
        return self.validation_warnings.copy()
    
    def clear_validation_warnings(self) -> None:
        """Clear all validation warnings."""
        self.validation_warnings.clear()
    
    def load_shortcuts(self, dev_config_path: str = None) -> Dict[str, Any]:
        """
        Load and merge shortcuts for the specified config types.
        
        Args:
            dev_config_path: Optional path to dev configs directory
            
        Returns:
            Merged shortcuts dictionary
        """
        shortcuts = {}
        
        # Load shortcuts for each config type by looking for corresponding shortcuts files
        for config_type in self.config_types:
            shortcuts_config_type = f"{config_type}_shortcuts"
            if shortcuts_config_type in self.system_config_files:
                # Load system shortcuts
                system_shortcuts = self._load_and_validate_system_config(shortcuts_config_type)
                if system_shortcuts:
                    # Remove the 'path' metadata key if present
                    shortcuts_data = {k: v for k, v in system_shortcuts.items() if k != 'path'}
                    if isinstance(shortcuts_data, dict):
                        shortcuts.update(shortcuts_data)
                
                # Load dev shortcuts if they exist
                dev_shortcuts = self._load_and_validate_dev_config(shortcuts_config_type, dev_config_path)
                if dev_shortcuts:
                    # Apply dev customizations to shortcuts
                    shortcuts = self._apply_shortcuts_customizations(shortcuts, dev_shortcuts)
        
        return shortcuts
    
    def _apply_shortcuts_customizations(self, system_shortcuts: Dict[str, Any], dev_shortcuts: Dict[str, Any]) -> Dict[str, Any]:
        """Apply dev customizations to shortcuts."""
        final_shortcuts = system_shortcuts.copy()
        
        # Apply override/add/exclude patterns
        if "override_nodes" in dev_shortcuts:
            for shortcut_name, overrides in dev_shortcuts["override_nodes"].items():
                if shortcut_name in final_shortcuts:
                    final_shortcuts[shortcut_name].update(overrides)
        
        if "add_nodes" in dev_shortcuts:
            for shortcut_name, shortcut_data in dev_shortcuts["add_nodes"].items():
                final_shortcuts[shortcut_name] = shortcut_data
        
        if "exclude_nodes" in dev_shortcuts:
            for shortcut_name in dev_shortcuts["exclude_nodes"]:
                final_shortcuts.pop(shortcut_name, None)
        
        return final_shortcuts
    
    def _collect_dev_node_customizations(self, dev_config_path: str = None) -> Dict[str, Any]:
        """Collect all override/add/exclude from all dev config files."""
        all_customizations = {
            "override_nodes": {},
            "add_nodes": {},
            "exclude_nodes": []
        }
        
        if not dev_config_path:
            return all_customizations
        
        for config_type in self.config_types:
            dev_config = self._load_and_validate_dev_config(config_type, dev_config_path)
            if dev_config:
                # Merge customizations from this config file
                all_customizations["override_nodes"].update(dev_config.get("override_nodes", {}))
                all_customizations["add_nodes"].update(dev_config.get("add_nodes", {}))
                all_customizations["exclude_nodes"].extend(dev_config.get("exclude_nodes", []))
        
        return all_customizations
    
    def _apply_dev_customizations_to_family(self, family_data: Dict[str, Any], family_file_path: str, customizations: Dict[str, Any]) -> None:
        """Apply dev customizations to a specific family's nodes using file-path-based semantic addressing."""
        family_nodes = family_data.get("nodes", {})
        
        # 1. OVERRIDE: Update specific fields in existing nodes
        for full_address, field_overrides in customizations["override_nodes"].items():
            try:
                target_file, node_id = self._parse_semantic_address(full_address)
                if self._file_matches(target_file, family_file_path):
                    if node_id in family_nodes:
                        family_nodes[node_id].update(field_overrides)
                        # Validation note: successful override
                    else:
                        self.validation_warnings.append(f"Override target node '{node_id}' not found in {family_file_path}")
            except ValueError as e:
                self.validation_warnings.append(f"Invalid override address '{full_address}': {e}")
        
        # 2. ADD: Insert complete new node definitions
        for full_address, complete_node_data in customizations["add_nodes"].items():
            try:
                target_file, node_id = self._parse_semantic_address(full_address)
                if self._file_matches(target_file, family_file_path):
                    family_nodes[node_id] = complete_node_data
                    # Validation note: successful addition
            except ValueError as e:
                self.validation_warnings.append(f"Invalid add address '{full_address}': {e}")
        
        # 3. EXCLUDE: Remove nodes entirely
        for full_address in customizations["exclude_nodes"]:
            try:
                target_file, node_id = self._parse_semantic_address(full_address)
                if self._file_matches(target_file, family_file_path):
                    if node_id in family_nodes:
                        family_nodes.pop(node_id)
                        # Validation note: successful exclusion
                    else:
                        self.validation_warnings.append(f"Exclude target node '{node_id}' not found in {family_file_path}")
            except ValueError as e:
                self.validation_warnings.append(f"Invalid exclude address '{full_address}': {e}")
    
    def _parse_semantic_address(self, full_address: str) -> Tuple[str, str]:
        """Parse 'path/to/file.json:node_id' into (file_path, node_id)."""
        if ":" not in full_address:
            raise ValueError(f"Invalid semantic address format: '{full_address}'. Expected 'path/to/file.json:node_id'")
        
        file_path, node_id = full_address.split(":", 1)
        file_path = file_path.strip()
        node_id = node_id.strip()
        
        if not file_path:
            raise ValueError(f"Invalid semantic address: missing file path in '{full_address}'")
        if not node_id:
            raise ValueError(f"Invalid semantic address: missing node_id in '{full_address}'")
        
        return file_path, node_id
    
    def _file_matches(self, target_file: str, actual_file_path: str) -> bool:
        """Check if target file matches actual family file path."""
        import os
        
        # Normalize paths for comparison
        target_normalized = os.path.normpath(target_file)
        actual_normalized = os.path.normpath(actual_file_path)
        
        # Support both absolute and relative path matching
        return (target_normalized == actual_normalized or 
                actual_normalized.endswith(target_normalized) or
                os.path.basename(actual_normalized) == os.path.basename(target_normalized))