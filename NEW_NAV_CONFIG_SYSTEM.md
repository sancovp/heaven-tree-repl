# New Nav Config System - Sprint Planning

## Current Status: Foundation Complete ✅

The nav config foundation is working correctly. All shells now load 141 nodes with proper navigation.

### What's Working
- **Base nav configs**: All 3 nav configs (nav_config.json, user_nav_config.json, agent_nav_config.json) are identical copies with 5 families
- **SystemConfigLoader**: Loads nav configs through `_load_referenced_configs()` when referenced by filename
- **All shell types**: BaseTreeShell, UserTreeShell, AgentTreeShell, FullstackTreeShell all load 141 nodes correctly
- **Family loading**: All 29 families load, 5 get numbered nav coordinates (0.1-0.5), others accessible via semantic coordinates
- **Dev config templates**: Empty dev nav config files created with correct override/add/exclude schema

## Next Sprint: Implement Dev Nav Config System

### Goal
Enable users to customize navigation through dev configs using the same override/add/exclude pattern as other config types.

### Architecture Design

#### Nav Config Types (6 total)
**System nav configs (3):**
- `system_base_nav_config.json` - Core minimal navigation 
- `system_agent_nav_config.json` - Agent-specific navigation extensions
- `system_user_nav_config.json` - User-specific navigation extensions

**Dev nav configs (3):**
- `dev_base_nav_config.json` - Base navigation customizations
- `dev_agent_nav_config.json` - Agent navigation customizations  
- `dev_user_nav_config.json` - User navigation customizations

#### Dev Nav Config Schema
```json
{
  "override_families": {
    "system": {
      "coordinate": "0.1",
      "priority": 1,
      "display_name": "Core System"
    }
  },
  "add_families": {
    "custom_family": {
      "coordinate": "0.6",
      "priority": 6,
      "display_name": "Custom Tools"
    }
  },
  "exclude_families": ["workflows", "development"]
}
```

#### Override/Add/Exclude Patterns
- **override_families**: Modify existing family nav properties (coordinate, priority, display_name)
- **add_families**: Add new families to navigation tree  
- **exclude_families**: Remove families from navigation (they remain accessible via semantic coordinates)

### Implementation Tasks

#### Task 1: Extend SystemConfigLoader for Nav Configs
**File**: `system_config_loader_v2.py`

```python
# Add to system_config_files
"base_nav_config": "system_base_nav_config.json",
"agent_nav_config": "system_agent_nav_config.json", 
"user_nav_config": "system_user_nav_config.json",

# Add to dev_config_files  
"base_nav_config": "dev_base_nav_config.json",
"agent_nav_config": "dev_agent_nav_config.json",
"user_nav_config": "dev_user_nav_config.json",
```

#### Task 2: Implement Nav Config Merging Logic
**New method**: `_apply_nav_customizations(system_nav, dev_nav) -> merged_nav`

```python
def _apply_nav_customizations(self, system_nav: Dict[str, Any], dev_nav: Dict[str, Any]) -> Dict[str, Any]:
    """Apply dev customizations to nav config using override/add/exclude pattern."""
    
    # Start with system nav config
    final_nav = system_nav.copy()
    nav_tree_order = final_nav.get("nav_tree_order", []).copy()
    coordinate_mapping = final_nav.get("coordinate_mapping", {}).copy()
    family_priorities = final_nav.get("family_priorities", {}).copy()
    
    # Apply exclusions (remove families)
    exclude_families = dev_nav.get("exclude_families", [])
    for family_name in exclude_families:
        if family_name in nav_tree_order:
            nav_tree_order.remove(family_name)
        # Remove from mappings
        coord_to_remove = None
        for coord, fam in coordinate_mapping.items():
            if fam == family_name:
                coord_to_remove = coord
                break
        if coord_to_remove:
            del coordinate_mapping[coord_to_remove]
        family_priorities.pop(family_name, None)
    
    # Apply overrides (modify existing families)
    override_families = dev_nav.get("override_families", {})
    for family_name, overrides in override_families.items():
        if family_name in nav_tree_order:
            # Update coordinate mapping if specified
            if "coordinate" in overrides:
                # Find old coordinate and update
                old_coord = None
                for coord, fam in coordinate_mapping.items():
                    if fam == family_name:
                        old_coord = coord
                        break
                if old_coord:
                    del coordinate_mapping[old_coord]
                coordinate_mapping[overrides["coordinate"]] = family_name
            
            # Update priority if specified
            if "priority" in overrides:
                family_priorities[family_name] = overrides["priority"]
    
    # Apply additions (add new families)
    add_families = dev_nav.get("add_families", {})
    for family_name, family_config in add_families.items():
        if family_name not in nav_tree_order:
            # Add to nav tree order based on priority
            priority = family_config.get("priority", 999)
            coordinate = family_config.get("coordinate")
            
            # Insert in correct position based on priority
            insert_index = len(nav_tree_order)
            for i, existing_family in enumerate(nav_tree_order):
                existing_priority = family_priorities.get(existing_family, 999)
                if priority < existing_priority:
                    insert_index = i
                    break
            
            nav_tree_order.insert(insert_index, family_name)
            
            if coordinate:
                coordinate_mapping[coordinate] = family_name
            family_priorities[family_name] = priority
    
    # Update final nav config
    final_nav["nav_tree_order"] = nav_tree_order
    final_nav["coordinate_mapping"] = coordinate_mapping
    final_nav["family_priorities"] = family_priorities
    
    return final_nav
```

