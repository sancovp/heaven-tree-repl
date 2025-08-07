# HEAVEN Tree REPL

Hierarchical Embodied Autonomously Validating Evolution Network Tree REPL - A modular tree navigation system with persistent state, pathway recording, and agent management capabilities.

## Features

- **Geometric Tree Navigation**: Navigate through hierarchical structures using coordinate-based addressing (0.1.2.3)
- **Live Variable Persistence**: Session variables persist throughout navigation and execution
- **Pathway Recording & Templates**: Record navigation sequences and convert them to reusable templates
- **RSI Analysis**: Pattern recognition, crystallization, and optimization insights
- **Agent Management**: Support for both user-level and agent-level tree shells with approval workflows
- **Modular Architecture**: Clean separation of concerns with mixin-based design

## Installation

```bash
pip install heaven-tree-repl
```

## Quick Start

```python
from heaven_tree_repl import TreeShell

# Create a basic tree configuration
config = {
    "app_id": "my_app",
    "domain": "example",
    "role": "assistant",
    "nodes": {
        "root": {
            "type": "Menu",
            "prompt": "Main Menu",
            "description": "Root menu",
            "options": {
                "1": "math_ops"
            }
        },
        "math_ops": {
            "type": "Callable",
            "prompt": "Math Operations",
            "description": "Perform mathematical operations",
            "function_name": "_test_add",
            "args_schema": {"a": "int", "b": "int"}
        }
    }
}

# Initialize TreeShell
shell = TreeShell(config)

# Navigate and execute
response = shell.handle_command("1")  # Navigate to math_ops
response = shell.handle_command('1 {"a": 5, "b": 3}')  # Execute with args
```

## Architecture

The system is built using a modular mixin architecture:

- **TreeShellBase**: Core navigation and state management
- **MetaOperationsMixin**: Variable management and session operations
- **PathwayManagementMixin**: Recording, saving, and template analysis
- **CommandHandlersMixin**: Navigation and interaction commands
- **RSIAnalysisMixin**: Pattern recognition and crystallization
- **ExecutionEngineMixin**: Core action execution
- **AgentManagementMixin**: Agent and user tree repl classes

## Agent Support

The system supports both user-level and agent-level interactions:

```python
from heaven_tree_repl import UserTreeShell, AgentTreeShell

# User shell with approval capabilities
user_shell = UserTreeShell()

# Agent shell with quarantine restrictions
agent_shell = AgentTreeShell(config, session_id="agent_001", 
                            approval_callback=user_shell._receive_agent_approval_request)
```

## Development Roadmap

See `docs/DEVELOPMENT_ROADMAP.md` for the complete phased development plan:

1. **Phase 1**: Prompt Engineering Agent Prototype (Current)
2. **Phase 2**: General Adaptor Layer 
3. **Phase 3**: Universal Agent App Generator
4. **Phase 4**: Game Mechanics Integration
5. **Phase 5**: Enhanced Base Library
6. **Phase 6**: Advanced Integrations (MCP, Full HEAVEN)

Future game mechanics specifications are in `docs/future_implementations/`.

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/heaven-tree-repl.git
cd heaven-tree-repl

# Install in development mode
pip install -e .[dev]

# Run tests
pytest
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.# Domain chain system implemented
