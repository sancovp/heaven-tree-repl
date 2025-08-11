# TreeShell Transformation Plan: Three-Tree Navigation System

## Overview
Transform TreeShell from hardcoded coordinate system to dynamic three-tree navigation with family-based addressing, nav ordering, and zone theming.

## Architecture Summary

### The Three Tree Systems
1. **Family Trees**: Domain-based independent trees floating in graph space
2. **Nav Tree**: Arbitrary ordering of families for main navigation (0.1, 0.2, 0.3...)
3. **Zone Trees**: Thematic grouping of nodes/families for RPG overlay

### TreeShell Language Integration
**Current System**: Manual shortcuts (`shortcut brain 0.3`)
**New System**: Automatic semantic resolution via family system

TreeShell already has:
- **Semantic programming language** with coordinate addressing
- **Chain language** with data flow (`step1 -> step2 {"data": "$step1_result"}`)
- **Control flow** (and, or, if/then/else, while) - **TURING COMPLETE**
- **Shortcut system** for manual word creation
- **Mixed syntax** (shortcuts + coordinates in chains)

### New Family Addressing System
- **Family**: `agent_management.equipment.tools` → auto-resolves to coordinate
- **System**: `system.workflows.setup_agent` → `0.0.workflows.setup_agent`
- **Nav**: `0.1.2` (maps to family coordinate)
- **Zone**: `crystal_forest.agent_management.equipment`
- **Legacy**: Existing coordinates continue working

### Address Space Layout
- `0.0` = **system** family (workflows, templates, meta operations)
- `0.1` = **agent_management** family (was 0.3)
- `0.2` = **conversations** family (was 0.4) 
- `0.3+` = Additional families as needed

## Implementation Plan

### Phase 1: Core Architecture Changes

#### 1.1 Family System Implementation
- [ ] Create complete family JSON files (replacing old node system)
- [ ] Implement automatic semantic resolution in jump handler
- [ ] Build family tree loading system
- [ ] Create family → coordinate mapping tables

**New Family Structure:**
- `/configs/families/system_family.json` (0.0 - workflows, templates, meta)
- `/configs/families/agent_management_family.json` (0.1 - was 0.3)
- `/configs/families/conversations_family.json` (0.2 - was 0.4)
- `/configs/nav_config.json` (family ordering)
- `/configs/zone_config.json` (RPG theming)

**Semantic Resolution Enhancement:**
Current TreeShell language gets automatic resolution:
- `chain agent_management.equipment.tools {} -> system.workflows.create {}`
- No manual shortcuts needed - family system handles resolution
- All existing chain/control flow syntax works with new addressing

#### 1.2 Navigation System Updates
- [ ] Implement nav_config.json loading and ordering
- [ ] Update `nav` command to support family/zone scoping
- [ ] Add dual addressing resolution (family ↔ nav coordinates)
- [ ] Preserve options auto-generation from tree structure

**Enhanced Navigation Examples:**
```bash
# TreeShell Language Integration
nav                                    # Show full nav tree (ordered families)
nav agent_management                  # Show specific family tree  
nav crystal_forest                   # Show zone-scoped tree

# Automatic Semantic Resolution (NEW)
jump equipment_selection                     # Auto-resolves by node name search
jump equipment.tools                        # Auto-resolves partial path  
jump agent_management.equipment.tools       # Auto-resolves full family path
jump system.workflows.setup_agent          # Auto-resolves to 0.0.workflows.setup_agent
jump chat.start                            # Auto-resolves (no shortcut needed)

# Chain Language Enhancement (NEW)
chain agent_management.config.save {"name": "prod"} -> system.workflows.deploy {}
chain if agent_management.provider.list then system.meta.backup else agent_management.utils.reset

# Legacy Support (continues working)
jump 0.1.2                            # Nav coordinate
shortcut brain agent_management       # Manual shortcuts still work
```

#### 1.3 Zone System Implementation
- [ ] Add game_config and zone_map to configs
- [ ] Implement zone-based tree filtering
- [ ] Update renderer to show zone context
- [ ] Create zone selection menus

