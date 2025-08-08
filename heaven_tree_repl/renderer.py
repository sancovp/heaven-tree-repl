#!/usr/bin/env python3
"""
Renderer module - Format TreeShell responses as crystal ball markdown.
"""
import json
from typing import Dict, Any, Union, List
from .display_brief import DisplayBrief

def resolve_description(description: Union[str, List[str]]) -> str:
    """Resolve description as string or HEAVEN blocks array."""
    if isinstance(description, str):
        return description  # Static string, return as-is
    elif isinstance(description, list):
        try:
            # Resolve as HEAVEN prompt suffix blocks
            from heaven_base import HeavenAgentConfig
            temp_config = HeavenAgentConfig(
                name="temp",
                system_prompt="",  # Empty base
                prompt_suffix_blocks=description
            )
            resolved = temp_config.get_system_prompt()
            return resolved.strip()  # Remove any leading/trailing whitespace
        except Exception as e:
            # Fallback to simple concatenation if HEAVEN resolution fails
            return '\n'.join(str(block) for block in description)
    else:
        return str(description)  # Fallback for other types


def render_response(response: Dict[str, Any]) -> str:
    """
    Render TreeShell response as crystal ball formatted markdown.
    
    Args:
        response: Dict response from TreeShell.handle_command()
        
    Returns:
        Formatted string with crystal ball header and markdown content
    """
    # Get metadata
    position = response.get("position", "0")
    app_id = response.get("app_id", "default")
    domain = response.get("domain", "general")
    role = response.get("role", "assistant")
    
    # Start with crystal ball tree header and position info
    base_header = f"<<[🔮‍🌳]>> You are now visiting position `{position}` in the {app_id} tree space for the domain: {domain}."
    
    # Build header with help message for main menu
    help_msg = " | 💡 New here? Use `jump 0.2.6` for Computational Model overview" if position == "0" else ""
    
    header = f"{base_header}{help_msg}"
    
    # Handle different response types
    action = response.get("action", "menu")
    
    if action == "menu" or "menu_options" in response:
        # Menu display
        content = _render_menu(response)
        
    elif action in ["execute", "execute_at_target"]:
        # Execution result
        content = _render_execution(response)
        
    elif "result" in response and "execution" in response:
        # This looks like an execution result (even without explicit action)
        content = _render_execution(response)
        
    elif action == "navigate":
        # Navigation result
        content = _render_navigation(response)
        
    elif action == "jump":
        # Jump result - same as navigation
        content = _render_navigation(response)
        
    elif action == "jump_execute":
        # Jump with execution
        content = _render_jump_execute(response)
        
    elif action == "chain":
        # Chain execution
        content = _render_chain(response)
        
    elif action == "navigation_overview":
        # Navigation overview (nav command)
        content = _render_navigation_overview(response)
        
    elif action == "create_shortcut":
        # Shortcut creation
        content = _render_create_shortcut(response)
        
    elif action == "list_shortcuts":
        # List shortcuts
        content = _render_list_shortcuts(response)
        
    elif "error" in response:
        # Error display
        content = _render_error(response)
        
    else:
        # Generic response
        content = _render_generic(response)
    
    return f"{header}\n\n{content}\n>>>"


def _render_menu(response: Dict[str, Any]) -> str:
    """Render menu display."""
    # Node ID and Menu title
    node_id = response.get("position", "Unknown")
    
    # Menu description with HEAVEN resolution
    raw_description = response.get("description", "No description available")
    description = resolve_description(raw_description)
    signature = response.get("signature", "")
    
    # Menu options
    menu_options = response.get("menu_options", {})
    actions = []
    for key, value in sorted(menu_options.items(), key=lambda x: int(x[0]) if x[0].isdigit() else x[0]):
        actions.append(f"  {key}: {value}")
    
    actions_text = "\n".join(actions) if actions else "  No actions available"
    
    # Build description section
    desc_section = f"Description: {description}"
    if signature and signature != "No signature available":
        desc_section += f"\n\nArgs: {signature}"
        
        # Add warning if system prefill is present
        if "SYSTEM_WILL_PREFILL" in signature:
            desc_section += f"\n\n⚠️ If param=SYSTEM_WILL_PREFILL, it can be ignored because the system will prefill it.\nIf signature shows (x, y=SYSTEM_WILL_PREFILL), call it with args={{\"x\": ...}}"
    
    # Get node name (prompt) or fallback to position
    node_name = response.get("prompt", response.get("position", "Unknown"))
    
    return f"""# {node_name} Menu

{desc_section}

Actions:[
{actions_text}
]"""


