#!/usr/bin/env python3
"""
Pydantic Models for TreeShell 17-Config System

Provides validation models for all 17 config types in the TreeShell architecture.
Models are used for validation only, not runtime type checking.
"""

from pydantic import BaseModel, Field, model_validator
from typing import Dict, List, Any, Optional, Literal, Union
from enum import Enum


# Base configuration model with path tracking
class BaseConfig(BaseModel):
    """Base configuration model with path tracking."""
    path: Optional[str] = None
    
    class Config:
        extra = "allow"  # Allow additional fields for flexibility


# === Node Models for Family Validation ===

class NodeType(str, Enum):
    """Valid node types for family validation."""
    MENU = "Menu"
    CALLABLE = "Callable"


class BaseNode(BaseModel):
    """Base node model for family file validation."""
    type: NodeType
    prompt: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    signature: Optional[str] = None
    options: Dict[str, str] = Field(default_factory=dict)
    id: Optional[str] = None
    
    @model_validator(mode='before')
    def handle_prompt_title(cls, values):
        """Handle prompt/title equivalence - they're the same thing."""
        if isinstance(values, dict):
            prompt = values.get('prompt')
            title = values.get('title')
            
            # If we have title but no prompt, copy title to prompt
            if title and not prompt:
                values['prompt'] = title
            # If we have prompt but no title, copy prompt to title  
            elif prompt and not title:
                values['title'] = prompt
                
        return values
    
    class Config:
        extra = "allow"


class CallableNode(BaseNode):
    """Callable node with function execution capabilities."""
    type: Literal[NodeType.CALLABLE] = NodeType.CALLABLE
    function_name: Optional[str] = None  # Not required for all callable nodes
    import_path: Optional[str] = None
    import_object: Optional[str] = None
    function_code: Optional[str] = None
    is_async: bool = False
    args_schema: Dict[str, Any] = Field(default_factory=dict)


class MenuNode(BaseNode):
    """Menu node with navigation options."""
    type: Literal[NodeType.MENU] = NodeType.MENU
    options: Dict[str, str] = Field(default_factory=dict)


# === Family Models ===

class FamilyConfig(BaseModel):
    """Family configuration containing 2D node structure."""
    family_root: str
    parent: Optional[str] = None
    domain: str
    description: str
    nodes: Dict[str, Union[CallableNode, MenuNode, BaseNode]] = Field(default_factory=dict)
    
    class Config:
        extra = "allow"


# === System Config Models (8 types) ===

class SystemBaseConfig(BaseConfig):
    """System-level base configuration."""
    app_id: str
    domain: str
    role: str
    about_app: Optional[str] = None
    about_domain: Optional[str] = None
    system_family: Optional[str] = None


class SystemAgentConfig(BaseConfig):
    """System-level agent configuration."""
    app_id: str
    domain: str
    role: str
    about_app: Optional[str] = None
    about_domain: Optional[str] = None
    families: List[str] = Field(default_factory=list)
    families_directory: Optional[str] = None
    nav_config: Optional[str] = None
    zone_config: Optional[str] = None


class SystemUserConfig(BaseConfig):
    """System-level user configuration."""
    app_id: str
    domain: str
    role: str
    about_app: Optional[str] = None
    about_domain: Optional[str] = None
    families: List[str] = Field(default_factory=list)
    families_directory: Optional[str] = None
    nav_config: Optional[str] = None
    zone_config: Optional[str] = None


class ShortcutAction(BaseModel):
    """Individual shortcut action definition."""
    type: Literal["jump", "chain"]
    coordinate: Optional[str] = None  # For jump shortcuts
    template: Optional[str] = None    # For chain shortcuts
    description: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None  # For chain shortcuts


class SystemBaseShortcuts(BaseConfig):
    """System-level base shortcuts."""
    shortcuts: Dict[str, ShortcutAction] = Field(default_factory=dict)
    
    def __init__(self, **data):
        # Handle both direct shortcut format and nested shortcuts format
        if 'shortcuts' not in data and any(key != 'path' for key in data.keys()):
            # Direct format - convert to nested
            shortcuts = {}
            for key, value in data.items():
                if key != 'path' and isinstance(value, dict):
                    shortcuts[key] = value
            data = {'shortcuts': shortcuts, 'path': data.get('path')}
        super().__init__(**data)


class SystemAgentShortcuts(SystemBaseShortcuts):
    """System-level agent shortcuts."""
    pass


class SystemUserShortcuts(SystemBaseShortcuts):
    """System-level user shortcuts."""
    pass


class ZoneConfig(BaseModel):
    """Zone configuration for RPG theming."""
    zone_tree: List[str] = Field(default_factory=list)
    description: Optional[str] = None


class SystemBaseZoneConfig(BaseConfig):
    """System-level base zone configuration."""
    zones: Dict[str, ZoneConfig] = Field(default_factory=dict)


class SystemAgentZoneConfig(BaseConfig):
    """System-level agent zone configuration."""
    zones: Dict[str, ZoneConfig] = Field(default_factory=dict)


class SystemUserZoneConfig(BaseConfig):
    """System-level user zone configuration."""
    zones: Dict[str, ZoneConfig] = Field(default_factory=dict)


# === Dev Config Models (8 types) ===
# These use the override/add/exclude pattern