**Zone Features:**
- RPG-themed interface (Sanctuary Revolution)
- Zone-specific navigation trees
- Thematic overlays (Crystal Forest, Silicon Valley, etc.)

### Phase 2: Actions and Workflow Integration

#### 2.1 Universal Actions System
- [ ] Implement `{id}.actions` virtual nodes
- [ ] Add universal template actions (1=see, 2=create, 3=edit, 4=hidden)
- [ ] Connect actions to workflow system
- [ ] Actions system works with any addressing (family/nav/zone)

**Universal Actions:**
1. See Templates - Show available templates for this node
2. Create Template - Interactive template creation
3. Edit Templates - Modify existing templates  
4. Show Hidden Templates - System/advanced templates

#### 2.2 Workflow System Connection
- [ ] Create workflow family for Train of Thought sequences
- [ ] Implement workflow step navigation
- [ ] Connect workflow actions to template system
- [ ] Enable workflow creation from any node via actions

### Phase 3: Migration and Testing

#### 3.1 Configuration Migration
- [ ] Convert existing user_default_config.json to family structure
- [ ] Create nav_config.json with current hierarchy
- [ ] Set up basic zone configuration
- [ ] Ensure all current coordinates have family equivalents

#### 3.2 Compatibility Testing
- [ ] Test all existing jump commands still work
- [ ] Verify nav command builds correct trees
- [ ] Test menu generation and option navigation
- [ ] Validate callable function execution unchanged

#### 3.3 New Features Testing
- [ ] Test family addressing (`agent_management.equipment`)
- [ ] Test zone navigation and filtering
- [ ] Test universal actions system
- [ ] Test dual addressing resolution

## Detailed Implementation

### Family JSON Structure
```json
{
  "family_root": "agent_management",
  "domain": "agent_management",
  "nodes": {
    "agent_management": {
      "id": "agent_management",
      "title": "🎮 Agent Management Hub",
      "description": "Configure and manage AI agents"
    },
    "agent_management.equipment": {
      "id": "agent_management.equipment", 
      "title": "🔧 Equipment System",
      "description": "Equip/unequip agent components"
    },
    "agent_management.equipment.tools": {
      "id": "agent_management.equipment.tools",
      "title": "🛠️ Tools",
      "description": "Manage agent tools",
      "callable": {
        "function_name": "equip_tool",
        "args_schema": {"tool_name": "str"}
      }
    }
  }
}
```

### Nav Config Structure
```json
{
  "nav_tree_order": [
    "agent_management",
    "conversations", 
    "workflows",
    "development",
    "system"
  ],
  "coordinate_mapping": {
    "0.1": "agent_management",
    "0.2": "conversations",
    "0.3": "workflows",
    "0.4": "development", 
    "0.5": "system"
  }
}
```

### Zone Config Structure  
```json
{
  "game_config": {
    "title": "Sanctuary Revolution",
    "subtitle": "The AI Ascension Chronicles",
    "default_zone": "crystal_forest"
  },
  "zones": {
    "crystal_forest": {
      "name": "Crystal Forest",
      "description": "Where nascent intelligences awaken",
      "zone_tree": [
        "agent_management",
        "conversations"
      ],
      "is_hub": true
    },
    "silicon_valley": {
      "name": "Silicon Valley of Broken Dreams",
      "zone_tree": [
        "development",
        "workflows.ci_cd",
        "system.debugging"
      ]
    }
  }
}
```

## Success Criteria

### Core Functionality
- [x] All existing coordinates continue working
- [ ] Family addressing works (`agent_management.equipment`)
- [ ] Nav tree shows ordered families
- [ ] Zone filtering shows correct subsets
- [ ] Options auto-generate from tree structure
- [ ] Universal actions available on every node

### User Experience
- [ ] Seamless navigation between addressing systems
- [ ] RPG theming enhances without hindering functionality
- [ ] Clear hierarchical structure in all trees
- [ ] Consistent menu behavior across all nodes

### Developer Experience  
- [ ] Easy to add new families
- [ ] Simple to reorganize nav order
- [ ] Straightforward zone configuration
- [ ] Maintains backward compatibility