#### Task 3: Update Shell Constructors
**File**: `shells.py`

Update config_types in each shell to include nav configs:
```python
# TreeShell (base)
config_types=["base", "base_zone_config", "base_shortcuts", "base_nav_config"]

# AgentTreeShell  
config_types=["agent", "agent_zone_config", "agent_shortcuts", "agent_nav_config"]

# UserTreeShell
config_types=["user", "user_zone_config", "user_shortcuts", "user_nav_config"]

# FullstackTreeShell
config_types=["base", "agent", "user", "base_zone_config", "agent_zone_config", "user_zone_config", "base_shortcuts", "agent_shortcuts", "user_shortcuts", "base_nav_config", "agent_nav_config", "user_nav_config"]
```

#### Task 4: Rename and Restructure Nav Configs
**Current nav configs** need to be split into proper inheritance hierarchy:

1. **Rename existing files**:
   - `nav_config.json` → `system_base_nav_config.json` (minimal: just "system")
   - `user_nav_config.json` → `system_user_nav_config.json` (base + user additions)  
   - `agent_nav_config.json` → `system_agent_nav_config.json` (base + agent additions)

2. **Restructure content**:
   - Base: `["system"]` only
   - User: `["system", "agent_management", "conversations"]` 
   - Agent: `["system", "task_execution", "tool_management"]`
   - Fullstack: All families `["system", "agent_management", "conversations", "workflows", "development"]`

#### Task 5: Add Nav Config Validation
**File**: `config_models.py`

```python
class NavConfig(BaseModel):
    nav_tree_order: List[str]
    coordinate_mapping: Optional[Dict[str, str]] = {}
    family_priorities: Optional[Dict[str, int]] = {}
    description: Optional[str] = ""
    version: Optional[str] = "1.0"
    legacy_mappings: Optional[Dict[str, str]] = {}

class DevNavConfig(BaseModel):
    override_families: Optional[Dict[str, Dict[str, Any]]] = {}
    add_families: Optional[Dict[str, Dict[str, Any]]] = {}
    exclude_families: Optional[List[str]] = []
```

### Testing Plan

#### Phase 1: Basic Nav Config Loading
1. Verify SystemConfigLoader recognizes nav config types
2. Test nav config merging with empty dev configs
3. Ensure all shells load correctly with new nav config types

#### Phase 2: Dev Nav Config Customizations
1. Test exclude_families: Remove "development" family from user nav
2. Test override_families: Change coordinate of "system" from 0.1 to 0.9
3. Test add_families: Add custom family at coordinate 0.6

#### Phase 3: Integration Testing
1. Test multiple dev nav configs simultaneously
2. Verify inheritance: user dev nav configs don't affect agent shells
3. Test nav config priority resolution and conflict handling

### Migration Strategy

#### Step 1: Implement Foundation (No Breaking Changes)
- Add nav config support to SystemConfigLoader
- Keep existing nav_config.json loading as fallback
- Test that everything still works

#### Step 2: Gradual Migration  
- Rename nav config files to system_* pattern
- Update shell constructors to use new nav config types
- Verify node counts remain correct (141 nodes)

#### Step 3: Enable Dev Customizations
- Test dev nav config override/add/exclude functionality
- Create example dev nav configs for common use cases
- Document nav config customization patterns

### Success Criteria

✅ **All shells maintain 141 base nodes** (no regression)
✅ **Nav config inheritance works**: base → user/agent → fullstack  
✅ **Dev customizations apply correctly**: override/add/exclude patterns work
✅ **Zero breaking changes**: existing functionality preserved
✅ **Clear separation**: library nav configs vs user customizations
✅ **Documentation complete**: examples and patterns documented

### Future Enhancements

