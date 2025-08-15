# Implementation Plan: 17-Config System for TreeShell

## Context & Current State

After reading `shells.py`, `base.py`, and all config files, here's what we have:

**Current Architecture:**
- Main configs contain metadata (app_id, domain, role, families list)
- Nodes come from family files in `/configs/families/` directory
- Each family = **2-dimensional node structure** (menu node + its children called **"portals"**)
- TreeShellBase loads families and assembles them into coordinate tree using NAV config + parent relationships
- **NAV config dictates which families are active on the navigation menu**
- **Family parent field creates chains**: families connect to top-level NAV siblings through parent relationships
- **User already gets their own families directory** where they can write custom family files with nodes
- User gets copied configs in HEAVEN_DATA_DIR (this breaks library updates)

**Grammar & Structure:**
- **Family** = 2-dimensional node (menu + its direct children "portals")
- **Portals** = the children of a family menu node
- **NAV** creates main branches (0.1, 0.2, 0.3...)
- **Parent relationships** create sub-branches within main branches
- **Semantic names** = top-level node keys in family files (used for customization)

**Current Problem:**
- Copying system families to user directory freezes them (no library updates)
- Need separation between library truth and user customizations

**CRITICAL PRODUCTION REQUIREMENTS:**
- This is a **production codebase** - no blind coding without understanding
- Must have **proper Pydantic models** for validation and type safety
- **Bad nodes should not load** but processing continues with warnings
- Need **17 config type models** for each config schema
- All validation errors collected as warnings for debugging

## 17-Config System Architecture

### The 17 Config Files

**System Layer (Library - 8 configs):**
1. `system_base_config.json` - Base metadata
2. `system_agent_config.json` - Agent metadata  
3. `system_user_config.json` - User metadata
4. `system_base_shortcuts.json` - Core shortcuts
5. `system_agent_shortcuts.json` - Agent shortcuts
6. `system_user_shortcuts.json` - User shortcuts
7. `system_agent_zone_config.json` - Agent zones
8. `system_user_zone_config.json` - User zones

**User Layer - System Level (8 configs):**
9. `user_base_config.json` - Override/add/exclude base metadata
10. `user_agent_config.json` - Override/add/exclude agent metadata
11. `user_user_config.json` - Override/add/exclude user metadata
12. `user_base_shortcuts.json` - Override/add/exclude base shortcuts
13. `user_agent_shortcuts.json` - Override/add/exclude agent shortcuts
14. `user_user_shortcuts.json` - Override/add/exclude user shortcuts
15. `user_agent_zone_config.json` - Override/add/exclude agent zones
16. `user_user_zone_config.json` - Override/add/exclude user zones

**User Layer - User Controlled (1 config):**
17. `nav_config.json` - Navigation structure (copied to HEAVEN_DATA_DIR)

### Family System Changes

**Current (WRONG):**
- Copy system families to user directory → user edits copies → breaks updates

**New (CORRECT):**
- **System families stay in library package** → always fresh, automatic updates
- **User families directory for custom families only** → users write their own family files with nodes
- **User customizes system nodes through config override/add/exclude pattern** by semantic name
- **NAV config controls what families are active** in navigation menu
- **Users can reference both system families** (from library) **and their custom families** (from user dir)

### User Customization Types

**Override:** "Dictate this instead" - completely replace node definition
**Add:** Addition - add entirely new nodes 
**Exclude:** Ablation - remove nodes completely

These apply to **semantic names** (top-level node keys in family files), allowing precise control over individual nodes without editing the family files directly.

## Implementation Steps

### 1. Create Pydantic Validation Models

Create models in `system_config_loader.py` - **CRITICAL for production codebase validation**:

