#!/usr/bin/env python3
"""
Recursive TreeShell Library Factory

Implements the adaptive injection pattern that works recursively on any TreeShell-based library.
Each generated library becomes a complete ecosystem that can spawn its own children.
"""

import os
import json
import shutil
import subprocess
import copy
import importlib
import inspect
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from .category_theory import TreeShellCategoryTheory, PyPISubstrate, GitHubSubstrate, LocalSubstrate


class RecursiveTreeShellFactory:
    """
    Recursive factory that can build on ANY TreeShell-based library.
    
    Uses adaptive base detection to inherit from the latest generation of
    TreeShell classes and config loaders, applying the same injection pattern
    at every level.
    """
    
    def __init__(
        self,
        base_library: str,
        new_library_name: str,
        version: str,
        author: str,
        description: str,
        dev_configs_path: str,
        target: str = "local",
        output_dir: str = None,
        pypi_token: Optional[str] = None,
        github_token: Optional[str] = None
    ):
        self.base_library = base_library
        self.new_library_name = new_library_name
        self.version = version
        self.author = author
        self.description = description
        self.dev_configs_path = Path(dev_configs_path)
        self.target = target
        self.output_dir = Path(output_dir) if output_dir else Path(f"./generated-{new_library_name}/")
        self.pypi_token = pypi_token
        self.github_token = github_token
        
        # Detect base library structure
        self.base_info = self._detect_base_library_structure()
        
        # Initialize category theory system
        self.base_config = self._load_base_config()
        self.category_system = TreeShellCategoryTheory(self.base_config)
        
        # Load dev configurations
        self.dev_config = self._load_dev_configs()
        
        self.validation_warnings: List[str] = []
        
    def _detect_base_library_structure(self) -> Dict[str, Any]:
        """
        Detect the base library structure to find what classes to inherit from.
        
        Returns info about the base library's TreeShell classes and config loader.
        """
        try:
            # Import the base library
            base_module = importlib.import_module(self.base_library)
            
            # Find all TreeShell classes in the base library
            treeshell_classes = {}
            config_loader_class = None
            
            for name, obj in inspect.getmembers(base_module, inspect.isclass):
                # Look for TreeShell classes
                if name.endswith('TreeShell'):
                    treeshell_classes[name] = obj
                    
                # Look for ConfigLoader classes
                if name.endswith('ConfigLoader'):
                    config_loader_class = obj
                    
            # If no custom config loader found, look for SystemConfigLoader
            if not config_loader_class:
                try:
                    from .system_config_loader_v2 import SystemConfigLoader
                    config_loader_class = SystemConfigLoader
                except ImportError:
                    pass
                    
            return {
                'module': base_module,
                'treeshell_classes': treeshell_classes,
                'config_loader_class': config_loader_class,
                'library_name': self.base_library
            }
            
        except ImportError as e:
            raise ValueError(f"Could not import base library '{self.base_library}': {e}")
            
    def _filter_to_latest_generation_classes(self, treeshell_classes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter TreeShell classes to only the latest generation.
        
        This prevents inheriting from both MyDomainTreeShell AND TreeShell -
        we only want to inherit from MyDomainTreeShell (the latest).
        """
        # If this is heaven-tree-repl (base library), return the core classes
        if self.base_library == "heaven_tree_repl":
            core_classes = {}
            for name, cls in treeshell_classes.items():
                if name in ['TreeShell', 'AgentTreeShell', 'UserTreeShell', 'FullstackTreeShell']:
                    core_classes[name] = cls
            return core_classes or treeshell_classes
            
        # For generated libraries, find the "latest generation" classes
        # These are the ones that start with the library's class prefix
        base_lib_clean = self.base_library.replace('_', '').replace('-', '')
        
        latest_classes = {}
        base_patterns = ['TreeShell', 'AgentTreeShell', 'UserTreeShell', 'FullstackTreeShell', 'LibraryTreeShell']
        
        # First, try to find custom classes that follow the naming pattern
        for name, cls in treeshell_classes.items():
            # Look for classes that start with the base library name pattern
            if any(name.endswith(pattern) for pattern in base_patterns):
                # If it's a custom class (contains the library name), it's latest generation
                if any(lib_part.lower() in name.lower() for lib_part in self.base_library.split('_')):
                    latest_classes[name] = cls
                    
        # If we found custom classes, use only those
        if latest_classes:
            return latest_classes
            
        # Fallback: use the standard TreeShell classes
        fallback_classes = {}
        for name, cls in treeshell_classes.items():
            if name in base_patterns:
                fallback_classes[name] = cls
                
        return fallback_classes or treeshell_classes
            
    def _generate_adaptive_shell_classes(self) -> str:
        """
        Generate shell classes that adapt to the base library structure.
        
        Uses the same injection pattern but inherits from whatever classes
        exist in the base library.
        """
        base_info = self.base_info
        new_lib_name = self.new_library_name.replace('-', '_')
        class_name = ''.join(word.capitalize() for word in new_lib_name.split('_'))
        
        # Generate imports
        imports = []
        imports.append("#!/usr/bin/env python3")
        imports.append("# Auto-generated by Recursive TreeShell Factory")
        imports.append("")
        imports.append("import os")
        imports.append("from pathlib import Path")
        
        # Import base classes
        base_lib = base_info['library_name']
        treeshell_classes = base_info['treeshell_classes']
        config_loader_class = base_info['config_loader_class']
        
        # Import all TreeShell classes from base
        class_imports = []
        for class_name_base in treeshell_classes.keys():
            class_imports.append(class_name_base)
            
        if class_imports:
            imports.append(f"from {base_lib} import {', '.join(class_imports)}")
            
        # Import config loader
        if config_loader_class and hasattr(config_loader_class, '__module__'):
            config_loader_name = config_loader_class.__name__
            if base_lib in config_loader_class.__module__:
                imports.append(f"from {base_lib} import {config_loader_name}")
            else:
                imports.append(f"from {config_loader_class.__module__} import {config_loader_name}")
        else:
            imports.append("from heaven_tree_repl.system_config_loader_v2 import SystemConfigLoader")
            config_loader_name = "SystemConfigLoader"
            
        imports.append("")
        
        # Generate config loader class
        config_loader_code = f"""
class {class_name}ConfigLoader({config_loader_name}):
    \"\"\"Custom config loader that uses this library's system configs as base.\"\"\"
    
    def _get_library_configs_dir(self) -> str:
        \"\"\"Override to use this library's configs instead of parent's.\"\"\"
        # Point to this library's config directory
        library_root = Path(__file__).parent.parent
        return str(library_root / "configs")
"""
        
        # Generate TreeShell classes
        shell_classes = []
        
        # Map common TreeShell class patterns
        class_patterns = {
            'TreeShell': 'base',
            'AgentTreeShell': 'agent', 
            'UserTreeShell': 'user',
            'LibraryTreeShell': 'library',
            'FullstackTreeShell': 'fullstack'
        }
        
        # Filter to only the "latest generation" classes
        latest_classes = self._filter_to_latest_generation_classes(treeshell_classes)
        
        # Generate classes based on latest generation only
        for base_class_name, base_class in latest_classes.items():
            # Determine config types for this class
            config_types = ["base"]  # Always include base
            
            if 'Agent' in base_class_name:
                config_types.append("agent")
            if 'User' in base_class_name:
                config_types.append("user")
            if 'Library' in base_class_name or 'Fullstack' in base_class_name:
                config_types.extend(["agent", "user"])
                
            config_types_str = json.dumps(config_types)
            
            new_class_name = f"{class_name}{base_class_name}"
            
            # Generate constructor parameters based on base class
            if 'Agent' in base_class_name:
                params = "user_config_path: str = None, session_id: str = None, approval_callback=None"
                super_params = "final_config, session_id, approval_callback"
            elif 'User' in base_class_name or 'Library' in base_class_name or 'Fullstack' in base_class_name:
                params = "user_config_path: str = None, parent_approval_callback=None"
                super_params = "final_config, parent_approval_callback"
            else:
                params = "user_config_path: str = None"
                super_params = "final_config"
                
            shell_class_code = f"""
class {new_class_name}({base_class_name}):
    \"\"\"Enhanced {base_class_name} with {class_name} customizations baked in.\"\"\"
    def __init__(self, {params}):
        config_loader = {class_name}ConfigLoader(config_types={config_types_str})
        final_config = config_loader.load_configs(user_config_path)
        super().__init__({super_params})
"""
            shell_classes.append(shell_class_code)
            
        # If no TreeShell classes found, generate basic ones
        if not treeshell_classes:
            # Fall back to basic TreeShell classes
            basic_classes = [
                ("TreeShell", "TreeShell", ["base"], "user_config_path: str = None", "final_config"),
                ("AgentTreeShell", "AgentTreeShell", ["base", "agent"], "user_config_path: str = None, session_id: str = None, approval_callback=None", "final_config, session_id, approval_callback"),
                ("UserTreeShell", "UserTreeShell", ["base", "user"], "user_config_path: str = None, parent_approval_callback=None", "final_config, parent_approval_callback"),
                ("LibraryTreeShell", "FullstackTreeShell", ["base", "agent", "user"], "user_config_path: str = None, parent_approval_callback=None", "final_config, parent_approval_callback")
            ]
            
            imports.append(f"from {base_lib} import TreeShell, AgentTreeShell, UserTreeShell, FullstackTreeShell")
            
            for class_suffix, base_class, config_types, params, super_params in basic_classes:
                new_class_name = f"{class_name}{class_suffix}"
                config_types_str = json.dumps(config_types)
                
                shell_class_code = f"""
class {new_class_name}({base_class}):
    \"\"\"Enhanced {base_class} with {class_name} customizations baked in.\"\"\"
    def __init__(self, {params}):
        config_loader = {class_name}ConfigLoader(config_types={config_types_str})
        final_config = config_loader.load_configs(user_config_path)
        super().__init__({super_params})
"""
                shell_classes.append(shell_class_code)
                
        # Combine all code
        full_code = "\n".join(imports) + config_loader_code + "\n".join(shell_classes)
        
        return full_code
        
    def generate_library(self) -> Dict[str, Any]:
        """Generate complete recursive library structure."""
        print(f"🔮 Generating recursive TreeShell library: {self.new_library_name}")
        print(f"   Building on: {self.base_library}")
        
        # Step 1: Create output directory
        self._prepare_output_directory()
        
        # Step 2: Generate adaptive shell classes
        shell_classes_code = self._generate_adaptive_shell_classes()
        
        # Step 3: Use category theory system for config promotion
        package = self.category_system.generate_and_release(
            dev_config=self.dev_config,
            substrate=self.target,
            coordinate=None
        )
        
        # Override shell classes with adaptive version
        package['shell_classes'] = shell_classes_code
        
        # Step 4: Write package files
        self._write_package_files(package)
        
        # Step 5: Include factory code in generated library
        self._include_factory_code()
        
        print(f"✅ Recursive library generated at: {self.output_dir}")
        return package
        
    def _include_factory_code(self):
        """Include factory code so generated library can spawn its own children."""
        # Copy this factory file to the generated library
        factory_source = Path(__file__)
        factory_dest = self.output_dir / self._get_package_name() / "factory.py"
        
        shutil.copy2(factory_source, factory_dest)
        
        # Create CLI script
        cli_script = f"""#!/usr/bin/env python3
\"\"\"CLI for {self.new_library_name} TreeShell Factory\"\"\"

import argparse
from pathlib import Path
from .factory import RecursiveTreeShellFactory

def main():
    parser = argparse.ArgumentParser(description="Generate TreeShell library from {self.new_library_name}")
    parser.add_argument("--new-library", required=True, help="Name of new library to generate")
    parser.add_argument("--dev-configs", required=True, help="Path to dev config directory")
    parser.add_argument("--version", default="1.0.0", help="Version of new library")
    parser.add_argument("--author", default="TreeShell Developer", help="Author name")
    parser.add_argument("--description", help="Library description")
    parser.add_argument("--target", default="local", choices=["local", "pypi", "github"], help="Publishing target")
    parser.add_argument("--output-dir", help="Output directory")
    
    args = parser.parse_args()
    
    if not args.description:
        args.description = f"TreeShell library based on {self.new_library_name}"
    
    factory = RecursiveTreeShellFactory(
        base_library="{self._get_package_name()}",
        new_library_name=args.new_library,
        version=args.version,
        author=args.author,
        description=args.description,
        dev_configs_path=args.dev_configs,
        target=args.target,
        output_dir=args.output_dir
    )
    
    package = factory.generate_library()
    
    if factory.validate():
        success = factory.publish()
        if success:
            print(f"🚀 Successfully published {{args.new_library}}!")
        else:
            print(f"❌ Publishing failed")
    else:
        print("❌ Validation failed")
        for warning in factory.get_validation_warnings():
            print(f"  - {{warning}}")

if __name__ == "__main__":
    main()
"""
        
        cli_path = self.output_dir / self._get_package_name() / "cli.py"
        with open(cli_path, 'w') as f:
            f.write(cli_script)
            
        print(f"✅ Included recursive factory code in generated library")
        
    def _load_base_config(self) -> Dict[str, Any]:
        """Load base configuration."""
        return {
            'library_name': self.new_library_name,
            'version': self.version,
            'author': self.author,
            'description': self.description,
            'coordinate_base': 0,
            'base_library': self.base_library
        }
        
    def _load_dev_configs(self) -> Dict[str, Any]:
        """Load all dev configuration files."""
        dev_config = {
            'override_nodes': {},
            'add_nodes': {},
            'exclude_nodes': []
        }
        
        dev_config_files = [
            'dev_base_config.json',
            'dev_agent_config.json',
            'dev_user_config.json',
            'dev_base_shortcuts.json',
            'dev_agent_shortcuts.json',
            'dev_user_shortcuts.json',
            'dev_base_zone_config.json',
            'dev_agent_zone_config.json',
            'dev_user_zone_config.json'
        ]
        
        for config_file in dev_config_files:
            config_path = self.dev_configs_path / config_file
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        file_config = json.load(f)
                        
                    if 'override_nodes' in file_config:
                        dev_config['override_nodes'].update(file_config['override_nodes'])
                    if 'add_nodes' in file_config:
                        dev_config['add_nodes'].update(file_config['add_nodes'])
                    if 'exclude_nodes' in file_config:
                        dev_config['exclude_nodes'].extend(file_config['exclude_nodes'])
                        
                except (json.JSONDecodeError, Exception) as e:
                    print(f"⚠️  Warning: Could not load {config_file}: {e}")
                    
        return dev_config
        
    def _prepare_output_directory(self):
        """Create and prepare output directory structure."""
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
            
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        package_dir = self.output_dir / self._get_package_name()
        package_dir.mkdir(exist_ok=True)
        
        configs_dir = self.output_dir / "configs"
        configs_dir.mkdir(exist_ok=True)
        
    def _write_package_files(self, package: Dict[str, Any]):
        """Write package files to output directory."""
        # Write setup.py with correct dependency
        setup_content = self._generate_setup_py()
        setup_path = self.output_dir / "setup.py"
        with open(setup_path, 'w') as f:
            f.write(setup_content)
            
        # Write pyproject.toml with correct dependency
        pyproject_content = self._generate_pyproject_toml()
        pyproject_path = self.output_dir / "pyproject.toml"
        with open(pyproject_path, 'w') as f:
            f.write(pyproject_content)
            
        # Write shell classes and update __init__.py
        package_dir = self.output_dir / self._get_package_name()
        init_path = package_dir / "__init__.py"
        
        # Generate __init__.py with predictable custom loader export
        init_content = self._generate_init_py(package['shell_classes'])
        with open(init_path, 'w') as f:
            f.write(init_content)
            
        # Promote configs
        self._promote_dev_to_system_configs()
        
        # Create dev templates
        self._create_dev_templates()
        
    def _generate_setup_py(self) -> str:
        """Generate setup.py with correct base library dependency."""
        package_name = self._get_package_name()
        
        return f"""#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="{self.new_library_name}",
    version="{self.version}",
    author="{self.author}",
    description="{self.description}",
    packages=find_packages(),
    install_requires=[
        "{self.base_library}",
    ],
    python_requires=">=3.8",
    entry_points={{
        'console_scripts': [
            '{package_name}-factory={package_name}.cli:main',
        ],
    }},
)
"""
    
    def _generate_pyproject_toml(self) -> str:
        """Generate pyproject.toml with correct base library dependency."""
        return f"""[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{self.new_library_name}"
version = "{self.version}"
description = "{self.description}"
authors = [{{name = "{self.author}"}}]
dependencies = [
    "{self.base_library}",
]
requires-python = ">=3.8"
"""

    def _promote_dev_to_system_configs(self):
        """Copy and customize configs from base library."""
        configs_dir = self.output_dir / "configs"
        
        # Try to find base library's config directory
        try:
            base_module = importlib.import_module(self.base_library)
            base_module_path = Path(base_module.__file__).parent
            base_configs_dir = base_module_path.parent / "configs"
            
            if not base_configs_dir.exists():
                # Try looking in the package itself
                base_configs_dir = base_module_path / "configs"
                
        except Exception:
            # Fall back to heaven-tree-repl configs
            base_configs_dir = Path(__file__).parent.parent / "configs"
            
        system_config_files = [
            'system_base_config.json',
            'system_agent_config.json', 
            'system_user_config.json',
            'system_base_shortcuts.json',
            'system_agent_shortcuts.json',
            'system_user_shortcuts.json',
            'system_base_zone_config.json',
            'system_agent_zone_config.json',
            'system_user_zone_config.json'
        ]
        
        for config_file in system_config_files:
            source_path = base_configs_dir / config_file
            dest_path = configs_dir / config_file
            
            if source_path.exists():
                with open(source_path, 'r') as f:
                    original_config = json.load(f)
                    
                customized_config = self._apply_dev_customizations_to_config(original_config, config_file)
                
                with open(dest_path, 'w') as f:
                    json.dump(customized_config, f, indent=2)
                    
                print(f"✅ Promoted {config_file} with customizations")
            else:
                with open(dest_path, 'w') as f:
                    json.dump({}, f, indent=2)
                print(f"⚠️  Created empty {config_file} (source not found)")
                
    def _apply_dev_customizations_to_config(self, original_config: Dict[str, Any], config_file: str) -> Dict[str, Any]:
        """Apply dev customizations to a specific config file."""
        customized_config = copy.deepcopy(original_config)
        
        dev_config_map = {
            'system_base_config.json': 'dev_base_config.json',
            'system_agent_config.json': 'dev_agent_config.json',
            'system_user_config.json': 'dev_user_config.json',
            'system_base_shortcuts.json': 'dev_base_shortcuts.json',
            'system_agent_shortcuts.json': 'dev_agent_shortcuts.json',
            'system_user_shortcuts.json': 'dev_user_shortcuts.json',
            'system_base_zone_config.json': 'dev_base_zone_config.json',
            'system_agent_zone_config.json': 'dev_agent_zone_config.json',
            'system_user_zone_config.json': 'dev_user_zone_config.json'
        }
        
        dev_config_file = dev_config_map.get(config_file)
        if not dev_config_file:
            return customized_config
            
        dev_config_path = self.dev_configs_path / dev_config_file
        if not dev_config_path.exists():
            return customized_config
            
        try:
            with open(dev_config_path, 'r') as f:
                dev_customizations = json.load(f)
        except (json.JSONDecodeError, Exception):
            return customized_config
            
        # Apply customizations
        if 'override_nodes' in dev_customizations:
            if 'customizations' not in customized_config:
                customized_config['customizations'] = {}
            if 'overrides' not in customized_config['customizations']:
                customized_config['customizations']['overrides'] = {}
            customized_config['customizations']['overrides'].update(dev_customizations['override_nodes'])
                
        if 'add_nodes' in dev_customizations:
            if 'customizations' not in customized_config:
                customized_config['customizations'] = {}
            if 'additions' not in customized_config['customizations']:
                customized_config['customizations']['additions'] = {}
            customized_config['customizations']['additions'].update(dev_customizations['add_nodes'])
            
        if 'exclude_nodes' in dev_customizations:
            if 'customizations' not in customized_config:
                customized_config['customizations'] = {}
            customized_config['customizations']['exclusions'] = dev_customizations['exclude_nodes']
            
        return customized_config
        
    def _create_dev_templates(self):
        """Create empty dev config templates for end users."""
        configs_dir = self.output_dir / "configs"
        
        dev_template = {
            "override_nodes": {},
            "add_nodes": {},
            "exclude_nodes": []
        }
        
        dev_config_files = [
            'dev_base_config.json',
            'dev_agent_config.json',
            'dev_user_config.json',
            'dev_base_shortcuts.json',
            'dev_agent_shortcuts.json',
            'dev_user_shortcuts.json',
            'dev_base_zone_config.json',
            'dev_agent_zone_config.json',
            'dev_user_zone_config.json'
        ]
        
        for config_file in dev_config_files:
            template_path = configs_dir / config_file
            with open(template_path, 'w') as f:
                json.dump(dev_template, f, indent=2)
                
    def _generate_init_py(self, shell_classes_code: str) -> str:
        """
        Generate __init__.py that predictably exports the custom config loader.
        
        This ensures each generated library properly exports its custom loader
        for the next generation to inherit from.
        """
        package_name = self._get_package_name()
        class_name = ''.join(word.capitalize() for word in package_name.split('_'))
        
        # Extract class names from the shell classes code
        import re
        class_pattern = rf'class ({class_name}\w*)\('
        class_matches = re.findall(class_pattern, shell_classes_code)
        
        config_loader_name = f"{class_name}ConfigLoader"
        shell_class_names = [name for name in class_matches if name != config_loader_name]
        
        init_content = f'''"""
{self.new_library_name.replace('-', ' ').title()} - TreeShell Library

Generated by Recursive TreeShell Factory
Built on: {self.base_library}
"""

__version__ = "{self.version}"

# Import all generated classes
{shell_classes_code}

# Export everything for public API and next-generation inheritance
__all__ = [
    "{config_loader_name}",'''
        
        for class_name in shell_class_names:
            init_content += f'\n    "{class_name}",'
            
        init_content += '\n]'
        
        return init_content
        
    def _get_package_name(self) -> str:
        """Get Python package name from library name."""
        return self.new_library_name.replace('-', '_')
        
    def validate(self) -> bool:
        """Validate generated library structure."""
        # Basic validation - check required files exist
        required_files = ['setup.py', 'pyproject.toml']
        for file_name in required_files:
            if not (self.output_dir / file_name).exists():
                self.validation_warnings.append(f"Missing required file: {file_name}")
                
        return len(self.validation_warnings) == 0
        
    def publish(self) -> bool:
        """Publish library to target substrate."""
        if self.target == "local":
            try:
                result = subprocess.run(
                    ['pip', 'install', '-e', '.'],
                    cwd=self.output_dir,
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0
            except Exception:
                return False
        return True
        
    def get_validation_warnings(self) -> List[str]:
        """Get validation warnings."""
        return self.validation_warnings