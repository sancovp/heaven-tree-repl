"""
HEAVEN Tree REPL Shell Classes

Core shell implementations for different TreeShell types:
- TreeShell: Complete base shell with all features
- AgentTreeShell: Agent-level shell with quarantine restrictions  
- UserTreeShell: User-level shell with agent management capabilities
- FullstackTreeShell: Complete fullstack shell supporting nested interactions
"""

from .base import TreeShellBase
from .meta_operations import MetaOperationsMixin
from .pathway_management import PathwayManagementMixin
from .command_handlers import CommandHandlersMixin
from .rsi_analysis import RSIAnalysisMixin
from .execution_engine import ExecutionEngineMixin
from .agent_management import AgentTreeReplMixin, UserTreeReplMixin, TreeReplFullstackMixin


class TreeShell(
    TreeShellBase,
    MetaOperationsMixin,
    PathwayManagementMixin,
    CommandHandlersMixin,
    RSIAnalysisMixin,
    ExecutionEngineMixin
):
    """
    Complete TreeShell implementation combining all modules.
    
    Provides geometric tree navigation with live variable persistence,
    pathway recording and templates, RSI analysis, and comprehensive
    command handling.
    """
    
    def __init__(self, graph_config: dict):
        """Initialize TreeShell with graph configuration."""
        super().__init__(graph_config)
    
    def _manage_pathways(self, final_args: dict) -> tuple:
        """Show pathway management interface."""
        pathways_info = {
            "saved_pathways": len(self.saved_pathways),
            "saved_templates": len(self.saved_templates),
            "pathway_list": list(self.saved_pathways.keys()),
            "ontology_domains": len(self.graph_ontology["domains"]),
            "crystallization_history": len(self.graph_ontology["crystallization_history"])
        }
        
        return pathways_info, True
    
    def _meta_list_shortcuts(self, final_args: dict) -> tuple:
        """List all active shortcuts with details."""
        # Get shortcuts directly and format properly for display
        shortcuts = self.session_vars.get("_shortcuts", {})
        
        if not shortcuts:
            result = "**No shortcuts defined yet.**\n\n" + \
                    "**Jump shortcuts:** `shortcut <alias> <coordinate>`\n" + \
                    "**Chain shortcuts:** `shortcut <alias> \"<chain_template>\"`"
            return result, True
        
        # Format shortcuts as readable markdown
        parts = []
        parts.append(f"# 🌳 TreeShell Language Reference\n")
        
        # Language structure overview
        parts.append("## 🗣️ Language Structure")
        parts.append("TreeShell is a **semantic programming language** with coordinate-based addressing:")
        parts.append("- **Words** = shortcuts (semantic aliases for coordinates and workflows)")
        parts.append("- **Grammar** = operands (and, or, if, while) + chain syntax (->)")
        parts.append("- **Execution** = node-based computation with data flow")
        parts.append("- **Vocabulary** = your custom shortcuts + base command set")
        parts.append("")
        
        parts.append(f"## 🔗 Active Words/Shortcuts ({len(shortcuts)})\n")
        
        # Separate jump and chain shortcuts
        jump_shortcuts = {}
        chain_shortcuts = {}
        
        for alias, shortcut in shortcuts.items():
            if isinstance(shortcut, dict):
                shortcut_type = shortcut.get("type", "jump")
                if shortcut_type == "jump":
                    coordinate = shortcut["coordinate"]
                    node = self.nodes.get(coordinate, {})
                    jump_shortcuts[alias] = {
                        "coordinate": coordinate,
                        "target": node.get("prompt", "Unknown"),
                        "description": node.get("description", "")
                    }
                elif shortcut_type == "chain":
                    analysis = shortcut.get("analysis", {})
                    chain_shortcuts[alias] = {
                        "template": shortcut["template"],
                        "template_type": analysis.get("type", "unconstrained"),
                        "required_args": analysis.get("entry_args", [])
                    }
        
        # Render jump shortcuts
        if jump_shortcuts:
            parts.append("## 🎯 Jump Shortcuts\n")
            for alias, info in jump_shortcuts.items():
                parts.append(f"**{alias}** → `{info['coordinate']}` ({info['target']})")
            parts.append("")
        
        # Render chain shortcuts
        if chain_shortcuts:
            parts.append("## ⛓️ Chain Shortcuts\n")
            for alias, info in chain_shortcuts.items():
                required_args = info["required_args"]
                args_str = f"requires: {', '.join(required_args)}" if required_args else "no args needed"
                parts.append(f"**{alias}** → Chain ({info['template_type']}) - {args_str}")
            parts.append("")
        
        # Language syntax
        parts.append("## 📝 Language Syntax")
        parts.append("**Simple Commands:** Direct execution")
        parts.append("- `jump <coordinate>` | `back` | `menu` | `exit`")
        parts.append("- `<shortcut>` → execute shortcut directly")
        parts.append("- `nav` | `lang` → system introspection")
        parts.append("")
        
        parts.append("**Chain Language:** Complex workflows with data flow")
        parts.append("- `chain step1 {} -> step2 {\"data\": \"$step1_result\"}` → sequential execution")
        parts.append("- **Shortcuts in chains:** `chain settings {} -> docs {}` ✓")  
        parts.append("- **Mixed syntax:** `chain brain {} -> 0.0.2.5 {} -> save_config {}`")
        parts.append("- **Data variables:** `$step1_result`, `$step2_result`, `$last_result`")
        parts.append("")
        
        parts.append("**Control Flow Grammar:** ✅ NOW IMPLEMENTED!")
        parts.append("- `and` → also execute with existing data")
        parts.append("- `or` → alternative execute with existing data") 
        parts.append("- `if condition then ... else ...` → conditional execution")
        parts.append("- `while condition x body` → loop execution")
        parts.append("- **TreeShell is TURING COMPLETE!** 🎉")
        parts.append("")
        
        # Base commands
        parts.append("## 🎮 Base Command Vocabulary")
        parts.append("- **Pathways:** `build_pathway` | `save_emergent_pathway <name>`")
        parts.append("- **History:** `show_execution_history` | `follow_established_pathway`")
        parts.append("- **Analysis:** `analyze_patterns` | `crystallize_pattern <name>`")
        
        # Management commands  
        parts.append("\n## 🛠️ Shortcut Management")
        parts.append("- **Create jump shortcut:** `shortcut <alias> <coordinate>`")
        parts.append("- **Create chain shortcut:** `shortcut <alias> \"<chain_template>\"`")
        parts.append("- **List shortcuts:** `lang` or `shortcuts` command")
        parts.append("- **Documentation:** `shortcuts` (jump to 0.2.7)")
        
        # Usage examples
        parts.append("\n## 💡 Usage Examples")
        parts.append("- **Jump:** `brain` → navigate to Brain Management")  
        parts.append("- **Chain:** `save {\"name\": \"key\", \"value\": \"data\"}` → execute with args")
        parts.append("- **Create:** `shortcut meta 0.0.2` → create jump shortcut")
        parts.append("- **Create:** `shortcut query \"0.0.7.1 {\\\"brain\\\": \\\"$brain\\\", \\\"query\\\": \\\"$question\\\"}\"` → chain shortcut")
        parts.append(f"\n*Total: {len(shortcuts)} shortcuts available*")
        
        result = "\n".join(parts)
        return result, True
    
    # === Documentation Functions ===
    
    def _docs_execution_syntax(self, final_args: dict) -> tuple:
        """Show execution syntax documentation."""
        docs = """📋 **Execution Syntax Guide**

When executing callable nodes, use these argument patterns:

**With Arguments (Dictionary):**
• `1 {"name": "Alice", "age": 30}` → calls func({"name": "Alice", "age": 30})
• `1 {"message": "Hello World"}` → calls func({"message": "Hello World"})

**Empty Arguments (Empty Dictionary):**  
• `1 {}` → calls func({}) - function receives empty dict

**No Arguments (Empty Parentheses):**
• `1 ()` → calls func() - function called with zero arguments
• Use this for functions like os.getcwd() that take no parameters

**Examples:**
• Math function: `1 {"a": 5, "b": 3}`
• Status check: `1 {}`  
• Get directory: `1 ()`

**Jump with Arguments:**
• `jump 0.1.5 {"data": "value"}` → navigate and execute with args
• `jump 0.1.5 ()` → navigate and execute with no args"""
        
        return docs, True
    
    def _docs_callable_nodes(self, final_args: dict) -> tuple:
        """Show callable nodes documentation."""
        docs = """🔧 **Callable Nodes Guide**

Create callable nodes using add_node (0.0.2.10) with 3 approaches:

**1. Import Existing Function:**
```json
{
  "type": "Callable",
  "prompt": "Get Directory", 
  "function_name": "_get_dir",
  "is_async": false,
  "import_path": "os",
  "import_object": "getcwd"
}
```

**2. Dynamic Function Code:**
```json
{
  "type": "Callable",
  "prompt": "System Info",
  "function_name": "_sys_info", 
  "is_async": false,
  "function_code": "def _sys_info(args): import os; return f'Dir: {os.getcwd()}', True"
}
```

**3. Use Existing Function:**
```json
{
  "type": "Callable",
  "prompt": "List Variables",
  "function_name": "_meta_list_vars",
  "is_async": false
}
```

**Required Fields:**
• `type`: "Callable"
• `prompt`: Display name
• `function_name`: Internal function name
• `is_async`: true/false for async handling

**Execution:** Use syntax from 0.2.1 (Execution Syntax)"""
        
        return docs, True
    
    def _docs_navigation(self, final_args: dict) -> tuple:
        """Show navigation documentation.""" 
        docs = """🧭 **Navigation Commands**

**Basic Navigation:**
• `1`, `2`, `3` → Navigate to menu options
• `back` → Go back one level
• `menu` → Go to nearest menu (find closest .0 node)
• `exit` → Exit TreeShell

**Jump Commands:**
• `jump 0.1.5` → Navigate directly to coordinate
• `jump 0.1.5 {"arg": "value"}` → Navigate and execute with args
• `jump 0.1.5 ()` → Navigate and execute with no args

**Chain Execution:**
• `chain 0.1.1 {} -> 0.1.2 {"data": "test"}` → Execute sequence
• Results from step1 available as variables in step2

**Universal Commands Available Everywhere:**
• jump, chain, build_pathway, save_emergent_pathway
• follow_established_pathway, show_execution_history
• analyze_patterns, crystallize_pattern, rsi_insights

**Coordinate System:**
• Every position has implicit .0 (menu/introspect)  
• 0 = root, 0.0 = settings, 0.1 = domain, 0.2 = docs
• Navigate hierarchically: 0 → 0.1 → 0.1.3 → 0.1.3.2"""
        
        return docs, True
    
    def _docs_pathways(self, final_args: dict) -> tuple:
        """Show pathway system documentation."""
        docs = """🛤️ **Pathway System**

**Recording Pathways:**
• `build_pathway` → Start recording your actions
• Navigate and execute commands (they get recorded)
• `save_emergent_pathway mypath` → Save recorded pathway

**From History:**
• `save_emergent_pathway_from_history mypath [0,1,2]` → Create from specific steps
• `save_emergent_pathway_from_history mypath [0-5]` → Create from range
• `show_execution_history` → See available steps

**Using Pathways:**
• `follow_established_pathway` → Show all pathways
• `follow_established_pathway mypath {"arg": "value"}` → Execute with args
• `follow_established_pathway domain=math` → Query by domain
• `follow_established_pathway tags=arithmetic` → Query by tags

**Analysis (RSI System):**
• `analyze_patterns` → Find optimization opportunities
• `crystallize_pattern mypattern` → Create reusable pattern
• `rsi_insights` → Show learning insights

**Pathway Management:** 
• Navigate to 0.0.1 for pathway management interface
• View saved pathways, templates, and ontology data"""
        
        return docs, True
    
    def _docs_meta_operations(self, final_args: dict) -> tuple:
        """Show meta operations documentation."""
        docs = """⚙️ **Meta Operations (0.0.2)**

**Session Variables:**
• `save_var` → Store value: {"name": "myvar", "value": "data"}
• `get_var` → Retrieve: {"name": "myvar"}  
• `append_to_var` → Add to list/string: {"name": "myvar", "value": "more"}
• `delete_var` → Remove: {"name": "myvar"}
• `list_vars` → Show all variables: {}

**File Operations:**
• `save_to_file` → Write var to file: {"filename": "data.json", "var_name": "myvar"}
• `load_from_file` → Read file to var: {"filename": "data.json", "var_name": "loaded"}
• `export_session` → Save complete session: {"filename": "session.json"}

**Tree Structure CRUD:**
• `add_node` → Create new nodes (see 0.2.2 for details)
• `update_node` → Modify existing: {"coordinate": "0.1.5", "updates": {...}}
• `delete_node` → Remove: {"coordinate": "0.1.5"}
• `list_nodes` → Show nodes: {"pattern": "0.1"} (optional filter)
• `get_node` → View details: {"coordinate": "0.1.5"}

**Session Info:**
• `session_stats` → Memory usage, variables, nodes count: {}

**MCP Generator:** Navigate to 0.0.3 for MCP server generation
**OmniTool Access:** Navigate to 0.0.4 for HEAVEN tool ecosystem"""
        
        return docs, True
    
    def _docs_computational_model(self, final_args: dict) -> tuple:
        """Show computational model documentation."""
        docs = """🧠 **Computational Model**

TreeShell achieves Turing completeness through three architectural layers:

**1. Self-Modification (CRUD Operations)**
• Tree structure operations allow runtime system evolution
• `add_node`, `update_node`, `delete_node` modify computational capabilities
• System can rewrite its own components and create new pathways
• Example: Agent creates a new workflow by adding connected callable nodes

**2. Hierarchical Agent Delegation**
```
FullstackTreeShell (orchestrator)
  ↓ spawns & manages
UserTreeShell (human approval layer)  
  ↓ spawns & monitors
AgentTreeShell (restricted execution environment)
```

• Each layer has different capabilities and restrictions
• Approval workflows create computational gates
• Quarantine system provides sandboxed execution
• Nested delegation enables complex multi-agent systems

**3. LLM-Powered Control Flow**
• AI agents provide arbitrary logical reasoning capabilities
• Natural language instructions → computational decisions
• If/then/else logic through agent reasoning: "if result contains error, retry with different parameters"
• While loops through pathway repetition: "keep processing until condition met"
• Dynamic branching: agents choose execution paths based on context

**Workflow Programming Language:**
TreeShell becomes a programming language where:
• **Nodes** = functions/procedures
• **Coordinates** = memory addresses  
• **Chains** = execution sequences with data flow
• **Pathways** = stored programs/procedures
• **Session variables** = persistent state
• **Tree CRUD** = self-modifying code capabilities
• **Agent reasoning** = dynamic control flow

**Example Turing-Complete Workflow:**
1. Agent analyzes data and creates processing nodes
2. Builds chain execution pipeline with conditional logic  
3. Records successful patterns as reusable pathways
4. System evolves by adding new capabilities through CRUD
5. Higher-level agents orchestrate multiple sub-agents

This creates an adaptive computational substrate where intelligent agents can dynamically build, modify, and orchestrate computational systems that extend their own capabilities."""
        
        return docs, True
    
    def _docs_shortcuts(self, final_args: dict) -> tuple:
        """Show shortcuts system documentation."""
        docs = """🔗 **Shortcuts System**

Create semantic aliases for coordinates and chain templates with layered persistent storage.

**Jump Shortcuts (Simple Navigation):**
• `shortcut brain 0.0.6` → Create alias 'brain' for coordinate 0.0.6
• `shortcut docs 0.2` → Create alias 'docs' for documentation menu
• `brain` → Jump directly to 0.0.6 (Brain Management)
• `docs` → Jump directly to 0.2 (Documentation)

**Chain Shortcuts (Workflow Templates):**
• `shortcut save "0.0.2.1 {\\\"name\\\": \\\"$name\\\", \\\"value\\\": \\\"$value\\\"}"` → Template with variables
• `shortcut workflow "0.1.1 {} -> 0.1.2 {\\\"data\\\": \\\"$step1_result\\\"}"` → Multi-step chain
• `save {"name": "config", "value": "production"}` → Execute template with variables
• `workflow {}` → Execute multi-step chain

**Variable Substitution:**
Chain templates support variable substitution using `$variable_name` pattern:
• `$name`, `$value` → User-provided entry arguments (required)
• `$step1_result`, `$step2_result` → Automatic step result variables
• `$last_result` → Result from previous chain step

**Template Types:**
• **Unconstrained**: No variables, execute as-is
• **Constrained**: Requires specific entry arguments from user

**Layered Persistence:**
Shortcuts persist across sessions in JSON files with layered inheritance:

• **base_shortcuts.json**: Universal shortcuts (all TreeShell types)
• **system_agent_shortcuts.json**: System defaults for agent-specific shortcuts (AgentTreeShell + FullstackTreeShell)  
• **system_user_shortcuts.json**: System defaults for user-specific shortcuts (UserTreeShell + FullstackTreeShell)
• **FullstackTreeShell**: Loads all three layers (base → agent → user)

**Management Commands:**
• `shortcuts` → List all active shortcuts with details
• `shortcut <alias> <coordinate>` → Create jump shortcut
• `shortcut <alias> "<chain_template>"` → Create chain shortcut template
• `nav` → Show all coordinates for shortcut creation

**Examples:**
```
# Simple navigation shortcuts
shortcut meta 0.0.2
shortcut brain 0.0.6
shortcut gen 0.0.3

# Workflow shortcuts with variables  
shortcut save "0.0.2.1 {\\\"name\\\": \\\"$name\\\", \\\"value\\\": \\\"$value\\\"}"
shortcut query "0.0.7.1 {\\\"brain_name\\\": \\\"$brain\\\", \\\"query\\\": \\\"$question\\\"}"

# Usage
meta           # Jump to meta operations
save {"name": "api_key", "value": "secret"}  # Execute save template
query {"brain": "treeshell", "question": "How do shortcuts work?"}
```

**Persistence Layers:**
Each TreeShell type automatically loads appropriate shortcut layers:
• **TreeShell/AgentTreeShell**: base + agent shortcuts
• **UserTreeShell**: base + user shortcuts  
• **FullstackTreeShell**: base + agent + user shortcuts (all layers)

Create shortcuts once, use them everywhere with consistent semantic navigation."""
        
        return docs, True
    
    def _docs_function_signatures(self, final_args: dict) -> tuple:
        """Show function signatures and auto-documentation guide."""
        docs = """📋 **Function Signatures & Auto-Documentation**

TreeShell automatically extracts and displays function signatures and docstrings using Python's `inspect` module, eliminating the need for manual documentation maintenance.

**Automatic Signature Extraction:**
• Function signatures are detected using `inspect.signature(function)`
• Parameter names, types, defaults, and return types are shown automatically
• Example: `equip_system_prompt(prompt: str) -> Tuple[str, bool]`

**Docstring Display:**
• Function docstrings are extracted using `function.__doc__`
• Displayed as the node description in TreeShell menus
• Example: "Equip a system prompt to the dynamic config."

**Graceful Fallbacks:**
• Missing signatures: `⚠️ Could not extract signature for function_name`
• Missing docstrings: `⚠️ No docstring available`
• Import failures: `⚠️ Could not display docstring for function_name`

**Function Discovery:**
TreeShell automatically finds functions in:
• Async registry (`self.async_functions`)
• Sync registry (`self.sync_functions`)
• Instance methods (`hasattr(self, function_name)`)
• Import on-demand via `import_path`/`import_object`

**Menu Display Example:**
```
📝 Equip System Prompt
Signature: equip_system_prompt(prompt: str) -> Tuple[str, bool]
Description: Equip a system prompt to the dynamic config.

Parameters:
  prompt (str): The system prompt text to equip
  
Returns:
  Tuple[str, bool]: Success message and status
```

**Benefits:**
• **Self-Documenting**: Functions document themselves
• **Always Accurate**: Can't get out of sync with code
• **Zero Maintenance**: No JSON metadata to maintain
• **Developer Friendly**: Encourages good docstring practices

**Technical Implementation:**
TreeShell uses `_get_function_docs()` method that:
1. Locates function in registries or imports it
2. Extracts signature with `inspect.signature()`
3. Extracts docstring with `function.__doc__`
4. Provides meaningful fallback messages for any failures

This system makes TreeShell a true "function browser" where you can navigate to discover what functions exist and exactly how to use them."""
        
        return docs, True
    
    def _docs_templating_system(self, final_args: dict) -> tuple:
        """Show templating system and variable injection guide."""
        docs = """🎯 **Templating System & Variable Injection**

TreeShell's `args_schema` system provides powerful templating capabilities for injecting session variables and formatting dynamic strings in function calls.

**Purpose: State Access for Functions**
Functions need access to TreeShell's internal state (selected agent, current user, etc.) without manual parameter passing. `args_schema` provides this through variable injection.

**1. Simple Variable Injection: `$variable_name`**
Injects entire values from session variables as function parameters.

```json
{
  "function_name": "start_chat",
  "args_schema": {
    "agent_config": "$selected_agent_config"
  }
}
```

**How it works:**
• User calls: `jump 0.4.1 {"title": "Test", "message": "Hello"}`
• TreeShell automatically adds: `agent_config: <HeavenAgentConfig object>`
• Function receives: `start_chat(title="Test", message="Hello", agent_config=<config>)`

**2. String Formatting: `{$variable_name}`**
Formats strings by substituting session variables into text templates.

```json
{
  "function_name": "create_prompt",
  "args_schema": {
    "system_prompt": "You are {$role} working on {$project_name}. Your task is {$current_task}."
  }
}
```

**Example substitution:**
• Session vars: `role="AI Assistant"`, `project_name="TreeShell MCP"`
• Result: `"You are AI Assistant working on TreeShell MCP. Your task is debugging."`

**3. Combined Usage:**
```json
{
  "args_schema": {
    "agent_config": "$selected_agent_config",
    "welcome_message": "Hello {$username}, you're using {$app_name}",
    "settings": "$user_preferences"
  }
}
```

**Variable Resolution Order:**
1. Special handling for `$selected_agent_config` (calls `_resolve_agent_config()`)
2. Session variables (`self.session_vars`)
3. Chain results (`self.chain_results`)
4. Keep original value if not found

**Template Execution Flow:**
1. **Merge**: User args + `args_schema` defaults
2. **Substitute**: Replace `$vars` and format `{$vars}` 
3. **Call**: Pass final args to function with intelligent calling

**Common Patterns:**

**Agent Context Injection:**
```json
"args_schema": {"agent_config": "$selected_agent_config"}
```

**User Personalization:**
```json
"args_schema": {"greeting": "Welcome {$username} to {$domain}!"}
```

**Dynamic Configuration:**
```json
"args_schema": {
  "api_key": "$current_api_key",
  "base_url": "$api_endpoint", 
  "prompt_template": "Context: {$context}\\nUser: {$user_input}\\nAssistant:"
}
```

**Error Handling:**
• Variables not found: Keep original `{$missing_var}` in output
• Invalid session state: Graceful fallbacks with warning messages
• Type mismatches: Convert to strings for formatting

**Best Practices:**
• Use `$variable` for object injection (configs, data structures)
• Use `{$variable}` for string templating (messages, prompts, paths)
• Keep `args_schema` focused on state access, not type hints
• Document expected session variables in function docstrings

This system enables functions to seamlessly access TreeShell's internal state while remaining pure, testable functions that work independently of the TreeShell context."""
        
        return docs, True
    
    def _docs_import_resolution(self, final_args: dict) -> tuple:
        """Show import resolution system guide.""" 
        docs = """🔧 **Import Resolution System**

TreeShell supports three approaches for implementing callable node functions: external imports, dynamic code compilation, and existing functions.

**1. External Module Import (Recommended)**
Import functions from external Python modules using `import_path` and `import_object`.

```json
{
  "type": "Callable",
  "function_name": "equip_system_prompt",
  "import_path": "heaven_tree_repl.agent_config_management",
  "import_object": "equip_system_prompt",
  "is_async": false
}
```

**How it works:**
• TreeShell executes: `from heaven_tree_repl.agent_config_management import equip_system_prompt`
• Function registered in appropriate registry (async/sync)
• Available for execution and signature extraction

**2. Dynamic Function Code**
Define functions directly in the node configuration using `function_code`.

```json
{
  "type": "Callable", 
  "function_name": "custom_calculator",
  "function_code": "def custom_calculator(a, b, operation):\\n    if operation == 'add':\\n        return a + b, True\\n    return 'Invalid operation', False",
  "is_async": false
}
```

**How it works:**
• TreeShell compiles code using `exec()` with enhanced globals
• Function has access to `self` (TreeShell instance)
• Registered in function registry for execution

**3. Existing Functions**
Reference functions that already exist in the TreeShell instance.

```json
{
  "type": "Callable",
  "function_name": "_test_add",
  "is_async": false
}
```

**Import Processing Flow:**

**During Node Building:**
1. TreeShell processes all callable nodes during `_build_coordinate_nodes()`
2. Calls `_process_callable_node()` for each callable node
3. Attempts import/compilation based on available fields
4. Registers functions in async/sync registries
5. Reports success/failure with detailed messages

**During Execution:**
1. TreeShell looks up function in registries first
2. If not found, attempts on-demand import using node metadata
3. Re-checks registries after import
4. Falls back to instance method lookup
5. Uses intelligent calling based on actual signature

**Import Resolution Priority:**
1. **Async Registry**: `self.async_functions[function_name]`
2. **Sync Registry**: `self.sync_functions[function_name]`  
3. **Instance Methods**: `hasattr(self, function_name)`
4. **On-Demand Import**: Using `import_path`/`import_object`

**Error Handling & Debugging:**

**Import Errors:**
```
Failed to import equip_tool from heaven_tree_repl.agent_config_management: No module named 'heaven_tree_repl.agent_config_management'
```

**Compilation Errors:**
```
Failed to compile function code: invalid syntax (<string>, line 1)
```

**Function Not Found:**
```
⚠️ Function custom_func not found in sync registry or as instance method
```

**Best Practices:**

**For Library Functions:**
```json
{
  "import_path": "mypackage.submodule", 
  "import_object": "my_function",
  "is_async": true
}
```

**For TreeShell Extensions:**
```json
{
  "import_path": "heaven_tree_repl.custom_tools",
  "import_object": "my_custom_tool", 
  "is_async": false
}
```

**For Quick Prototypes:**
```json
{
  "function_code": "def quick_test(data):\\n    return f'Processed: {data}', True"
}
```

**Advanced Features:**

**Async vs Sync Detection:**
• Set `"is_async": true` for async functions
• Set `"is_async": false` or omit for sync functions
• TreeShell handles calling convention automatically

**Function Registry Access:**
• Functions available across all TreeShell instances
• Persistent during session lifetime
• Can be listed via development tools

**On-Demand Loading:**
• Functions imported only when first needed
• Enables lazy loading of heavy dependencies
• Reduces startup time for complex applications

**Development Workflow:**
1. **Write Function**: Create in separate module with proper docstring
2. **Configure Node**: Add import_path/import_object to JSON
3. **Test Import**: TreeShell shows import success/failure on startup
4. **Verify Signature**: Check auto-extracted signature in menu
5. **Test Execution**: Call function and verify behavior

This system provides flexibility for both rapid prototyping and production-quality integrations while maintaining clean separation between TreeShell navigation and business logic."""
        
        return docs, True