def _render_execution(response: Dict[str, Any]) -> str:
    """Render execution result."""
    parts = []
    
    # Execution header
    target = response.get("target", response.get("position", "Unknown"))
    
    # Check if this is an error result
    result = response.get("result", {})
    if isinstance(result, dict) and "error" in result:
        # This is an error result - render as error
        parts.append(f"# ❌ Execution Error at {target}")
        parts.append(f"\n**Error:** {result['error']}")
        
        if "exception_type" in result:
            parts.append(f"**Exception Type:** {result['exception_type']}")
        
        if "function_name" in result:
            parts.append(f"**Function:** {result['function_name']}")
            
        if "args" in result and result["args"]:
            parts.append(f"**Arguments:** {result['args']}")
            
        # Only show traceback if debugging is needed
        if "traceback" in result:
            parts.append(f"\n**Traceback:**\n```\n{result['traceback']}\n```")
            
    else:
        # Normal successful execution
        parts.append(f"# Executed at {target}")
        
        # Result
        if isinstance(result, dict):
            if "result" in result:
                # Nested result structure
                actual_result = result["result"]
                if isinstance(actual_result, dict):
                    parts.append("## Result:")
                    for key, value in actual_result.items():
                        parts.append(f"- **{key}:** {value}")
                else:
                    parts.append(f"**Result:** {actual_result}")
            else:
                # Direct result dict
                parts.append("## Result:")
                for key, value in result.items():
                    if key != "execution":  # Skip execution metadata
                        parts.append(f"- **{key}:** {value}")
        else:
            parts.append(f"**Result:** {result}")
    
    return "\n".join(parts)


def _render_navigation(response: Dict[str, Any]) -> str:
    """Render navigation result."""
    parts = []
    
    target = response.get("target", "Unknown")
    parts.append(f"# Navigated to {target}")
    
    # Show menu if available
    if "menu" in response:
        menu_content = _render_menu(response["menu"])
        # Remove the state_id from menu content to avoid duplication
        menu_lines = menu_content.split("\n")
        filtered_lines = [line for line in menu_lines if not line.startswith("**State:**")]
        parts.append("\n".join(filtered_lines))
    
    return "\n".join(parts)


def _render_jump_execute(response: Dict[str, Any]) -> str:
    """Render jump with execution."""
    parts = []
    
    target = response.get("target", "Unknown")
    parts.append(f"# Jumped to {target} and Executed")
    
    # Show result
    result = response.get("result")
    if result is not None:
        parts.append(f"**Result:** {result}")
    
    return "\n".join(parts)


def _render_chain(response: Dict[str, Any]) -> str:
    """Render chain execution."""
    parts = []
    
    steps_executed = response.get("steps_executed", 0)
    parts.append(f"# Chain Executed ({steps_executed} steps)")
    
    # Show chain results
    chain_results = response.get("chain_results", [])
    if chain_results:
        parts.append("## Steps:")
        for step in chain_results:
            step_num = step.get("step", "?")
            target = step.get("target", "Unknown")
            result = step.get("result", {}).get("result", "No result")
            parts.append(f"**Step {step_num}:** {target} → {result}")
    
    # Final position
    final_position = response.get("final_position")
    if final_position:
        parts.append(f"*Now at: {final_position}*")
    
    return "\n".join(parts)


def _render_navigation_overview(response: Dict[str, Any]) -> str:
    """Render navigation overview (nav command)."""
    parts = []
    
    # Title with emoji
    parts.append("# 🗺️ Navigation Overview")
    
    # Tree structure (the main content)
    tree_structure = response.get("tree_structure", "")
    if tree_structure:
        parts.append("```")
        parts.append(tree_structure)
        parts.append("```")
    
    # Summary stats
    summary = response.get("summary", {})
    if summary:
        parts.append("## 📊 Forest Summary")
        parts.append(f"- **Total nodes:** {summary.get('total_nodes', 0)}")
        parts.append(f"- **Crystal hubs:** {summary.get('menu_nodes', 0)} (menus)")
        parts.append(f"- **Active gears:** {summary.get('callable_nodes', 0)} (executables)")
        parts.append(f"- **Max depth:** {summary.get('max_depth', 0)} levels")
        parts.append(f"- **Current position:** {summary.get('current_position', '0')}")
    
    # Usage hint
    usage = response.get("usage", "")
    if usage:
        parts.append(f"## 💡 Usage")
        parts.append(f"*{usage}*")
    
    # DSL legend
    parts.append("## 🎯 Ontological Emoji DSL")
    parts.append("- **🔮** = Root crystal")
    parts.append("- **🧠** = Brain/AI domain") 
    parts.append("- **📜** = Documentation domain")
    parts.append("- **🚀** = Generation/creation domain")
    parts.append("- **🛠️** = Tools/utilities domain")
    parts.append("- **🌀** = Meta/system operations domain")
    parts.append("- **🤖** = Agent systems domain")
    parts.append("- **🗺️** = General navigation hub")
    parts.append("- **⚙️** = Executable function (universal)")
    
    return "\n".join(parts)


