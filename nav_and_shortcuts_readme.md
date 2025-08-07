# Navigation and Shortcuts Guide

This guide covers the powerful navigation and shortcut systems in HEAVEN TreeShell.

## 🗺️ Navigation Overview (`nav` command)

The `nav` command displays the complete tree structure with beautiful ASCII art and ontological emoji classification.

### Usage
```bash
nav
```

### Features
- **ASCII Tree Structure** - Visual hierarchy with proper branches (`├──`, `└──`, `│`)
- **Ontological Emoji DSL** - Semantic classification of every node
- **Numerical Sorting** - Coordinates sorted properly (1, 2, 3... 10, 11, 12)
- **Complete Overview** - See all 47+ nodes at once
- **Summary Statistics** - Total nodes, crystal hubs, active gears, max depth

### Ontological Emoji DSL

Each emoji represents a semantic category:

| Emoji | Meaning | Examples |
|-------|---------|----------|
| 🔮 | Root crystal | Main entry point (0) |
| 🧠 | Brain/AI domain | Brain Management, Brain Agent Query |
| 📜 | Documentation domain | Help, guides, references |
| 🚀 | Generation/creation domain | MCP Server Generator |
| 🛠️ | Tools/utilities domain | OmniTool Access |
| 🌀 | Meta/system operations domain | Meta Operations, variables |
| 🤖 | Agent systems domain | Agent-specific functionality |
| 🗺️ | General navigation hub | Settings & Management |
| ⚙️ | Executable function (universal) | All callable functions |

### Example Output
```
🔮 0: Main Menu (3 paths) - Root menu for interactive_repl
├── 🗺️ 0.0: Settings & Management (7 paths) - System configuration and pathway management
│   ├── ⚙️ 0.0.1: Manage Pathways (_manage_pathways) - View and manage saved pathways
│   ├── 🌀 0.0.2: Meta Operations (14 paths) - State management and session operations
│   │   ├── ⚙️ 0.0.2.1: Save Variable (_meta_save_var) - Store value in session variables
│   │   ├── ⚙️ 0.0.2.2: Get Variable (_meta_get_var) - Retrieve session variable value
│   │   └── ⚙️ 0.0.2.3: Append to Variable (_meta_append_to_var)
│   ├── 🧠 0.0.6: 🧠 Brain Management (5 paths) - Create and manage knowledge brains
│   │   ├── ⚙️ 0.0.6.1: Setup System Brains (_brain_setup_system_brains)
│   │   └── ⚙️ 0.0.6.2: Create Brain from GitHub (_brain_create_from_github)
│   └── 🧠 0.0.7: 🤖 Brain Agent Query (4 paths)
└── 📜 0.2: 📚 Documentation (6 paths)
    ├── ⚙️ 0.2.1: Execution Syntax (_docs_execution_syntax)
    └── ⚙️ 0.2.2: Callable Nodes (_docs_callable_nodes)
```

## 🔗 Shortcut System

Create semantic aliases for navigation and execution. Two types: **Jump Shortcuts** and **Chain Shortcuts**.

### Jump Shortcuts (Simple Navigation)

Navigate directly to any coordinate with a memorable alias.

#### Creating Jump Shortcuts
```bash
shortcut <alias> <coordinate>
```

#### Examples
```bash
shortcut brain 0.0.6           # Navigate to Brain Management
shortcut docs 0.2              # Navigate to Documentation  
shortcut tools 0.0.4           # Navigate to OmniTool Access
shortcut meta 0.0.2            # Navigate to Meta Operations
shortcut syntax 0.2.1          # Navigate to Execution Syntax docs
```

#### Using Jump Shortcuts
```bash
brain                          # → jump 0.0.6
docs                           # → jump 0.2
tools                          # → jump 0.0.4
```

### Chain Shortcuts (Template Execution)

Execute chain templates with variable substitution. Can be single steps or multi-step workflows.

#### Creating Chain Shortcuts
```bash
shortcut <alias> "<chain_template>"
```

#### Unconstrained Examples (No Variables)
```bash
shortcut list_vars "0.0.2.5 {}"                    # List all variables
shortcut stats "0.0.2.9 {}"                        # Show session stats  
shortcut workflow "0.0.2.5 {} -> 0.0.2.9 {}"      # Multi-step: list vars then stats
```