- **Dynamic nav reloading**: Hot-reload nav configs without restart
- **Nav config validation**: Prevent coordinate conflicts and circular dependencies  
- **Visual nav editor**: GUI tool for editing nav configs
- **Nav config templates**: Pre-built nav configs for common workflows
- **Advanced nav patterns**: Conditional navigation based on context

## Current File Structure

```
/configs/
├── nav_config.json                    # Main nav config (5 families)
├── user_nav_config.json               # Copy of main (will be restructured)  
├── agent_nav_config.json              # Copy of main (will be restructured)
├── dev_base_nav_config.json           # Empty dev template ✅
├── dev_agent_nav_config.json          # Empty dev template ✅
├── dev_user_nav_config.json           # Empty dev template ✅
└── system_*_config.json               # Other system configs
```

## Key Insight: Navigation as Configuration Layer

Navigation is a **configuration layer** on top of the family system, not a replacement for it. All families always load (29 total), but nav configs determine:

1. **Which families get numbered coordinates** (0.1, 0.2, etc.)
2. **Navigation order and priority**  
3. **Display names and grouping**
4. **User-specific customizations**

This allows maximum flexibility while maintaining system consistency.

---

## Advanced Family Management Operations

Based on the need for better family creation and management workflows, we should implement three new meta operations to improve the user experience:

### 1. Add Family Operation (`_meta_add_family`)

**Purpose**: Create complete family structures in one operation instead of node-by-node creation.

**Current Problem**: Users must:
- Track parent-child relationships manually
- Call add_node multiple times for each family member
- Keep coordinate mappings straight across multiple operations

**Solution**: Single operation that takes a complete family definition and creates all nodes at once.

#### Family Model Validation
```python
class FamilyModel(BaseModel):
    family_name: str
    domain: str
    description: Optional[str] = ""
    nodes: Dict[str, FamilyNodeModel]
    
class FamilyNodeModel(BaseModel):
    title: str
    description: str
    type: str = "Menu"
    parent: Optional[str] = None
    callable: Optional[CallableConfig] = None
    options: Optional[Dict[str, Any]] = {}
```

#### Implementation
- Validate entire family structure with Pydantic
- Create family file in user's dev configs
- Generate all nodes with proper parent relationships
- Automatic prompt block creation for all descriptions
- Return summary of created family structure

### 2. Add Family to Navigation (`_meta_add_family_to_nav`)

**Purpose**: Integrate existing families into the navigation system by updating nav configs.

**Workflow**:
1. Take existing family name
2. Assign nav coordinate (e.g., 0.6)
3. Set priority and display name
4. Update appropriate nav config file (base/user/agent)
5. Validate no coordinate conflicts

#### Parameters
```python
{
    "family_name": "my_custom_tools",
    "nav_coordinate": "0.6", 
    "priority": 6,
    "display_name": "🛠️ Custom Tools",
    "nav_config_type": "user"  # base/user/agent
}
```

### 3. Add Zone Operation (`_meta_add_zone`)

**Purpose**: Create new zone configurations for semantic grouping.

**Note**: This requires the zone config system to support dev customizations (similar to nav config system).

#### Zone Model
```python
class ZoneModel(BaseModel):
    zone_name: str
    description: str
    zone_tree: List[str]  # Family references
    semantic_mappings: Optional[Dict[str, str]] = {}
    display_config: Optional[Dict[str, Any]] = {}
```

#### Implementation Dependencies
- Extend zone config system to support override/add/exclude patterns
- Add dev zone config files (dev_base_zone_config.json, etc.)
- Zone config merging logic in SystemConfigLoader
- Validation to prevent zone conflicts

### Implementation Priority

**Phase 1: Family Management**
1. Create FamilyModel and validation
2. Implement `_meta_add_family` 
3. Implement `_meta_add_family_to_nav`
4. Add these operations to system family as accessible nodes

**Phase 2: Zone Management** 
1. Extend zone config system for dev customizations
2. Implement zone config merging in SystemConfigLoader  
3. Create ZoneModel and validation
4. Implement `_meta_add_zone`

### Benefits

- **Simplified Workflow**: Create entire families at once
- **Better UX**: No manual coordinate tracking
- **Validation**: Prevent structural errors upfront  
- **Separation of Concerns**: Family creation vs nav integration vs zone grouping
- **Consistency**: All operations follow same override/add/exclude patterns

### Integration Points

These operations integrate with:
- **19-config system**: Save to appropriate dev config directories
- **Prompt block system**: Automatic prompt block creation for descriptions
- **Navigation system**: Coordinate assignment and conflict prevention
- **Validation system**: Pydantic models for structure validation