class AgentTreeShell(TreeShell, AgentTreeReplMixin):
    """
    Agent-level TreeShell with quarantine restrictions.
    Agents can create workflows but cannot approve them.
    """
    
    def __init__(self, graph_config: dict = None, session_id: str = None, approval_callback=None):
        # Load base config and agent config, then merge with provided config
        base_config = self._static_load_config("base_default_config_v2.json")
        agent_config = self._static_load_config("agent_default_config_v2.json")
        
        # Start with base config
        final_config = base_config.copy() if base_config else {}
        
        # Add agent-specific nodes (0.1.* domain)
        if agent_config and "nodes" in agent_config:
            if "nodes" not in final_config:
                final_config["nodes"] = {}
            final_config["nodes"].update(agent_config["nodes"])
        
        # Merge provided config (app-specific nodes)
        if graph_config:
            if "nodes" in graph_config:
                if "nodes" not in final_config:
                    final_config["nodes"] = {}
                final_config["nodes"].update(graph_config["nodes"])
                # Remove nodes from graph_config to avoid double-updating
                config_without_nodes = {k: v for k, v in graph_config.items() if k != "nodes"}
                final_config.update(config_without_nodes)
            else:
                final_config.update(graph_config)
        
        # Set default role for agent shells if not specified
        if 'role' not in final_config:
            final_config['role'] = 'Autonomous AI Agent'
        
        TreeShell.__init__(self, final_config)
        self.__init_agent_features__(session_id, approval_callback)
    
    @staticmethod
    def _static_load_config(filename: str) -> dict:
        """Static method to load configuration from JSON file."""
        import os
        import json
        
        # Get the directory where this module is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to heaven-tree-repl directory, then into configs
        configs_dir = os.path.join(os.path.dirname(current_dir), "configs")
        file_path = os.path.join(configs_dir, filename)
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            else:
                print(f"Warning: Config file not found: {file_path}")
                return {}
        except Exception as e:
            print(f"Error loading config from {filename}: {e}")
            return {}
    
    def _load_shortcuts(self) -> None:
        """Load base + agent shortcuts."""
        shortcuts = {}
        
        # Load base shortcuts
        base_shortcuts = self._load_shortcuts_file("base_shortcuts.json")
        if base_shortcuts:
            shortcuts.update(base_shortcuts)
        
        # Load agent shortcuts
        agent_shortcuts = self._load_shortcuts_file("system_agent_shortcuts.json")
        if agent_shortcuts:
            shortcuts.update(agent_shortcuts)
        
        # Store in session vars
        self.session_vars["_shortcuts"] = shortcuts
    
    def _save_shortcut_to_file(self, alias: str, shortcut_data: dict) -> None:
        """Save shortcut to agent_shortcuts.json for agent-specific shortcuts."""
        self._save_shortcut_to_specific_file(alias, shortcut_data, "system_agent_shortcuts.json")
    
    def handle_command(self, command: str) -> dict:
        """Override to use agent command handling."""
        return self.handle_command_agent(command)


