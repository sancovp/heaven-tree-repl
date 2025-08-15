# Testing the 19-Config System

This document provides a comprehensive testing routine for verifying that the TreeShell 19-config system is working correctly with dev customizations, validation, and proper separation between system and dev configs.

## Overview

The 19-config system consists of:
- **9 System Configs**: Load fresh from library (e.g., `system_base_config.json`)
- **9 Dev Configs**: Apply customizations (e.g., `dev_base_config.json`) 
- **1 Nav Config**: User-controlled navigation (`nav_config.json`)

## Prerequisites

1. HEAVEN_DATA_DIR environment variable set (e.g., `/tmp/heaven_data`)
2. TreeShell system installed and working
3. System family files in `configs/families/` directory
4. SystemConfigLoader v2 with Pydantic validation

## Testing Routine

### Phase 1: Basic Navigation Testing

Test that the core navigation system works without customizations.

#### Test 1.1: Root Menu Navigation
```bash
PYTHONPATH=/home/GOD/heaven-tree-repl python3 test_user_treeshell.py "0"
```

**Expected Output:**
```
<<[🔮‍🌳]>> You are now visiting position `0` in the user_interface_hub tree space...
# Introspect
>>>
```

**Validates:** Root menu loads and shell initializes correctly.

#### Test 1.2: Navigation Tree Overview  
```bash
PYTHONPATH=/home/GOD/heaven-tree-repl python3 test_user_treeshell.py "nav"
```

**Expected Output:**
```
# 🗺️ Navigation Overview
```
🔮 0: Main Menu (3 paths) - Root menu for user_interface_hub
├── 🗺️ 0.1: Settings & Management (12 paths) - System configuration...
├── 🤖 0.2: 🎮 Agent Management Hub (4 paths)
└── 🗺️ 0.3: 💬 Conversation Management (5 paths)
```

**Validates:** 
- Navigation tree builds correctly
- All family nodes have proper titles (no "None" values)
- Coordinate assignments work
- Tree structure is hierarchical

#### Test 1.3: Individual Node Navigation
```bash
PYTHONPATH=/home/GOD/heaven-tree-repl python3 test_user_treeshell.py "jump 0.1"
```

**Expected Output:**
```
# Settings & Management Menu
Description: System configuration and pathway management
Actions:[
  1: 1 -> system_pathways
  2: 2 -> system_meta
  ...
]
```

**Validates:**
- Individual nodes are accessible
- Nodes have proper titles from family files
- Options are properly populated

### Phase 2: App Folder Management Testing

Test that HEAVEN_DATA_DIR management works correctly.

#### Test 2.1: App Folder Creation
Delete existing app folder and create new shell:
```bash
rm -rf /tmp/heaven_data/user_interface_hub_v1_0
PYTHONPATH=/home/GOD/heaven-tree-repl python3 test_user_treeshell.py "0"
```

**Expected Output:**
```
Initialized HEAVEN_DATA_DIR for user_interface_hub_v1_0 at /tmp/heaven_data/user_interface_hub_v1_0
Created 9 empty dev config templates
```

**Validates:**
- App folder created with correct version naming
- All 9 dev config templates created
- Nav config copied to user directory

#### Test 2.2: Dev Config Template Verification
```bash
ls -la /tmp/heaven_data/user_interface_hub_v1_0/configs/
```

**Expected Files:**
```
dev_base_config.json
dev_agent_config.json  
dev_user_config.json
dev_base_shortcuts.json
dev_agent_shortcuts.json
dev_user_shortcuts.json
dev_base_zone_config.json
dev_agent_zone_config.json
dev_user_zone_config.json
nav_config.json
```

**Validates:**
- Correct dev config naming (not user_*)
- Empty templates with override/add/exclude schema
- Nav config present for user control

### Phase 3: Dev Customization Testing

Test the override/add/exclude pattern with dev configs.

#### Test 3.1: Create Dev Customization Config
Create `/tmp/heaven_data/user_interface_hub_v1_0/configs/dev_base_config.json`:
```json
{
  "override_nodes": {
    "configs/families/system_family.json:system": {
      "title": "🚀 CUSTOM SYSTEM MENU"
    }
  },
  "add_nodes": {
    "configs/families/system_family.json:my_custom_node": {
      "type": "Menu",
      "title": "🎯 My Custom Feature",
      "description": "This is a custom node added via dev config",
      "options": {}
    }
  },
  "exclude_nodes": [
    "configs/families/conversations_family.json:search"
  ]
}
```

**Validates:** File-path-based semantic addressing format.

#### Test 3.2: Test Shell with Customizations
```python
#!/usr/bin/env python3
import os
import sys
import asyncio