## Risk Mitigation

### High Risk Items
1. **Breaking existing functionality** - Maintain dual addressing during transition
2. **Performance impact** - Cache family trees and coordinate mappings
3. **Complex address resolution** - Implement clear fallback hierarchy
4. **Menu generation complexity** - Keep auto-generation logic simple and predictable

### Rollback Strategy
- Keep original config files as `_legacy` versions
- Implement feature flags for new vs old system
- Maintain complete backward compatibility until migration verified

## Timeline Estimate
- **Phase 1**: 2-3 days (core architecture)
- **Phase 2**: 1-2 days (actions/workflow)  
- **Phase 3**: 1 day (migration/testing)
- **Total**: 4-6 days for complete transformation

## Current Codebase Analysis

### Key Files and Functions
**Node Loading (`base.py`):**
- `_build_coordinate_nodes()` - Currently loads from single JSON config
- `_load_config_file()` - Loads JSON configs from `/configs/` directory
- Processes "Callable" vs "Menu" node types

**Address Resolution (`command_handlers.py`):**
- `_handle_jump()` - Direct coordinate lookup in `self.nodes`
- Simple string matching, no dynamic resolution
- Line 99: `if target_coord not in self.nodes: return error`

**Navigation (`command_handlers.py`):**
- `_handle_nav()` - Builds tree from coordinate parsing (splits on ".")
- Lines 577-597: Creates hierarchy from existing coordinate strings
- Independent of options system

**Rendering (`renderer.py`):**
- `render_response()` - Crystal ball markdown formatting
- Line 48: Shows position, app_id, domain in header
- Ready for zone/theme integration

### Current Config Structure
**Existing Configs:**
- `/configs/user_default_config.json` - 130+ nodes with hardcoded coordinates
- `/configs/base_default_config.json` - Base system nodes  
- `/configs/agent_default_config.json` - Agent-specific nodes

### Implementation Strategy

#### Phase 1A: Family System Foundation
**Create New Structure:**
```
/configs/families/
  ├── agent_management_family.json
  ├── conversations_family.json  
  ├── workflows_family.json
  └── system_family.json
/configs/nav_config.json
/configs/zone_config.json
```

**Modify `base.py`:**
- Add `_load_family_configs()` method
- Update `_build_coordinate_nodes()` to merge family trees
- Add family→coordinate and coordinate→family mapping
- Maintain backward compatibility with existing configs

**Modify `command_handlers.py`:**
- Update `_handle_jump()` to resolve family addresses first
- Add fallback to numeric coordinates
- Keep nav command tree-building unchanged (works with new coordinates)

#### Phase 1B: Automatic Semantic Resolution System
**Resolution Priority (TreeShell Language Enhancement):**
1. **Node name resolution**: `equipment_selection` → search all families for matching node name
2. **Partial path resolution**: `equipment.tools` → resolve within families
3. **Full family resolution**: `agent_management.equipment.tools` → `0.1.equipment.tools`
4. **System family resolution**: `system.workflows` → `0.0.workflows`  
5. **Zone-scoped resolution**: `crystal_forest.chat.start` → zone-filtered lookup
6. **Legacy coordinates**: `0.1.2` (exact numeric matches)
7. **Manual shortcuts**: `brain` → existing shortcut system

**Implementation in `_handle_jump()` (extends existing TreeShell language):**
```python
def _resolve_semantic_address(self, target_coord: str) -> str:
    """Auto-resolve family.node.subnode addresses"""
    # Try family resolution (NEW)
    if "." in target_coord and not target_coord[0].isdigit():
        # Check if starts with known family name
        family_name = target_coord.split(".")[0]
        if family_name in self.family_mappings:
            family_root = self.family_mappings[family_name]  # e.g. "0.1"
            semantic_path = target_coord[len(family_name)+1:]  # e.g. "equipment.tools"
            resolved = f"{family_root}.{semantic_path}"  # e.g. "0.1.equipment.tools"
            if resolved in self.nodes:
                return resolved
    
    # Try system family (NEW)
    if target_coord.startswith("system."):
        resolved = f"0.0.{target_coord[7:]}"  # system.workflows → 0.0.workflows
        if resolved in self.nodes:
            return resolved
    
    # Fall back to existing shortcut system
    return target_coord

# Integration with existing jump handler
original_target = target_coord
target_coord = self._resolve_semantic_address(target_coord)  # NEW

# Existing logic continues...
if target_coord not in self.nodes:
    return {"error": f"Target coordinate {original_target} not found"}
```

