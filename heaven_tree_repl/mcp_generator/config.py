#!/usr/bin/env python3
"""
TreeShell MCP Configuration - Pydantic model for MCP server generation
"""
import json
import os
from typing import List, Optional, Dict, Any
from pathlib import Path
from pydantic import BaseModel, Field, validator


class TreeShellMCPConfig(BaseModel):
    """
    Configuration for generating TreeShell MCP servers.
    
    This model defines all the parameters needed to automatically generate
    a complete MCP server package from a user's TreeShell application.
    """
    
    # Core app configuration
    app_name: str = Field(..., description="Name of the TreeShell application")
    import_path: str = Field(..., description="Python import path for the app module")
    factory_function: str = Field(default="main", description="Function that returns TreeShell instance")
    description: str = Field(..., description="Description of what the TreeShell app does")
    
    # MCP server configuration  
    server_name: Optional[str] = Field(default=None, description="MCP server name (auto-generated if not provided)")
    tool_name: Optional[str] = Field(default=None, description="MCP tool name (auto-generated if not provided)")
    
    # Package metadata
    version: str = Field(default="0.1.0", description="Package version")
    author: str = Field(default="TreeShell User", description="Package author")
    author_email: str = Field(default="user@example.com", description="Author email")
    license: str = Field(default="MIT", description="Package license")
    python_requires: str = Field(default=">=3.8", description="Python version requirement")
    
    # Dependencies
    dependencies: List[str] = Field(
        default_factory=lambda: ["heaven-tree-repl>=0.1.4", "mcp>=1.0.0"],
        description="Package dependencies"
    )
    dev_dependencies: List[str] = Field(
        default_factory=lambda: ["pytest>=6.0", "black", "flake8"],
        description="Development dependencies"
    )
    
    # Advanced configuration
    environment_vars: Dict[str, str] = Field(
        default_factory=dict,
        description="Required environment variables"
    )
    setup_instructions: List[str] = Field(
        default_factory=list,
        description="Additional setup instructions"
    )
    
    @validator('server_name', always=True)
    def generate_server_name(cls, v, values):
        """Auto-generate server name from app name if not provided."""
        if v is None and 'app_name' in values:
            return f"heaven-{values['app_name'].lower().replace('_', '-')}"
        return v
    
    @validator('tool_name', always=True) 
    def generate_tool_name(cls, v, values):
        """Auto-generate tool name from app name if not provided."""
        if v is None and 'app_name' in values:
            return f"run_{values['app_name'].lower().replace('-', '_')}_shell"
        return v
    
    @classmethod
    def from_config_file(cls, config_path: str) -> "TreeShellMCPConfig":
        """
        Load configuration from JSON file.
        
        Args:
            config_path: Path to JSON configuration file
            
        Returns:
            TreeShellMCPConfig instance
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        return cls(**config_data)
    
    def save_config_file(self, config_path: str):
        """
        Save configuration to JSON file.
        
        Args:
            config_path: Path where to save the configuration
        """
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.dict(), f, indent=2)
    
    def get_package_name(self) -> str:
        """Get the Python package name for the generated MCP server."""
        return self.server_name.replace('-', '_')
    
    def get_mcp_server_class_name(self) -> str:
        """Get the MCP server class name."""
        # Convert kebab-case to PascalCase
        parts = self.server_name.replace('heaven-', '').split('-')
        return ''.join(word.capitalize() for word in parts) + 'MCPServer'
    
    def validate_import_path(self, base_path: str = None) -> bool:
        """
        Validate that the import path can be imported.
        
        Args:
            base_path: Base directory to add to sys.path for testing
            
        Returns:
            True if import succeeds, False otherwise
        """
        import sys
        import importlib
        
        old_path = sys.path[:]
        try:
            if base_path:
                sys.path.insert(0, base_path)
            
            module = importlib.import_module(self.import_path)
            
            # Check if factory function exists
            if not hasattr(module, self.factory_function):
                return False
                
            return True
            
        except ImportError:
            return False
        finally:
            sys.path[:] = old_path
    
    def generate_example_config(self) -> Dict[str, Any]:
        """Generate an example configuration dict."""
        return {
            "app_name": "workflow-manager",
            "import_path": "my_workflow_app",
            "factory_function": "get_workflow_shell", 
            "description": "Advanced workflow management system with TreeShell navigation",
            "version": "0.1.0",
            "author": "Your Name",
            "author_email": "your.email@example.com",
            "dependencies": [
                "heaven-tree-repl>=0.1.4",
                "mcp>=1.0.0",
                "requests>=2.28.0"
            ],
            "environment_vars": {
                "WORKFLOW_DATA_DIR": "/tmp/workflow_data",
                "API_KEY": "your-api-key-here"  
            },
            "setup_instructions": [
                "Set WORKFLOW_DATA_DIR environment variable",
                "Obtain API key from service provider",
                "Run: mkdir -p $WORKFLOW_DATA_DIR"
            ]
        }