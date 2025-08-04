#!/usr/bin/env python3
"""
TreeShell MCP Generator - Generate complete MCP server packages
"""
import os
import json
from pathlib import Path
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader, Template

from .config import TreeShellMCPConfig


class MCPGenerator:
    """
    Generate complete MCP server packages from TreeShell applications.
    
    Takes a TreeShellMCPConfig and generates all necessary files:
    - server.py (main MCP server)
    - __init__.py (package init)
    - setup.py (package setup)
    - pyproject.toml (modern packaging)
    - requirements.txt (dependencies)
    - config_template.json (user config template)
    - README.md (documentation)
    """
    
    def __init__(self, config: TreeShellMCPConfig):
        """
        Initialize generator with configuration.
        
        Args:
            config: TreeShellMCPConfig instance with all generation parameters
        """
        self.config = config
        
        # Setup Jinja2 environment
        template_dir = Path(__file__).parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
    def generate_all(self, output_dir: str) -> Dict[str, str]:
        """
        Generate complete MCP server package.
        
        Args:
            output_dir: Directory where to generate the package
            
        Returns:
            Dict mapping file paths to their generated content
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        generated_files = {}
        
        # Generate all components
        generated_files.update(self.generate_server_py(output_path))
        generated_files.update(self.generate_init_py(output_path))
        generated_files.update(self.generate_setup_py(output_path))
        generated_files.update(self.generate_pyproject_toml(output_path))
        generated_files.update(self.generate_requirements_txt(output_path))
        generated_files.update(self.generate_config_template(output_path))
        generated_files.update(self.generate_readme_md(output_path))
        
        return generated_files
    
    def generate_server_py(self, output_dir: Path) -> Dict[str, str]:
        """Generate the main MCP server file."""
        template = self.jinja_env.get_template('server.py.j2')
        content = template.render(config=self.config)
        
        file_path = output_dir / "server.py"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return {str(file_path): content}
    
    def generate_init_py(self, output_dir: Path) -> Dict[str, str]:
        """Generate package __init__.py file."""
        template = self.jinja_env.get_template('__init__.py.j2')
        content = template.render(config=self.config)
        
        file_path = output_dir / "__init__.py"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return {str(file_path): content}
    
    def generate_setup_py(self, output_dir: Path) -> Dict[str, str]:
        """Generate setup.py file."""
        template = self.jinja_env.get_template('setup.py.j2')
        content = template.render(config=self.config)
        
        file_path = output_dir / "setup.py"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return {str(file_path): content}
    
    def generate_pyproject_toml(self, output_dir: Path) -> Dict[str, str]:
        """Generate pyproject.toml file."""
        template = self.jinja_env.get_template('pyproject.toml.j2')
        content = template.render(config=self.config)
        
        file_path = output_dir / "pyproject.toml"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return {str(file_path): content}
    
    def generate_requirements_txt(self, output_dir: Path) -> Dict[str, str]:
        """Generate requirements.txt file."""
        content = '\n'.join(self.config.dependencies) + '\n'
        
        file_path = output_dir / "requirements.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return {str(file_path): content}
    
    def generate_config_template(self, output_dir: Path) -> Dict[str, str]:
        """Generate configuration template for users."""
        template_config = {
            "server_name": self.config.server_name,
            "app_import_path": self.config.import_path,
            "factory_function": self.config.factory_function,
            "environment_variables": self.config.environment_vars,
            "description": f"Configuration for {self.config.description}"
        }
        
        content = json.dumps(template_config, indent=2)
        
        file_path = output_dir / "config_template.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return {str(file_path): content}
    
    def generate_readme_md(self, output_dir: Path) -> Dict[str, str]:
        """Generate README.md documentation."""
        template = self.jinja_env.get_template('README.md.j2')
        content = template.render(config=self.config)
        
        file_path = output_dir / "README.md"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return {str(file_path): content}
    
    def generate_cli_script(self) -> str:
        """Generate a CLI script for easy generation."""
        template = self.jinja_env.get_template('generate_mcp.py.j2')
        return template.render(config=self.config)
    
    def validate_generation(self, output_dir: str) -> Dict[str, bool]:
        """
        Validate that all generated files are correct.
        
        Args:
            output_dir: Directory containing generated files
            
        Returns:
            Dict mapping file names to validation status
        """
        output_path = Path(output_dir)
        
        validation_results = {}
        
        # Check required files exist
        required_files = [
            "server.py",
            "__init__.py", 
            "setup.py",
            "pyproject.toml",
            "requirements.txt",
            "config_template.json",
            "README.md"
        ]
        
        for file_name in required_files:
            file_path = output_path / file_name
            validation_results[file_name] = file_path.exists() and file_path.stat().st_size > 0
        
        # Validate Python syntax
        try:
            import ast
            server_path = output_path / "server.py"
            if server_path.exists():
                with open(server_path, 'r') as f:
                    ast.parse(f.read())
                validation_results["server.py_syntax"] = True
        except SyntaxError:
            validation_results["server.py_syntax"] = False
        
        return validation_results