os.environ['HEAVEN_DATA_DIR'] = '/tmp/heaven_data'
sys.path.insert(0, '/home/GOD/heaven-tree-repl')

from heaven_tree_repl.shells import UserTreeShell
from heaven_tree_repl import render_response

async def main():
    # Point to dev configs directory
    dev_config_path = "/tmp/heaven_data/user_interface_hub_v1_0/configs"
    shell = UserTreeShell(user_config_path=dev_config_path)
    
    command = sys.argv[1] if len(sys.argv) > 1 else "nav"
    result = await shell.handle_command(command)
    rendered = render_response(result)
    print(rendered)

if __name__ == "__main__":
    asyncio.run(main())
```

#### Test 3.3: Verify Override Customization
```bash
PYTHONPATH=/home/GOD/heaven-tree-repl python3 test_with_customizations.py "jump 0.1"
```

**Expected Output:**
```
# 🚀 CUSTOM SYSTEM MENU Menu
Description: System configuration and pathway management
```

**Validates:** Override pattern changes node titles correctly.

#### Test 3.4: Verify Add Customization
```bash
PYTHONPATH=/home/GOD/heaven-tree-repl python3 test_with_customizations.py "jump my_custom_node"
```

**Expected Output:**
```
# 🎯 My Custom Feature Menu
Description: This is a custom node added via dev config
```

**Validates:** Add pattern creates new nodes with custom data.

#### Test 3.5: Verify Exclude Customization
```bash
PYTHONPATH=/home/GOD/heaven-tree-repl python3 test_with_customizations.py "jump search"
```

**Expected Output:**
```
# Unknown Menu
Description: No description available
```

**Validates:** Exclude pattern removes nodes from navigation.

#### Test 3.6: Navigation Tree with Customizations
```bash
PYTHONPATH=/home/GOD/heaven-tree-repl python3 test_with_customizations.py "nav"
```

**Expected Changes in Output:**
```
├── 🗺️ 0.1: 🚀 CUSTOM SYSTEM MENU (12 paths) - System configuration...
│   └── 🗺️ 0.1.1: 🎯 My Custom Feature (0 paths) - This is a custom node...
```
And search node should be missing from conversations section.

**Validates:** All customizations appear in navigation tree.

### Phase 4: System Config Isolation Testing

Test that system configs remain unchanged and dev configs only apply when specified.

#### Test 4.1: Default Shell (No Dev Config)
```bash
PYTHONPATH=/home/GOD/heaven-tree-repl python3 test_user_treeshell.py "jump 0.1"
```

**Expected Output:**
```
# Settings & Management Menu  
```

**Validates:** Without dev_config_path, original system config is used.

#### Test 4.2: Shell with Dev Config
```bash
PYTHONPATH=/home/GOD/heaven-tree-repl python3 test_with_customizations.py "jump 0.1"
```

**Expected Output:**
```
# 🚀 CUSTOM SYSTEM MENU Menu
```

**Validates:** With dev_config_path, customizations are applied.

### Phase 5: Pydantic Validation Testing

Test that all configs validate correctly with Pydantic models.

#### Test 5.1: SystemConfigLoader Validation
```python
from heaven_tree_repl.system_config_loader_v2 import SystemConfigLoader

# Test different config type combinations
config_combinations = [
    ["base"],
    ["base", "agent"], 
    ["base", "user"],
    ["base", "agent", "user"]
]

for config_types in config_combinations:
    loader = SystemConfigLoader(config_types=config_types)
    config = loader.load_and_validate_configs(dev_config_path=None)
    warnings = loader.get_validation_warnings()
    print(f"Config types {config_types}: {len(config)} keys, {len(warnings)} warnings")
```

**Expected Output:**
```
Config types ['base']: 6 keys, 0 warnings
Config types ['base', 'agent']: 10 keys, 0 warnings  
Config types ['base', 'user']: 10 keys, 0 warnings
Config types ['base', 'agent', 'user']: 10 keys, 0 warnings
```

**Validates:** All config combinations validate without warnings.

#### Test 5.2: Family Node Validation
Test that family nodes validate correctly with prompt/title equivalence:

```python
from heaven_tree_repl.config_models import BaseNode

# Test prompt field
node_data = {"type": "Menu", "prompt": "Test Menu", "description": "Test"}
validated = BaseNode(**node_data)
assert validated.prompt == "Test Menu"
assert validated.title == "Test Menu"