**TreeShell Language Benefits:**
- **Combinatorial explosion**: Every family.node.subnode automatically addressable
- **Node name resolution**: `equipment_selection` auto-resolves to its coordinate anywhere in graph
- **Partial path resolution**: `equipment.tools`, `config.save`, `workflows.create` all work
- **Chain language enhanced**: Use any semantic names in complex chains
- **Control flow enhanced**: `if equipment_selection` or `if agent_management.provider.list` works
- **No manual shortcuts needed**: System handles all resolution automatically

## Critical Files for Implementation

### Files to Read for Context:
1. **`/configs/user_default_config.json`** - Current node structure (130+ nodes to migrate)
2. **`heaven_tree_repl/base.py`** - Lines 194-243: `_build_coordinate_nodes()` method
3. **`heaven_tree_repl/command_handlers.py`** - Lines 90-119: `_handle_jump()` method  
4. **`heaven_tree_repl/command_handlers.py`** - Lines 572-650: `_handle_nav()` method
5. **`heaven_tree_repl/renderer.py`** - Lines 31-50: `render_response()` method

### Files to Create:
1. **`/configs/families/system_family.json`** (0.0 - workflows, templates, meta)
2. **`/configs/families/agent_management_family.json`** (0.1 - equipment, config, utils)  
3. **`/configs/families/conversations_family.json`** (0.2 - chat, management)
4. **`/configs/nav_config.json`** (family ordering: 0.0→system, 0.1→agent_management, etc.)
5. **`/configs/zone_config.json`** (RPG theming: crystal_forest, silicon_valley)

### Files to Modify:
1. **`heaven_tree_repl/base.py`** - Add family loading + coordinate mapping
2. **`heaven_tree_repl/command_handlers.py`** - Add semantic resolution to `_handle_jump()`
3. **`heaven_tree_repl/renderer.py`** - Add zone theming to display

### Key Implementation Notes:
- **Current nav system** (lines 577-597) builds tree by parsing coordinate strings - will work with new family coordinates automatically
- **Current jump system** (lines 99) does direct `self.nodes` lookup - needs semantic resolution layer
- **TreeShell language** already exists - we're adding auto-resolution to existing chain/control flow system
- **Existing shortcuts** (`brain`, `settings`) are manual - we're adding automatic semantic resolution
- **Family JSON files** contain complete node definitions (not just structure)
- **Address mapping**: `agent_management.equipment.tools` → `0.1.equipment.tools`

### Migration Strategy:
1. **Phase 1**: Create family JSONs from existing nodes
2. **Phase 2**: Add semantic resolution to jump handler  
3. **Phase 3**: Test that `equipment.tools` auto-resolves correctly
4. **Phase 4**: Add zone theming and universal actions

## Updated Next Steps
1. ✅ ~~Examine current codebase structure in detail~~
2. ✅ ~~Create implementation plan document~~
3. [ ] **START NEW CHAT** - Begin implementation with family JSON creation
4. [ ] Extract current `user_default_config.json` to family structure
5. [ ] Implement semantic resolution in `_handle_jump()`
6. [ ] Test auto-resolution: `equipment_selection`, `equipment.tools`, etc.
7. [ ] Add zone theming and universal actions system

## Implementation Order
**Day 1:** Family JSONs + semantic resolution  
**Day 2:** Testing + zone theming
**Day 3:** Universal actions + workflow integration
**Day 4:** Polish + documentation

---

*Last Updated: Pre-Implementation - Ready for New Chat*
*Status: Complete Plan - Begin Implementation*