def _render_create_shortcut(response: Dict[str, Any]) -> str:
    """Render shortcut creation response."""
    parts = []
    
    # Title
    parts.append("# 🔗 Shortcut Created")
    
    # Shortcut info
    alias = response.get("alias", "unknown")
    coordinate = response.get("coordinate", "unknown") 
    target = response.get("target", "unknown")
    
    parts.append(f"**Alias:** `{alias}`")
    parts.append(f"**Target:** `{coordinate}` ({target})")
    
    # Usage
    usage = response.get("usage", "")
    if usage:
        parts.append(f"## 💡 Usage")
        parts.append(f"*{usage}*")
    
    return "\n".join(parts)


def _render_list_shortcuts(response: Dict[str, Any]) -> str:
    """Render shortcuts list."""
    parts = []
    
    # Title
    count = response.get("count", 0)
    parts.append(f"# 🔗 Active Shortcuts ({count})")
    
    shortcuts = response.get("shortcuts", {})
    if shortcuts:
        # Separate jump and chain shortcuts
        jump_shortcuts = {k: v for k, v in shortcuts.items() if v.get("shortcut_type") == "jump"}
        chain_shortcuts = {k: v for k, v in shortcuts.items() if v.get("shortcut_type") == "chain"}
        
        if jump_shortcuts:
            parts.append("## 🎯 Jump Shortcuts")
            parts.append("```")
            for alias, info in jump_shortcuts.items():
                coordinate = info.get("coordinate", "")
                target = info.get("target", "Unknown")
                parts.append(f"{alias:<15} → {coordinate:<8} ({target})")
            parts.append("```")
        
        if chain_shortcuts:
            parts.append("## ⛓️ Chain Shortcuts")
            parts.append("```")
            for alias, info in chain_shortcuts.items():
                template_type = info.get("template_type", "unconstrained")
                required_args = info.get("required_args", [])
                args_str = f"requires: {', '.join(required_args)}" if required_args else "no args needed"
                parts.append(f"{alias:<15} → Chain ({template_type}) - {args_str}")
            parts.append("```")
        
        # Usage hint
        usage = response.get("usage", "")
        if usage:
            parts.append(f"## 💡 Usage")
            parts.append(f"*{usage}*")
            
        # Show examples
        parts.append("## 📝 Examples")
        parts.append("- Jump: `brain` → navigate to Brain Management")
        parts.append("- Chain: `workflow {\"param\": \"value\"}` → execute with args")
        
    else:
        parts.append("*No shortcuts defined yet.*")
        parts.append("**Jump shortcuts:** `shortcut <alias> <coordinate>`")
        parts.append("**Chain shortcuts:** `shortcut <alias> \"<chain_template>\"`")
    
    return "\n".join(parts)


def _render_error(response: Dict[str, Any]) -> str:
    """Render error response."""
    error = response.get("error", "Unknown error")
    return f"# ❌ Error\n\n{error}"


def _render_generic(response: Dict[str, Any]) -> str:
    """Render generic response."""
    parts = []
    
    # Try to find a meaningful title
    if "action" in response:
        parts.append(f"# {response['action'].replace('_', ' ').title()}")
    else:
        parts.append("# Response")
    
    # Show key information
    important_keys = ["message", "result", "status", "info"]
    for key in important_keys:
        if key in response:
            value = response[key]
            if isinstance(value, dict):
                parts.append(f"## {key.title()}:")
                for k, v in value.items():
                    parts.append(f"- **{k}:** {v}")
            else:
                parts.append(f"**{key.title()}:** {value}")
    
    return "\n".join(parts)