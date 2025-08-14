# HEAVEN TreeShell Config Architecture

## Overview

TreeShell uses a 6-level configuration system that separates **system defaults** (controlled by the library) from **user customizations** (controlled by the user). This enables library evolution while preserving user modifications.

## Core Philosophy

- **System configs**: Always loaded fresh from the library package (automatic updates)
- **User configs**: Persistent customizations stored in HEAVEN_DATA_DIR 
- **Override pattern**: User configs use structured override/add/exclude instead of flat replacement

## Configuration Files (17 Total)

### Main Configs (6)
| System (Library) | User (HEAVEN_DATA_DIR) | Purpose |
|------------------|------------------------|---------|
| `system_base_config.json` | `user_base_config.json` | Core TreeShell foundation |
| `system_agent_config.json` | `user_agent_config.json` | Agent shell capabilities |
| `system_user_config.json` | `user_user_config.json` | User shell features |

### Shortcuts (6)
| System (Library) | User (HEAVEN_DATA_DIR) | Purpose |
|------------------|------------------------|---------|
| `system_base_shortcuts.json` | `user_base_shortcuts.json` | Core navigation shortcuts |
| `system_agent_shortcuts.json` | `user_agent_shortcuts.json` | Agent-specific shortcuts |
| `system_user_shortcuts.json` | `user_user_shortcuts.json` | User interface shortcuts |

### Zone Configs (4)
| System (Library) | User (HEAVEN_DATA_DIR) | Purpose |
|------------------|------------------------|---------|
| `system_agent_zone_config.json` | `user_agent_zone_config.json` | Agent shell zones/tutorials |
| `system_user_zone_config.json` | `user_user_zone_config.json` | User shell zones/interfaces |

### Navigation (1)
| File | Location | Purpose |
|------|----------|---------|
| `nav_config.json` | User controlled | Family ordering and coordinate mapping |

## User Config Structure

User configs use a structured override pattern instead of flat replacement:

```json
{
  "override_nodes": {
    "system.omnitool.execute_tool": {
      "prompt": "My Custom Tool Executor",
      "description": "Customized for my workflow"
    }
  },
  "add_nodes": {
    "my_custom_chat_tool": {
      "type": "Callable",
      "prompt": "Chat Handler",
      "function_name": "handle_chat"
    }
  },
  "exclude_nodes": [
    "system.some_tool_i_dont_want"
  ],
  "app_id": "my_custom_app"
}
```

## Loading Priority

1. **Load system config** from library package (always fresh)
2. **Load user config** from HEAVEN_DATA_DIR (if exists)
3. **Apply user overrides** to system config
4. **Add user nodes** to final config
5. **Exclude specified nodes** from final config

## Shell Loading Patterns

### AgentTreeShell
```python
base_config = load_config_layer("base")
agent_config = load_config_layer("agent") 
final_config = merge_configs(base_config, agent_config)
```

### UserTreeShell
```python
base_config = load_config_layer("base")
user_config = load_config_layer("user")
final_config = merge_configs(base_config, user_config)
```

### FullstackTreeShell
```python
base_config = load_config_layer("base")
agent_config = load_config_layer("agent")
user_config = load_config_layer("user")
final_config = merge_configs(base_config, agent_config, user_config)
```

## Benefits

- **Library evolution**: System configs update automatically
- **User customization**: Persistent user modifications
- **Clean separation**: Clear boundary between system and user concerns
- **Backwards compatibility**: Existing behavior preserved
- **Conflict resolution**: Structured overrides prevent accidental breakage

## Migration Plan

1. **Rename current configs** to `system_*` versions
2. **Create user config templates** with override/add/exclude structure
3. **Update loading logic** in `base.py` to support 6-level system
4. **Update shell constructors** to use new config merging
5. **Remove system config copying** from `_initialize_heaven_data_dir()`
6. **Test config loading** and merging behavior

## Implementation Status

- [ ] Rename current configs to system versions
- [ ] Create user config templates
- [ ] Implement 6-level loading logic
- [ ] Update shell constructors
- [ ] Remove config copying from initialization
- [ ] Test and validate behavior

## Shell Class Architecture & Config Path Discovery

### System Config Loading Built Into Shell Classes

Shell classes have a **loader attribute** that automatically loads their system-level configurations from the library package:

```python
class AgentTreeShell(TreeShell):
    def __init__(self, user_config_path: str = None, session_id: str = None):
        # Loader automatically loads system configs from library
        self.system_config_loader = SystemConfigLoader(
            config_types=["base", "agent"]
        )
        
        # System configs loaded from library package (always fresh)
        system_config = self.system_config_loader.load_system_configs()
        
        # User configs only loaded if path provided and configs exist
        if user_config_path:
            user_config = self._load_user_configs_from_path(user_config_path)
            final_config = self._apply_user_customizations(system_config, user_config)
        else:
            final_config = system_config  # Pure system defaults
        
        super().__init__(final_config)
```

### Developer Usage Pattern

Developers specify a **config path** where their app-specific user configs live:

```python
# Using system defaults only
agent = AgentTreeShell()

# With app-specific customizations
agent = AgentTreeShell(user_config_path="/my_chat_app/configs/")
```

### Config Path Discovery

When a config path is provided, the shell looks for user configs in that directory:

```
/my_chat_app/configs/
├── user_base_config.json      # Base customizations (optional)
├── user_agent_config.json     # Agent customizations (optional)  
├── user_base_shortcuts.json   # Custom shortcuts (optional)
├── user_agent_zone_config.json # Zone customizations (optional)
└── nav_config.json            # Navigation structure (optional)
```

**Only configs that exist are loaded** - missing files are ignored and system defaults used.

### Benefits of This Approach

- **Zero config startup**: `AgentTreeShell()` works immediately with system defaults
- **App-specific customization**: Each app can have its own config directory  
- **Selective customization**: Apps only override what they need to change
- **Library updates automatic**: System configs loaded fresh from library package
- **No global state**: Each app's configs are isolated to their chosen path

### Config Storage Locations

**System Configs:** Stored as library-level data files in the heaven-tree-repl package
- `system_base_config.json`, `system_agent_config.json`, etc.
- Always loaded fresh from the library package
- Updated automatically when library is updated

**User Configs:** Stored in app-specific paths provided by developers
- `user_base_config.json`, `user_agent_config.json`, etc. 
- Located wherever the developer specifies via `user_config_path`
- Persistent across library updates

**Nav Config Exception:** `nav_config.json` is the only config that must be saved in HEAVEN_DATA_DIR
- Controls coordinate mapping and family ordering
- Needs to persist in a standard location for session continuity
- User has direct control over this file

### Session Persistence Considerations

The current session saving mechanism may need adjustment since:

1. **System configs** are loaded from library package (not HEAVEN_DATA_DIR)
2. **User configs** come from app-specified paths (not HEAVEN_DATA_DIR)
3. **Nav config** remains in HEAVEN_DATA_DIR for coordinate stability
4. **Session state** still needs to persist somewhere accessible

Potential solution: Use HEAVEN_DATA_DIR for session state and nav config, while allowing app-specific paths for all other user customizations.