class UserTreeShell(TreeShell, UserTreeReplMixin):
    """
    User-level TreeShell with agent management and approval capabilities.
    Humans can launch agents and approve/reject their workflows.
    """
    
    def __init__(self, config: dict = None, parent_approval_callback=None):
        # Load user config which specifies families to load
        user_config = self._static_load_config("user_default_config_v2.json")
        
        # Start with user config as base
        final_config = user_config.copy() if user_config else {}
        
        # Merge provided config (app-specific customization)
        if config:
            final_config.update(config)
        
        # Initialize with family-based config (TreeShellBase will handle family loading)
        TreeShell.__init__(self, final_config)
        self.__init_user_features__(parent_approval_callback)
    
    @staticmethod
    def _static_load_config(filename: str) -> dict:
        """Static method to load configuration from JSON file."""
        import os
        import json
        
        # Get the directory where this module is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to heaven-tree-repl directory, then into configs
        configs_dir = os.path.join(os.path.dirname(current_dir), "configs")
        file_path = os.path.join(configs_dir, filename)
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            else:
                print(f"Warning: Config file not found: {file_path}")
                return {}
        except Exception as e:
            print(f"Error loading config from {filename}: {e}")
            return {}
    
    def _load_shortcuts(self) -> None:
        """Load base + user shortcuts."""
        shortcuts = {}
        
        # Load base shortcuts
        base_shortcuts = self._load_shortcuts_file("base_shortcuts.json")
        if base_shortcuts:
            shortcuts.update(base_shortcuts)
        
        # Load user shortcuts
        user_shortcuts = self._load_shortcuts_file("system_user_shortcuts.json")
        if user_shortcuts:
            shortcuts.update(user_shortcuts)
        
        # Store in session vars
        self.session_vars["_shortcuts"] = shortcuts
    
    def _save_shortcut_to_file(self, alias: str, shortcut_data: dict) -> None:
        """Save shortcut to user_shortcuts.json for user-specific shortcuts."""
        self._save_shortcut_to_specific_file(alias, shortcut_data, "system_user_shortcuts.json")


