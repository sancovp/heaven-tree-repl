#!/usr/bin/env python3
"""
Renderer module - Format TreeShell responses as crystal ball markdown.
"""
import json
from typing import Dict, Any
from .display_brief import DisplayBrief


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
    
    # Create display brief for main menu
    display_brief = None
    if position == "0":
        display_brief = DisplayBrief(role=role)
    
    # Start with crystal ball tree header and position info
    base_header = f"<<[🔮‍🌳]>> You are now visiting position `{position}` in the {app_id} tree space for the domain: {domain}."
    
    if display_brief and display_brief.has_content():
        header = f"{base_header} {display_brief.to_display_string()}"
    else:
        header = base_header
    
    # Handle different response types
    action = response.get("action", "menu")
    
    if action == "menu" or "menu_options" in response:
        # Menu display
        content = _render_menu(response)
        
    elif action in ["execute", "execute_at_target"]:
        # Execution result
        content = _render_execution(response)
        
    elif action == "navigate":
        # Navigation result
        content = _render_navigation(response)
        
    elif action == "jump_execute":
        # Jump with execution
        content = _render_jump_execute(response)
        
    elif action == "chain":
        # Chain execution
        content = _render_chain(response)
        
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
    
    # Menu description
    description = response.get("description", "No description available")
    
    # Menu options
    menu_options = response.get("menu_options", {})
    actions = []
    for key, value in sorted(menu_options.items(), key=lambda x: int(x[0]) if x[0].isdigit() else x[0]):
        actions.append(f"  {key}: {value}")
    
    actions_text = "\n".join(actions) if actions else "  No actions available"
    
    return f"""# {node_id} Menu

Description: {description}

Actions:[
{actions_text}
]"""


def _render_execution(response: Dict[str, Any]) -> str:
    """Render execution result."""
    parts = []
    
    # Execution header
    target = response.get("target", response.get("position", "Unknown"))
    parts.append(f"# Executed at {target}")
    
    # Result
    result = response.get("result", {})
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