#### Constrained Examples (With Variables)
```bash
shortcut save_var "0.0.2.1 {\"name\": \"$var_name\", \"value\": \"$var_value\"}"
shortcut load_file "0.0.2.7 {\"filename\": \"$file\", \"var_name\": \"$var\"}"
shortcut brain_query "0.0.7.1 {\"brain_name\": \"$brain\", \"query\": \"$question\"}"
```

#### Using Chain Shortcuts

**Unconstrained shortcuts** (execute immediately):
```bash
list_vars                      # Execute: 0.0.2.5 {}
stats                          # Execute: 0.0.2.9 {}
workflow                       # Execute multi-step chain
```

**Constrained shortcuts** (require arguments):
```bash
save_var {"var_name": "config", "var_value": "production"}
load_file {"file": "data.json", "var": "my_data"}  
brain_query {"brain": "docs", "question": "How does this work?"}
```

### Template Variable Substitution

Variables in chain templates use `$variable_name` format:

```bash
# Template with variables
"0.0.2.1 {\"name\": \"$var_name\", \"value\": \"$var_value\"}"

# When called with args
save_var {"var_name": "test", "var_value": "hello"}

# Becomes
"0.0.2.1 {\"name\": \"test\", \"value\": \"hello\"}"
```

### Shortcut Management

#### List All Shortcuts
```bash
shortcuts
```

Shows both jump and chain shortcuts with their types and requirements:

```
# 🔗 Active Shortcuts (5)

## 🎯 Jump Shortcuts
brain           → 0.0.6    (🧠 Brain Management)
docs            → 0.2      (📚 Documentation)
tools           → 0.0.4    (🛠️ OmniTool Access)

## ⛓️ Chain Shortcuts  
save_var        → Chain (constrained) - requires: var_name, var_value
list_vars       → Chain (unconstrained) - no args needed
```

#### Shortcut Storage
- Shortcuts are stored in session variables under `_shortcuts`
- Persist for the entire TreeShell session
- Lost when session ends (use pathways for permanent storage)

## 🎯 Navigation Best Practices

### Discovery Workflow
1. **Start with `nav`** - Get the complete overview
2. **Create jump shortcuts** - For frequently visited areas
3. **Create chain shortcuts** - For common workflows
4. **Use `shortcuts`** - Remember what you've created

### Common Shortcuts to Create
```bash
# Essential navigation
shortcut home 0                # Back to main menu
shortcut brain 0.0.6           # Brain management
shortcut docs 0.2              # Documentation
shortcut vars 0.0.2.5          # Quick variable list

# Useful workflows  
shortcut save "0.0.2.1 {\"name\": \"$name\", \"value\": \"$value\"}"
shortcut load "0.0.2.7 {\"filename\": \"$file\", \"var_name\": \"$var\"}"
shortcut query "0.0.7.1 {\"brain_name\": \"$brain\", \"query\": \"$question\"}"
```

### Advanced Patterns

#### Multi-Step Workflows
```bash
# Save variables then export session
shortcut backup "0.0.2.1 {\"name\": \"$key\", \"value\": \"$data\"} -> 0.0.2.8 {\"filename\": \"backup.json\"}"

# Query brain then deepen the response
shortcut deep_query "0.0.7.1 {\"brain_name\": \"$brain\", \"query\": \"$question\"} -> 0.0.7.2 {\"previous_answer\": \"$step1_result\", \"original_query\": \"$question\"}"
```

#### Error Handling
- **Invalid coordinates**: System validates coordinates exist before creating shortcuts
- **Missing arguments**: Constrained shortcuts show required args in error messages
- **Bad JSON**: Clear error messages for malformed arguments

## 🚀 Pro Tips

1. **Use `nav` frequently** - Discover new capabilities and remember coordinates
2. **Create semantic aliases** - Use meaningful names like `brain`, `docs`, `save`
3. **Chain single steps** - Even single functions benefit from argument templates
4. **Combine with pathways** - Shortcuts for quick access, pathways for permanent workflows
5. **Check `shortcuts` regularly** - Remember what aliases you've created

## 🎮 Crystal Forest Game Integration

The navigation system embodies the "Crystal Forest Game" concept:

- **🔮 Crystals** represent navigation hubs with different powers
- **⚙️ Gears** are the active mechanisms you can trigger  
- **ASCII branches** show the paths between different areas
- **Shortcuts** are like teleportation spells you learn
- **Chains** are combo moves that execute multiple actions

Navigate the forest, learn its secrets, and create your own magical shortcuts! 🌳✨