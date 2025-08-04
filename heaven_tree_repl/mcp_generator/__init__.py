"""
TreeShell MCP Generator - Automatically generate MCP servers from TreeShell apps
"""

from .config import TreeShellMCPConfig
from .generator import MCPGenerator


def generate_mcp_from_config(config_file: str, output_dir: str) -> dict:
    """
    Convenience function to generate MCP server from config file.
    
    Args:
        config_file: Path to JSON configuration file
        output_dir: Directory where to generate the MCP server
        
    Returns:
        Dict mapping file paths to their generated content
    """
    config = TreeShellMCPConfig.from_config_file(config_file)
    generator = MCPGenerator(config)
    return generator.generate_all(output_dir)


def generate_mcp_from_dict(config_dict: dict, output_dir: str) -> dict:
    """
    Convenience function to generate MCP server from config dict.
    
    Args:
        config_dict: Configuration dictionary
        output_dir: Directory where to generate the MCP server
        
    Returns:
        Dict mapping file paths to their generated content
    """
    config = TreeShellMCPConfig(**config_dict)
    generator = MCPGenerator(config)
    return generator.generate_all(output_dir)


__all__ = [
    "TreeShellMCPConfig", 
    "MCPGenerator", 
    "generate_mcp_from_config",
    "generate_mcp_from_dict"
]