```python
# Base node types for family file validation
class Node(BaseModel):
    type: str
    prompt: str
    description: Optional[str] = None

class CallableNode(Node):
    type: Literal["Callable"] = "Callable"
    function_name: str
    import_path: Optional[str] = None
    import_object: Optional[str] = None
    is_async: bool = False
    args_schema: Dict[str, Any] = {}

class MenuNode(Node):
    type: Literal["Menu"] = "Menu" 
    options: Dict[str, str] = {}

class FamilyNode(Node):
    """2-dimensional node structure: menu + children portals"""
    type: Literal["Family"] = "Family"
    parent: Optional[str] = None  # For chaining families
    children: Dict[str, Node] = {}  # The portals

class NavNode(BaseModel):
    """Navigation structure node"""
    nav_tree_order: List[str] = []
    coordinate_mapping: Optional[Dict[str, str]] = {}

# Config models for ALL 17 types - MUST HAVE PROPER SCHEMAS
class SystemBaseConfig(BaseModel):
    app_id: str
    domain: str
    role: str
    about_app: Optional[str] = None
    about_domain: Optional[str] = None
    system_family: Optional[str] = None

class UserBaseConfig(BaseModel):
    """User customizations applied to system base"""
    override_nodes: Dict[str, Dict[str, Any]] = {}  # "Dictate this instead"
    add_nodes: Dict[str, Dict[str, Any]] = {}       # Addition
    exclude_nodes: List[str] = []                   # Ablation
    app_id: Optional[str] = None
    domain: Optional[str] = None
    role: Optional[str] = None

class SystemAgentConfig(BaseModel):
    app_id: str
    domain: str
    role: str
    about_app: Optional[str] = None
    about_domain: Optional[str] = None
    families: List[str] = []
    families_directory: Optional[str] = None
    nav_config: Optional[str] = None
    zone_config: Optional[str] = None

class UserAgentConfig(BaseModel):
    override_nodes: Dict[str, Dict[str, Any]] = {}
    add_nodes: Dict[str, Dict[str, Any]] = {}
    exclude_nodes: List[str] = []
    app_id: Optional[str] = None
    domain: Optional[str] = None
    role: Optional[str] = None

# ... MUST IMPLEMENT ALL 17 CONFIG TYPES
# SystemUserConfig, UserUserConfig
# SystemBaseShortcuts, UserBaseShortcuts
# SystemAgentShortcuts, UserAgentShortcuts  
# SystemUserShortcuts, UserUserShortcuts
# SystemAgentZoneConfig, UserAgentZoneConfig
# SystemUserZoneConfig, UserUserZoneConfig
# NavConfig
```

**Validation Strategy:**
- **Bad nodes filtered out** but processing continues
- **All validation errors collected** in `validation_warnings` attribute
- **Models validate JSON structure** before manipulation
- **No runtime type checking** - models are for validation only

### 2. Update SystemConfigLoader

Fix the loader to handle both **system families (library)** and **user families (user directory)**:

```python
class SystemConfigLoader:
    def __init__(self, config_types: List[str]):
        self.config_types = config_types
        self.validation_warnings: List[str] = []
        # ... ALL 17 config file attributes hardcoded
    
    def load_and_validate_configs(self, user_config_path: str = None) -> Dict[str, Any]:
        """Load, validate, and merge all configs with Pydantic validation"""
        final_config = {}
        
        for config_type in self.config_types:
            # Load system config with validation
            system_config = self._load_and_validate_system_config(config_type)
            
            # Load user config with validation (if exists)
            user_config = self._load_and_validate_user_config(config_type, user_config_path)
            
            # Merge configs (user overrides system)
            merged_config = self._merge_configs(system_config, user_config)
            
            # Add to final config
            final_config.update(merged_config)
        
        return final_config
    
    def load_families(self, families_list: List[str], user_families_dir: str = None) -> Dict[str, Any]:
        """Load and validate families from BOTH library and user directories"""
        families = {}
        
        # Load system families from library package (always fresh)
        for family_name in families_list:
            try:
                system_family = self._load_system_family(family_name)
                if system_family:
                    validated_family = self._validate_family(system_family, family_name)
                    if validated_family:
                        families[family_name] = validated_family
            except Exception as e:
                self.validation_warnings.append(f"Failed to load system family '{family_name}': {e}")
        
        # Load user families from user directory (custom families)
        if user_families_dir and os.path.exists(user_families_dir):
            for family_file in os.listdir(user_families_dir):
                if family_file.endswith("_family.json"):
                    family_name = family_file.replace("_family.json", "")
                    try:
                        user_family = self._load_user_family(user_families_dir, family_file)
                        if user_family:
                            validated_family = self._validate_family(user_family, family_name)
                            if validated_family:
                                families[family_name] = validated_family  # User families can override system
                    except Exception as e:
                        self.validation_warnings.append(f"Failed to load user family '{family_name}': {e}")
        
        return families
    
    def _validate_family(self, family_data: dict, family_name: str) -> dict:
        """Validate family nodes with Pydantic - bad nodes filtered out"""
        validated_nodes = {}
        
        for node_id, node_data in family_data.get("nodes", {}).items():
            try:
                # Validate node based on type
                node_type = node_data.get("type", "Menu")
                if node_type == "Callable":
                    validated_node = CallableNode(**node_data)
                elif node_type == "Menu":
                    validated_node = MenuNode(**node_data)
                else:
                    validated_node = Node(**node_data)
                
                # Store as dict (no runtime typing)
                validated_nodes[node_id] = validated_node.dict()
                
            except Exception as e:
                # Bad node filtered out, warning collected
                self.validation_warnings.append(f"Invalid node '{node_id}' in family '{family_name}': {e}")
                continue
        
        return {"nodes": validated_nodes} if validated_nodes else {}
```

