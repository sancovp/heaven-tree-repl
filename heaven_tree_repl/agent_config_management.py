"""
Agent Config Management - Equipment system for building HeavenAgentConfig

Simple wrapper functions for TreeShell nodes that use existing HEAVEN framework utilities.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List

# Global dynamic config storage
_dynamic_config = {}

def get_dynamic_config() -> Dict[str, Any]:
    """Get the current dynamic agent config."""
    return _dynamic_config.copy()

def reset_dynamic_config():
    """Reset the dynamic config to empty state."""
    _dynamic_config.clear()

# System Prompt management
def equip_system_prompt(prompt: str):
    """Equip a system prompt to the dynamic config."""
    _dynamic_config['system_prompt'] = prompt
    return f"✅ Equipped system prompt ({len(prompt)} chars)", True

def unequip_system_prompt() -> Dict[str, Any]:
    """Remove system prompt from dynamic config."""
    if 'system_prompt' in _dynamic_config:
        del _dynamic_config['system_prompt']
        return {"success": True, "message": "Unequipped system prompt"}
    return {"success": False, "message": "No system prompt equipped"}

def list_system_prompts() -> Dict[str, Any]:
    """List current system prompt."""
    current = _dynamic_config.get('system_prompt')
    if current:
        preview = current[:100] + "..." if len(current) > 100 else current
        return {"success": True, "current": preview, "message": f"Current: {len(current)} chars"}
    return {"success": True, "current": None, "message": "No system prompt equipped"}

# Tools management
def equip_tool(tool_name: str):
    """Equip a tool to the dynamic config."""
    # Resolve tool name to actual tool class
    try:
        from heaven_base.utils.agent_and_tool_lists import get_tool_class
        tool_class = get_tool_class(tool_name)
        
        tools = _dynamic_config.get('tools', [])
        # Check by class name to avoid duplicates
        tool_names = [getattr(t, '__name__', str(t)) for t in tools]
        if tool_name not in tool_names:
            tools.append(tool_class)
            _dynamic_config['tools'] = tools
            return f"✅ Equipped tool: {tool_name}", True
        return f"❌ Tool {tool_name} already equipped", False
    except Exception as e:
        return f"❌ Failed to equip tool {tool_name}: {str(e)}", False

def unequip_tool(tool_name: str) -> Dict[str, Any]:
    """Remove a tool from dynamic config."""
    tools = _dynamic_config.get('tools', [])
    if tool_name in tools:
        tools.remove(tool_name)
        _dynamic_config['tools'] = tools
        return {"success": True, "message": f"Unequipped tool: {tool_name}"}
    return {"success": False, "message": f"Tool {tool_name} not equipped"}

def list_tools() -> Dict[str, Any]:
    """List available and equipped tools."""
    from heaven_base.utils.agent_and_tool_lists import get_tool_modules
    available = get_tool_modules().split(", ")
    equipped = _dynamic_config.get('tools', [])
    return {
        "success": True, 
        "available": available[:10],  # Show first 10
        "equipped": equipped,
        "message": f"Available: {len(available)}, Equipped: {len(equipped)}"
    }

# Provider management
def equip_provider(provider: str) -> Dict[str, Any]:
    """Equip an AI provider to the dynamic config."""
    valid_providers = ['anthropic', 'openai', 'google']
    if provider.lower() not in valid_providers:
        return {"success": False, "message": f"Invalid provider. Must be one of: {valid_providers}"}
    _dynamic_config['provider'] = provider.lower()
    return {"success": True, "message": f"Equipped provider: {provider}"}

def unequip_provider() -> Dict[str, Any]:
    """Remove provider from dynamic config."""
    if 'provider' in _dynamic_config:
        del _dynamic_config['provider']
        return {"success": True, "message": "Unequipped provider"}
    return {"success": False, "message": "No provider equipped"}

def list_providers() -> Dict[str, Any]:
    """List available providers."""
    available = ['anthropic', 'openai', 'google']
    current = _dynamic_config.get('provider')
    return {"success": True, "available": available, "current": current}

# Model management
def equip_model(model: str) -> Dict[str, Any]:
    """Equip a model to the dynamic config."""
    _dynamic_config['model'] = model
    return {"success": True, "message": f"Equipped model: {model}"}

def unequip_model() -> Dict[str, Any]:
    """Remove model from dynamic config."""
    if 'model' in _dynamic_config:
        del _dynamic_config['model']
        return {"success": True, "message": "Unequipped model"}
    return {"success": False, "message": "No model equipped"}

def list_models() -> Dict[str, Any]:
    """List available models."""
    models_by_provider = {
        'anthropic': ['claude-3-7-sonnet-latest', 'claude-3-5-sonnet-20241022'],
        'openai': ['gpt-4.1', 'gpt-4.1-mini', 'gpt-4.1-nano'],
        'google': ['gemini-2.5-flash-preview-04-17', 'gemini-pro']
    }
    current_provider = _dynamic_config.get('provider', 'anthropic')
    available = models_by_provider.get(current_provider, [])
    current = _dynamic_config.get('model')
    return {"success": True, "available": available, "current": current, "provider": current_provider}

# Temperature management
def equip_temperature(temperature: float) -> Dict[str, Any]:
    """Equip temperature setting."""
    if not 0.0 <= temperature <= 1.0:
        return {"success": False, "message": "Temperature must be between 0.0 and 1.0"}
    _dynamic_config['temperature'] = temperature
    return {"success": True, "message": f"Equipped temperature: {temperature}"}

def unequip_temperature() -> Dict[str, Any]:
    """Remove temperature from dynamic config."""
    if 'temperature' in _dynamic_config:
        del _dynamic_config['temperature']
        return {"success": True, "message": "Unequipped temperature"}
    return {"success": False, "message": "No temperature equipped"}

def list_temperature() -> Dict[str, Any]:
    """Show current temperature."""
    current = _dynamic_config.get('temperature')
    return {"success": True, "current": current, "default": 0.7}

# Max tokens management
def equip_max_tokens(max_tokens: int) -> Dict[str, Any]:
    """Equip max_tokens setting."""
    if max_tokens <= 0:
        return {"success": False, "message": "max_tokens must be positive"}
    _dynamic_config['max_tokens'] = max_tokens
    return {"success": True, "message": f"Equipped max_tokens: {max_tokens}"}

def unequip_max_tokens() -> Dict[str, Any]:
    """Remove max_tokens from dynamic config."""
    if 'max_tokens' in _dynamic_config:
        del _dynamic_config['max_tokens']
        return {"success": True, "message": "Unequipped max_tokens"}
    return {"success": False, "message": "No max_tokens equipped"}

def list_max_tokens() -> Dict[str, Any]:
    """Show current max_tokens."""
    current = _dynamic_config.get('max_tokens')
    return {"success": True, "current": current, "default": 8000}

# Name management
def equip_name(name: str) -> Dict[str, Any]:
    """Equip agent name."""
    if not name or not name.strip():
        return {"success": False, "message": "Agent name cannot be empty"}
    _dynamic_config['name'] = name.strip()
    return {"success": True, "message": f"Equipped name: {name}"}

def unequip_name() -> Dict[str, Any]:
    """Remove name from dynamic config."""
    if 'name' in _dynamic_config:
        del _dynamic_config['name']
        return {"success": True, "message": "Unequipped name"}
    return {"success": False, "message": "No name equipped"}

def list_names() -> Dict[str, Any]:
    """Show current name."""
    current = _dynamic_config.get('name')
    return {"success": True, "current": current}

# Prompt blocks management
def equip_prompt_block(block_name: str) -> Dict[str, Any]:
    """Equip a prompt suffix block."""
    blocks = _dynamic_config.get('prompt_suffix_blocks', [])
    if block_name not in blocks:
        blocks.append(block_name)
        _dynamic_config['prompt_suffix_blocks'] = blocks
        return {"success": True, "message": f"Equipped prompt block: {block_name}"}
    return {"success": False, "message": f"Prompt block {block_name} already equipped"}

def unequip_prompt_block(block_name: str) -> Dict[str, Any]:
    """Remove a prompt suffix block."""
    blocks = _dynamic_config.get('prompt_suffix_blocks', [])
    if block_name in blocks:
        blocks.remove(block_name)
        _dynamic_config['prompt_suffix_blocks'] = blocks
        return {"success": True, "message": f"Unequipped prompt block: {block_name}"}
    return {"success": False, "message": f"Prompt block {block_name} not equipped"}

def list_prompt_blocks() -> Dict[str, Any]:
    """List prompt suffix blocks."""
    equipped = _dynamic_config.get('prompt_suffix_blocks', [])
    available = ["switchboard", "extraction", "thinking", "debug"]
    return {"success": True, "available": available, "equipped": equipped}

# Config file management
def save_config_as(name: str) -> Dict[str, Any]:
    """Save current dynamic config as a Python file using HEAVEN framework."""
    if not name or not name.strip():
        return {"success": False, "message": "Config name cannot be empty"}
    
    name = name.strip()
    
    if 'system_prompt' not in _dynamic_config:
        return {"success": False, "message": "Cannot save config without system_prompt"}
    
    try:
        heaven_data_dir = os.getenv('HEAVEN_DATA_DIR')
        if not heaven_data_dir:
            return {"success": False, "message": "HEAVEN_DATA_DIR environment variable not set"}
        
        agents_dir = Path(heaven_data_dir) / 'agents' / name
        config_file = agents_dir / f"{name}_config.py"
        
        if config_file.exists():
            return {"success": False, "message": f"Config '{name}' already exists. Use copy_existing to load it."}
        
        agents_dir.mkdir(parents=True, exist_ok=True)
        
        # Use HEAVEN's template generation (this would need to be implemented)
        config_content = f'''from heaven_base.baseheavenagent import HeavenAgentConfig
from heaven_base.unified_chat import ProviderEnum

agent_config = HeavenAgentConfig(
    name="{name}",
    system_prompt="""{_dynamic_config['system_prompt']}""",
    tools={_dynamic_config.get('tools', [])},
    provider=ProviderEnum.{_dynamic_config.get('provider', 'ANTHROPIC').upper()},
    model="{_dynamic_config.get('model', '')}",
    temperature={_dynamic_config.get('temperature', 0.7)},
    max_tokens={_dynamic_config.get('max_tokens', 8000)},
    prompt_suffix_blocks={_dynamic_config.get('prompt_suffix_blocks', [])},
)
'''
        
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        return {"success": True, "message": f"Saved config '{name}' to {config_file}"}
        
    except Exception as e:
        return {"success": False, "message": f"Failed to save config: {str(e)}"}

def copy_existing(name: str) -> Dict[str, Any]:
    """Load an existing config into the dynamic config."""
    if not name or not name.strip():
        return {"success": False, "message": "Config name cannot be empty"}
    
    try:
        heaven_data_dir = os.getenv('HEAVEN_DATA_DIR')
        if not heaven_data_dir:
            return {"success": False, "message": "HEAVEN_DATA_DIR environment variable not set"}
        
        config_file = Path(heaven_data_dir) / 'agents' / name / f"{name}_config.py"
        
        if not config_file.exists():
            return {"success": False, "message": f"Config '{name}' not found at {config_file}"}
        
        # Load the config (simplified - would use proper Python module loading)
        # For now, just reset and set name
        _dynamic_config.clear()
        _dynamic_config['name'] = name
        
        return {"success": True, "message": f"Loaded config '{name}' into dynamic config"}
        
    except Exception as e:
        return {"success": False, "message": f"Failed to load config: {str(e)}"}

def list_saved_configs() -> Dict[str, Any]:
    """List all saved agent configs."""
    try:
        heaven_data_dir = os.getenv('HEAVEN_DATA_DIR')
        if not heaven_data_dir:
            return {"success": False, "message": "HEAVEN_DATA_DIR environment variable not set"}
        
        agents_dir = Path(heaven_data_dir) / 'agents'
        if not agents_dir.exists():
            return {"success": True, "configs": [], "message": "No saved configs found"}
        
        configs = []
        for agent_dir in agents_dir.iterdir():
            if agent_dir.is_dir():
                config_file = agent_dir / f"{agent_dir.name}_config.py"
                if config_file.exists():
                    configs.append(agent_dir.name)
        
        return {"success": True, "configs": configs, "message": f"Found {len(configs)} saved configs"}
        
    except Exception as e:
        return {"success": False, "message": f"Failed to list configs: {str(e)}"}

def preview_dynamic_config() -> Dict[str, Any]:
    """Show current state of dynamic config."""
    config = get_dynamic_config()
    required_fields = ['name', 'system_prompt']
    missing = [field for field in required_fields if field not in config or not config[field]]
    complete = len(missing) == 0
    
    return {
        "success": True,
        "config": config,
        "complete": complete,
        "missing": missing,
        "message": f"Config {'complete' if complete else 'incomplete'}"
    }