class FullstackTreeShell(UserTreeShell, TreeReplFullstackMixin):
    """
    Complete fullstack TreeShell supporting nested human-agent interactions.
    """
    
    def __init__(self, user_config: dict = None, agent_config: dict = None, base_config: dict = None, parent_approval_callback=None):
        # Load all three config layers and merge them
        base_cfg = base_config if base_config else self._static_load_config("base_default_config_v2.json")
        agent_cfg = agent_config if agent_config else self._static_load_config("agent_default_config_v2.json")
        user_cfg = user_config if user_config else self._static_load_config("user_default_config.json")
        
        # Start with base config
        final_config = base_cfg.copy() if base_cfg else {}
        
        # Add agent-specific nodes (0.1.* domain)
        if agent_cfg and "nodes" in agent_cfg:
            if "nodes" not in final_config:
                final_config["nodes"] = {}
            final_config["nodes"].update(agent_cfg["nodes"])
        
        # Add user-specific nodes (0.3.*, 0.4.*)
        if user_cfg and "nodes" in user_cfg:
            if "nodes" not in final_config:
                final_config["nodes"] = {}
            final_config["nodes"].update(user_cfg["nodes"])
            
        # Update other config fields from user config (user config takes precedence)
        if user_cfg:
            for key, value in user_cfg.items():
                if key != "nodes":
                    final_config[key] = value
        
        # Set default role for fullstack shells if not specified
        if 'role' not in final_config:
            final_config['role'] = 'AI Automation Emergence Engineer'
        
        # Initialize TreeShell directly to avoid UserTreeShell's config loading
        TreeShell.__init__(self, final_config)
        self.__init_user_features__(parent_approval_callback)
        self.__init_fullstack_features__(parent_approval_callback)
    
    @staticmethod
    def _static_load_config(filename: str) -> dict:
        """Static method to load configuration from JSON file."""
        import os
        import json
        
        # Get the directory where this module is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to heaven-tree-repl directory, then into configs
        configs_dir = os.path.join(os.path.dirname(current_dir), "configs")
        file_path = os.path.join(configs_dir, filename)
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            else:
                print(f"Warning: Config file not found: {file_path}")
                return {}
        except Exception as e:
            print(f"Error loading config from {filename}: {e}")
            return {}
    
    def _load_shortcuts(self) -> None:
        """Load base + agent + user shortcuts (all layers)."""
        shortcuts = {}
        
        # Load base shortcuts
        base_shortcuts = self._load_shortcuts_file("base_shortcuts.json")
        if base_shortcuts:
            shortcuts.update(base_shortcuts)
        
        # Load agent shortcuts
        agent_shortcuts = self._load_shortcuts_file("system_agent_shortcuts.json")
        if agent_shortcuts:
            shortcuts.update(agent_shortcuts)
        
        # Load user shortcuts
        user_shortcuts = self._load_shortcuts_file("system_user_shortcuts.json")
        if user_shortcuts:
            shortcuts.update(user_shortcuts)
        
        # Store in session vars
        self.session_vars["_shortcuts"] = shortcuts
    
    def _save_shortcut_to_file(self, alias: str, shortcut_data: dict) -> None:
        """Save shortcut to user_shortcuts.json for fullstack shortcuts (inherits from UserTreeShell)."""
        self._save_shortcut_to_specific_file(alias, shortcut_data, "system_user_shortcuts.json")