**Key Points:**
- **System families loaded from library** (always fresh)
- **User families loaded from user directory** (custom families only)
- **Bad nodes filtered out** but processing continues
- **All validation errors collected** for debugging
- **Users can write complete family files** with their own nodes
- **NAV config controls which families are active** on menu

### 3. Update Base.py Family Loading

Modify `_load_family_configs()` in `base.py`:

```python
def _load_family_configs(self) -> dict:
    """Load families using SystemConfigLoader for validation"""
    families = {}
    
    # Get families list from merged configs
    config_families = self.graph.get("families", [])
    
    # Load families through SystemConfigLoader (with validation)
    if hasattr(self, 'system_config_loader'):
        user_families_dir = getattr(self, 'user_families_dir', None)
        families = self.system_config_loader.load_families(
            config_families, 
            user_families_dir
        )
        
        # Expose validation warnings
        self.config_validation_warnings = self.system_config_loader.validation_warnings
    
    return families
```

### 4. Update Shell Constructors

Modify shells to pass user directories properly:

```python
class UserTreeShell(TreeShell):
    def __init__(self, user_config_path: str = None, parent_approval_callback=None):
        self.user_config_path = user_config_path
        self.user_families_dir = os.path.join(user_config_path, "families") if user_config_path else None
        
        # Load and validate configs
        self.system_config_loader = SystemConfigLoader(config_types=["base", "user"])
        final_config = self.system_config_loader.load_and_validate_configs(user_config_path)
        
        TreeShell.__init__(self, final_config)
        # ... rest
```

### 5. Update HEAVEN_DATA_DIR Initialization

Modify `_initialize_heaven_data_dir()` in `base.py`:

```python
def _initialize_heaven_data_dir(self) -> bool:
    """Initialize user directory structure - USER FAMILIES DIRECTORY ALREADY EXISTS"""
    # Create directory structure
    os.makedirs(os.path.join(app_data_dir, "configs"), exist_ok=True)
    os.makedirs(os.path.join(app_data_dir, "families"), exist_ok=True)  # For user families only
    
    # Copy ONLY nav_config.json (user controlled - copied to HEAVEN_DATA_DIR)
    nav_config_src = os.path.join(library_configs_dir, "nav_config.json")
    nav_config_dst = os.path.join(app_data_dir, "configs", "nav_config.json")
    if os.path.exists(nav_config_src):
        shutil.copy2(nav_config_src, nav_config_dst)
    
    # Create ALL 16 empty user config templates with proper schema
    user_config_template = {
        "override_nodes": {},  # "Dictate this instead"
        "add_nodes": {},       # Addition
        "exclude_nodes": []    # Ablation
    }
    
    user_configs = [
        # User-level system configs (8)
        "user_base_config.json", "user_agent_config.json", "user_user_config.json",
        "user_base_shortcuts.json", "user_agent_shortcuts.json", "user_user_shortcuts.json", 
        "user_agent_zone_config.json", "user_user_zone_config.json"
    ]
    
    for config_file in user_configs:
        config_path = os.path.join(app_data_dir, "configs", config_file)
        with open(config_path, 'w') as f:
            json.dump(user_config_template, f, indent=2)
    
    # DO NOT copy system families - they stay in library for automatic updates
    # Users write their own family files in the families directory
```

### 6. Node Customization Process

After families are loaded and tree is built, apply user customizations:

```python
def _apply_user_node_customizations(self, nodes: Dict[str, Any]) -> Dict[str, Any]:
    """Apply user config customizations to loaded nodes"""
    if not hasattr(self, 'system_config_loader'):
        return nodes
    
    # Get user customizations from loaded configs
    user_overrides = self.system_config_loader.get_node_customizations()
    
    # Apply overrides by semantic name
    for node_id, overrides in user_overrides.get("override_nodes", {}).items():
        if node_id in nodes:
            nodes[node_id].update(overrides)
    
    # Add new nodes
    for node_id, node_data in user_overrides.get("add_nodes", {}).items():
        nodes[node_id] = node_data
    
    # Exclude nodes
    for node_id in user_overrides.get("exclude_nodes", []):
        nodes.pop(node_id, None)
    
    return nodes
```

## Key Architecture Principles

1. **System configs always load fresh from library** → automatic updates
2. **User configs apply customizations to system configs** → persistent user changes
3. **System families stay in library** → updatable
4. **User families in user directory** → custom families only
5. **Pydantic validation catches bad configs** → robust error handling
6. **Node customization by semantic name** → precise control
7. **Validation warnings preserved** → debugging capability

## Testing Strategy

1. Test each of the 17 config types loads and validates correctly
2. Test user customizations (override/add/exclude) work on nodes
3. Test system families load from library (not user directory)
4. Test user families load from user directory
5. Test validation catches malformed configs
6. Test library updates flow through while user customizations persist

This architecture ensures library evolution while preserving user customizations, with proper validation and error handling throughout.