class DevCustomizationPattern(BaseModel):
    """Base pattern for dev-level customizations."""
    override_nodes: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    add_nodes: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    exclude_nodes: List[str] = Field(default_factory=list)


class DevBaseConfig(BaseConfig, DevCustomizationPattern):
    """Dev-level base configuration customizations."""
    app_id: Optional[str] = None
    domain: Optional[str] = None
    role: Optional[str] = None
    about_app: Optional[str] = None
    about_domain: Optional[str] = None
    system_family: Optional[str] = None


class DevAgentConfig(BaseConfig, DevCustomizationPattern):
    """Dev-level agent configuration customizations."""
    app_id: Optional[str] = None
    domain: Optional[str] = None
    role: Optional[str] = None
    about_app: Optional[str] = None
    about_domain: Optional[str] = None
    families: Optional[List[str]] = None
    families_directory: Optional[str] = None
    nav_config: Optional[str] = None
    zone_config: Optional[str] = None


class DevUserConfig(BaseConfig, DevCustomizationPattern):
    """Dev-level user configuration customizations."""
    app_id: Optional[str] = None
    domain: Optional[str] = None
    role: Optional[str] = None
    about_app: Optional[str] = None
    about_domain: Optional[str] = None
    families: Optional[List[str]] = None
    families_directory: Optional[str] = None
    nav_config: Optional[str] = None
    zone_config: Optional[str] = None


class DevBaseShortcuts(BaseConfig, DevCustomizationPattern):
    """Dev-level base shortcuts customizations."""
    pass


class DevAgentShortcuts(BaseConfig, DevCustomizationPattern):
    """Dev-level agent shortcuts customizations."""
    pass


class DevUserShortcuts(BaseConfig, DevCustomizationPattern):
    """Dev-level user shortcuts customizations."""
    pass


class DevBaseZoneConfig(BaseConfig, DevCustomizationPattern):
    """Dev-level base zone configuration customizations."""
    zones: Optional[Dict[str, ZoneConfig]] = None


class DevAgentZoneConfig(BaseConfig, DevCustomizationPattern):
    """Dev-level agent zone configuration customizations."""
    zones: Optional[Dict[str, ZoneConfig]] = None


class DevUserZoneConfig(BaseConfig, DevCustomizationPattern):
    """Dev-level user zone configuration customizations."""
    zones: Optional[Dict[str, ZoneConfig]] = None


# === Navigation Config (1 type) ===

class NavConfig(BaseConfig):
    """Navigation configuration (user-controlled)."""
    nav_tree_order: List[str] = Field(default_factory=list)
    coordinate_mapping: Optional[Dict[str, str]] = None
    family_priorities: Optional[Dict[str, int]] = None
    description: Optional[str] = None
    version: Optional[str] = None
    legacy_mappings: Optional[Dict[str, str]] = None


# === Container Models ===

class SystemConfigContainer(BaseModel):
    """Container for all 9 system-level configurations."""
    system_base_config: SystemBaseConfig
    system_agent_config: SystemAgentConfig
    system_user_config: SystemUserConfig
    system_base_shortcuts: SystemBaseShortcuts
    system_agent_shortcuts: SystemAgentShortcuts
    system_user_shortcuts: SystemUserShortcuts
    system_base_zone_config: SystemBaseZoneConfig
    system_agent_zone_config: SystemAgentZoneConfig
    system_user_zone_config: SystemUserZoneConfig


class DevConfigContainer(BaseModel):
    """Container for all 9 dev-level customization configurations."""
    dev_base_config: DevBaseConfig
    dev_agent_config: DevAgentConfig
    dev_user_config: DevUserConfig
    dev_base_shortcuts: DevBaseShortcuts
    dev_agent_shortcuts: DevAgentShortcuts
    dev_user_shortcuts: DevUserShortcuts
    dev_base_zone_config: DevBaseZoneConfig
    dev_agent_zone_config: DevAgentZoneConfig
    dev_user_zone_config: DevUserZoneConfig


class CompleteConfigSet(BaseModel):
    """Complete set of all 19 configurations."""
    # System configs (9)
    system_configs: SystemConfigContainer
    
    # Dev configs (9)
    dev_configs: DevConfigContainer
    
    # Navigation config (1)
    nav_config: NavConfig


# === Type Mapping for Dynamic Loading ===

SYSTEM_CONFIG_MODELS = {
    "base": SystemBaseConfig,
    "agent": SystemAgentConfig,
    "user": SystemUserConfig,
    "base_shortcuts": SystemBaseShortcuts,
    "agent_shortcuts": SystemAgentShortcuts,
    "user_shortcuts": SystemUserShortcuts,
    "base_zone_config": SystemBaseZoneConfig,
    "agent_zone_config": SystemAgentZoneConfig,
    "user_zone_config": SystemUserZoneConfig,
}

DEV_CONFIG_MODELS = {
    "base": DevBaseConfig,
    "agent": DevAgentConfig,
    "user": DevUserConfig,
    "base_shortcuts": DevBaseShortcuts,
    "agent_shortcuts": DevAgentShortcuts,
    "user_shortcuts": DevUserShortcuts,
    "base_zone_config": DevBaseZoneConfig,
    "agent_zone_config": DevAgentZoneConfig,
    "user_zone_config": DevUserZoneConfig,
}

NODE_MODELS = {
    "Menu": MenuNode,
    "Callable": CallableNode,
}