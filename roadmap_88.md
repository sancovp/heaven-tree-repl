# Roadmap 88: TreeShell Configuration Architecture

## Current Problem

The TreeShell architecture incorrectly mixes framework code with default app configuration. The base.py file hardcodes nodes in Python instead of properly loading JSON configurations, which prevents proper layering and separation of concerns.

## Correct Architecture

The TreeShell system should use a layered configuration approach with separate default configs for different shell types:

### Base TreeShell
- Loads `base_default_config.json`
- Contains universal nodes (meta operations, omnitool, brain management, etc.)
- Functions defined in separate utility modules, not hardcoded in base.py
- This is ONLY what both agent and user tree shells have access to

### AgentTreeShell
- Loads `agent_default_config.json` ON TOP of base config
- Contains agent-specific nodes (quarantine restrictions, etc.)
- Anything specific to agent shells but generally available in all agent shells

### UserTreeShell  
- Loads `user_default_config.json` ON TOP of base config
- Contains user-specific nodes (agent management, approval workflows, etc.)
- Anything specific to user shells but generally available in all user shells

### FullstackTreeShell
- Combines all three: base + agent + user configs
- Gets the full feature set from all layers
- Default config is just the bundle of the other three configs

## Implementation Steps

1. **Extract hardcoded nodes from base.py**
   - Move all node definitions from base.py into `base_default_config.json`
   - base.py should only contain framework code

2. **Create utility modules for node functions**
   - Move all base node functions to separate utility modules
   - Functions referenced in JSON configs via import_path/import_object

3. **Implement config layering system**
   - Modify base.py to load JSON configs in layers
   - Each shell type loads its default config on top of lower layers

4. **Create separate default configs**
   - `base_default_config.json` - Universal TreeShell functionality
   - `agent_default_config.json` - Agent-specific features  
   - `user_default_config.json` - User-specific features

5. **Add brain management to appropriate config**
   - Brain management should go in whichever default config makes sense for the feature scope
   - Likely base config since it's universal functionality

## Benefits

- Clean separation between framework and configuration
- Proper layering allows customization at each level
- Apps can override defaults at any layer
- Modular architecture supports different shell types
- Framework code stays separate from app logic

## Config Loading Order

1. `base_default_config.json` (universal features)
2. `agent_default_config.json` OR `user_default_config.json` (shell-specific)
3. `fullstack_default_config.json` (if using FullstackTreeShell)
4. App-specific config (passed to constructor)

Each layer can override or extend the previous layers.