# Test title field  
node_data = {"type": "Menu", "title": "Test Menu", "description": "Test"}
validated = BaseNode(**node_data)
assert validated.prompt == "Test Menu"
assert validated.title == "Test Menu"
```

**Validates:** BaseNode model handles prompt/title equivalence correctly.

### Phase 6: Shell Type Testing

Test that all shell types support dev customizations.

#### Test 6.1: UserTreeShell with Dev Config
```python
from heaven_tree_repl.shells import UserTreeShell

shell = UserTreeShell(user_config_path="/tmp/heaven_data/user_interface_hub_v1_0/configs")
assert len(shell.nodes) > 0
assert shell.app_id == "user_interface_hub"
```

#### Test 6.2: AgentTreeShell with Dev Config
```python
from heaven_tree_repl.shells import AgentTreeShell

shell = AgentTreeShell(
    user_config_path="/tmp/heaven_data/user_interface_hub_v1_0/configs",
    session_id="test_agent"
)
assert len(shell.nodes) > 0
assert shell.role == "AI Agent"
```

#### Test 6.3: FullstackTreeShell with Dev Config
```python
from heaven_tree_repl.shells import FullstackTreeShell

shell = FullstackTreeShell(user_config_path="/tmp/heaven_data/user_interface_hub_v1_0/configs")
assert len(shell.nodes) > 0
assert shell.role == "AI Automation Emergence Engineer"
```

**Validates:** All shell types load dev customizations correctly.

## Expected Test Results

After running all tests, you should see:

### ✅ **Working Features:**
1. **Navigation System**: Tree navigation with proper titles (no None values)
2. **App Folder Management**: Versioned folders with correct dev templates
3. **Override Pattern**: Node titles changed via dev configs
4. **Add Pattern**: New custom nodes accessible
5. **Exclude Pattern**: Specified nodes removed from navigation  
6. **Config Isolation**: System configs unchanged, dev configs apply only when specified
7. **Pydantic Validation**: All configs validate without warnings
8. **Shell Type Support**: All shell types support dev customizations
9. **File-path Semantic Addressing**: Precise node targeting works
10. **Library Updates**: System configs stay in library, receive updates

### ❌ **Common Issues and Debugging:**

**Issue: Nodes showing "None" titles**
- **Cause**: BaseNode Pydantic model not handling prompt/title equivalence
- **Fix**: Ensure `@model_validator(mode='before')` handles both fields

**Issue: Dev customizations not applied**
- **Cause**: `user_config_path` not passed or wrong path
- **Fix**: Pass correct dev config directory path to shell constructor

**Issue: Validation warnings**
- **Cause**: Config file format doesn't match Pydantic models
- **Fix**: Check config file JSON structure matches model expectations

**Issue: App folder not created**
- **Cause**: HEAVEN_DATA_DIR not set or not writable
- **Fix**: Set environment variable and check permissions

## Debugging Commands

```bash
# Check app folder contents
ls -la /tmp/heaven_data/user_interface_hub_v1_0/configs/

# Verify dev config format
cat /tmp/heaven_data/user_interface_hub_v1_0/configs/dev_base_config.json

# Test specific node data
PYTHONPATH=/home/GOD/heaven-tree-repl python3 -c "
from heaven_tree_repl.shells import UserTreeShell
shell = UserTreeShell(user_config_path='/tmp/heaven_data/user_interface_hub_v1_0/configs')
print(shell.nodes.get('my_custom_node'))
"

# Check validation warnings
PYTHONPATH=/home/GOD/heaven-tree-repl python3 -c "
from heaven_tree_repl.system_config_loader_v2 import SystemConfigLoader
loader = SystemConfigLoader(config_types=['base', 'user'])
loader.load_and_validate_configs('/tmp/heaven_data/user_interface_hub_v1_0/configs')
print(loader.get_validation_warnings())
"
```

## Success Criteria

The 19-config system passes all tests when:

1. ✅ Navigation shows proper node titles (no None values)
2. ✅ Dev customizations (override/add/exclude) work correctly
3. ✅ System configs remain in library, dev configs in user directory
4. ✅ All shell types support dev customizations  
5. ✅ Pydantic validation passes without warnings
6. ✅ App folders created with correct templates
7. ✅ File-path-based semantic addressing works
8. ✅ Config isolation works (dev configs only apply when specified)

When all tests pass, the 19-config system is fully functional and ready for production use.