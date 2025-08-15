#!/usr/bin/env python3
"""
TreeShell Library Factory Implementation

Converts development work into published libraries using category-theoretic foundations.
Built on TreeShellCategoryTheory (Operad + Monad + Fibration).
"""

import os
import json
import shutil
import subprocess
import copy
from typing import Dict, List, Any, Optional
from pathlib import Path

from .category_theory import TreeShellCategoryTheory, PyPISubstrate, GitHubSubstrate
from .system_config_loader_v2 import SystemConfigLoader


class TreeShellLibraryFactory:
    """
    Build tool that converts development work into published libraries.
    
    Takes a developer's customized TreeShell system and automatically generates 
    a complete, publishable library with all customizations baked in as defaults.
    """
    
    def __init__(
        self,
        library_name: str,
        version: str,
        author: str,
        description: str,
        dev_configs_path: str,
        custom_families_path: Optional[str] = None,
        target: str = "pypi",
        output_dir: str = "./generated-library/",
        pypi_token: Optional[str] = None,
        github_token: Optional[str] = None
    ):
        self.library_name = library_name
        self.version = version
        self.author = author
        self.description = description
        self.dev_configs_path = Path(dev_configs_path)
        self.custom_families_path = Path(custom_families_path) if custom_families_path else None
        self.target = target
        self.output_dir = Path(output_dir)
        self.pypi_token = pypi_token
        self.github_token = github_token
        
        # Initialize category theory system
        self.base_config = self._load_base_config()
        self.category_system = TreeShellCategoryTheory(self.base_config)
        
        # Load dev configurations
        self.dev_config = self._load_dev_configs()
        
        self.validation_warnings: List[str] = []
        
    def generate_library(self) -> Dict[str, Any]:
        """
        Generate complete library structure using category theory pipeline.
        
        Returns the generated package structure.
        """
        print(f"🔮 Generating TreeShell library: {self.library_name}")
        
        # Step 1: Create output directory
        self._prepare_output_directory()
        
        # Step 2: Use category theory system to generate and materialize
        try:
            package = self.category_system.generate_and_release(
                dev_config=self.dev_config,
                substrate=self.target,
                coordinate=None  # Auto-assign next coordinate
            )
            print(f"✅ Category theory pipeline completed")
            print(f"   Generated package keys: {list(package.keys())}")
        except Exception as e:
            print(f"❌ Category theory pipeline failed: {e}")
            import traceback
            traceback.print_exc()
            raise
        
        # Step 3: Write files to output directory
        self._write_package_files(package)
        
        # Step 4: Copy custom families if provided
        if self.custom_families_path:
            self._copy_custom_families()
            
        print(f"✅ Library generated at: {self.output_dir}")
        return package
        
    def validate(self) -> bool:
        """
        Validate generated library structure and dependencies.
        
        Returns True if validation passes, False otherwise.
        """
        print("🔍 Validating generated library...")
        
        self.validation_warnings = []
        
        # Check required files exist
        required_files = ['setup.py', 'pyproject.toml']
        for file_name in required_files:
            file_path = self.output_dir / file_name
            if not file_path.exists():
                self.validation_warnings.append(f"Missing required file: {file_name}")
                
        # Check shell classes file
        shell_classes_path = self.output_dir / f"{self._get_package_name()}" / "__init__.py"
        if not shell_classes_path.exists():
            self.validation_warnings.append("Missing shell classes file")
            
        # Check config structure
        configs_dir = self.output_dir / "configs"
        if not configs_dir.exists():
            self.validation_warnings.append("Missing configs directory")
        else:
            # Check system configs
            expected_configs = [
                'system_base_config.json',
                'system_agent_config.json', 
                'system_user_config.json'
            ]
            for config_name in expected_configs:
                config_path = configs_dir / config_name
                if not config_path.exists():
                    self.validation_warnings.append(f"Missing system config: {config_name}")
                    
        # Try importing the package (syntax check)
        try:
            import_test_script = f"""
import sys
sys.path.insert(0, '{self.output_dir}')
import {self._get_package_name()}
print("Import successful")
"""
            result = subprocess.run(
                ['python', '-c', import_test_script],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                self.validation_warnings.append(f"Import test failed: {result.stderr}")
        except Exception as e:
            self.validation_warnings.append(f"Import validation error: {e}")
            
        if self.validation_warnings:
            print("⚠️  Validation warnings:")
            for warning in self.validation_warnings:
                print(f"  - {warning}")
            return False
        else:
            print("✅ Validation passed")
            return True
            
    def publish(self) -> bool:
        """
        Publish library to target substrate.
        
        Returns True if publishing succeeds, False otherwise.
        """
        if not self.validate():
            print("❌ Cannot publish: validation failed")
            return False
            
        print(f"🚀 Publishing to {self.target}...")
        
        if self.target == "pypi":
            return self._publish_to_pypi()
        elif self.target == "github":
            return self._publish_to_github()
        elif self.target == "local":
            return self._publish_local()
        else:
            print(f"❌ Unknown target: {self.target}")
            return False
            
    def get_validation_warnings(self) -> List[str]:
        """Get list of validation warnings."""
        return self.validation_warnings
        
    def _load_base_config(self) -> Dict[str, Any]:
        """Load base TreeShell configuration."""
        return {
            'library_name': self.library_name,
            'version': self.version,
            'author': self.author,
            'description': self.description,
            'coordinate_base': 0
        }
        
    def _load_dev_configs(self) -> Dict[str, Any]:
        """Load all dev configuration files."""
        dev_config = {
            'override_nodes': {},
            'add_nodes': {},
            'exclude_nodes': []
        }
        
        # Load each dev config file
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
                        
                    # Merge configurations
                    if 'override_nodes' in file_config:
                        dev_config['override_nodes'].update(file_config['override_nodes'])
                    if 'add_nodes' in file_config:
                        dev_config['add_nodes'].update(file_config['add_nodes'])
                    if 'exclude_nodes' in file_config:
                        dev_config['exclude_nodes'].extend(file_config['exclude_nodes'])
                        
                except json.JSONDecodeError as e:
                    print(f"⚠️  Warning: Invalid JSON in {config_file}: {e}")
                except Exception as e:
                    print(f"⚠️  Warning: Could not load {config_file}: {e}")
                    
        return dev_config
        
    def _prepare_output_directory(self):
        """Create and prepare output directory structure."""
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
            
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create package directory
        package_dir = self.output_dir / self._get_package_name()
        package_dir.mkdir(exist_ok=True)
        
        # Create configs directory
        configs_dir = self.output_dir / "configs"
        configs_dir.mkdir(exist_ok=True)
        
    def _write_package_files(self, package: Dict[str, Any]):
        """Write package files to output directory."""
        # Write setup.py
        setup_path = self.output_dir / "setup.py"
        with open(setup_path, 'w') as f:
            f.write(package['setup_py'])
            
        # Write pyproject.toml
        pyproject_path = self.output_dir / "pyproject.toml"
        with open(pyproject_path, 'w') as f:
            f.write(package['pyproject_toml'])
            
        # Write shell classes as package __init__.py
        package_dir = self.output_dir / self._get_package_name()
        init_path = package_dir / "__init__.py"
        with open(init_path, 'w') as f:
            f.write(package['shell_classes'])
            
        # Promote dev configs to system configs
        self._promote_dev_to_system_configs()
                
        # Create empty dev templates for end users
        self._create_dev_templates()
        
    def _promote_dev_to_system_configs(self):
        """Promote dev configs to system configs by applying customizations."""
        configs_dir = self.output_dir / "configs"
        
        # First, copy the original system configs from heaven-tree-repl
        heaven_configs_dir = Path(__file__).parent.parent / "configs"
        
        # Copy all system config files as base
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
            source_path = heaven_configs_dir / config_file
            dest_path = configs_dir / config_file
            
            if source_path.exists():
                # Load original config
                with open(source_path, 'r') as f:
                    original_config = json.load(f)
                    
                # Apply dev customizations if they exist
                customized_config = self._apply_dev_customizations_to_config(original_config, config_file)
                
                # Write customized version
                with open(dest_path, 'w') as f:
                    json.dump(customized_config, f, indent=2)
                    
                print(f"✅ Promoted {config_file} with customizations")
            else:
                # Create empty config if source doesn't exist
                with open(dest_path, 'w') as f:
                    json.dump({}, f, indent=2)
                print(f"⚠️  Created empty {config_file} (source not found)")
                
    def _apply_dev_customizations_to_config(self, original_config: Dict[str, Any], config_file: str) -> Dict[str, Any]:
        """Apply dev customizations to a specific config file."""
        # Start with original config
        customized_config = copy.deepcopy(original_config)
        
        # Determine which dev config file applies to this system config
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
        # Note: This is a simplified version - full implementation would use SystemConfigLoader logic
        
        # Apply overrides (merge into existing config)
        if 'override_nodes' in dev_customizations:
            for node_path, overrides in dev_customizations['override_nodes'].items():
                # This would need more sophisticated merging logic
                # For now, just add to the config
                if 'customizations' not in customized_config:
                    customized_config['customizations'] = {}
                if 'overrides' not in customized_config['customizations']:
                    customized_config['customizations']['overrides'] = {}
                customized_config['customizations']['overrides'][node_path] = overrides
                
        # Apply additions
        if 'add_nodes' in dev_customizations:
            if 'customizations' not in customized_config:
                customized_config['customizations'] = {}
            if 'additions' not in customized_config['customizations']:
                customized_config['customizations']['additions'] = {}
            customized_config['customizations']['additions'].update(dev_customizations['add_nodes'])
            
        # Apply exclusions
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
                
    def _copy_custom_families(self):
        """Copy custom family files to output directory."""
        if not self.custom_families_path.exists():
            print(f"⚠️  Warning: Custom families path does not exist: {self.custom_families_path}")
            return
            
        families_dir = self.output_dir / "families"
        families_dir.mkdir(exist_ok=True)
        
        for family_file in self.custom_families_path.glob("*.json"):
            dest_path = families_dir / family_file.name
            shutil.copy2(family_file, dest_path)
            print(f"📁 Copied family: {family_file.name}")
            
    def _get_package_name(self) -> str:
        """Get Python package name from library name."""
        return self.library_name.replace('-', '_')
        
    def _publish_to_pypi(self) -> bool:
        """Publish package to PyPI."""
        try:
            # Build package
            build_result = subprocess.run(
                ['python', '-m', 'build'],
                cwd=self.output_dir,
                capture_output=True,
                text=True
            )
            
            if build_result.returncode != 0:
                print(f"❌ Build failed: {build_result.stderr}")
                return False
                
            # Upload to PyPI
            if self.pypi_token:
                upload_cmd = [
                    'python', '-m', 'twine', 'upload',
                    '--username', '__token__',
                    '--password', self.pypi_token,
                    'dist/*'
                ]
            else:
                upload_cmd = ['python', '-m', 'twine', 'upload', 'dist/*']
                
            upload_result = subprocess.run(
                upload_cmd,
                cwd=self.output_dir,
                capture_output=True,
                text=True
            )
            
            if upload_result.returncode != 0:
                print(f"❌ Upload failed: {upload_result.stderr}")
                return False
                
            print(f"✅ Successfully published {self.library_name} to PyPI")
            return True
            
        except Exception as e:
            print(f"❌ PyPI publishing error: {e}")
            return False
            
    def _publish_to_github(self) -> bool:
        """Publish package to GitHub repository."""
        try:
            # Initialize git repo
            subprocess.run(['git', 'init'], cwd=self.output_dir, check=True)
            subprocess.run(['git', 'add', '.'], cwd=self.output_dir, check=True)
            subprocess.run(
                ['git', 'commit', '-m', f'Initial commit for {self.library_name} v{self.version}'],
                cwd=self.output_dir,
                check=True
            )
            
            # Create GitHub repo if token provided
            if self.github_token:
                create_repo_cmd = [
                    'gh', 'repo', 'create', self.library_name,
                    '--private',
                    '--source', str(self.output_dir),
                    '--push'
                ]
                
                subprocess.run(
                    create_repo_cmd,
                    env={**os.environ, 'GITHUB_TOKEN': self.github_token},
                    check=True
                )
                
            print(f"✅ Successfully published {self.library_name} to GitHub")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ GitHub publishing failed: {e}")
            return False
        except Exception as e:
            print(f"❌ GitHub publishing error: {e}")
            return False
            
    def _publish_local(self) -> bool:
        """Install package locally for development."""
        try:
            # Install in development mode
            install_result = subprocess.run(
                ['pip', 'install', '-e', '.'],
                cwd=self.output_dir,
                capture_output=True,
                text=True
            )
            
            if install_result.returncode != 0:
                print(f"❌ Local installation failed: {install_result.stderr}")
                return False
                
            print(f"✅ Successfully installed {self.library_name} locally")
            return True
            
        except Exception as e:
            print(f"❌ Local installation error: {e}")
            return False


def create_library_from_dev_environment(
    dev_config_path: str,
    library_name: str,
    version: str = "1.0.0",
    author: str = "TreeShell Developer",
    description: str = None,
    target: str = "local"
) -> TreeShellLibraryFactory:
    """
    Convenience function to create library from existing dev environment.
    
    Args:
        dev_config_path: Path to directory containing dev_*.json files
        library_name: Name for the generated library
        version: Library version
        author: Library author
        description: Library description
        target: Publishing target (local, pypi, github)
        
    Returns:
        Configured TreeShellLibraryFactory instance
    """
    if description is None:
        description = f"Custom TreeShell library: {library_name}"
        
    factory = TreeShellLibraryFactory(
        library_name=library_name,
        version=version,
        author=author,
        description=description,
        dev_configs_path=dev_config_path,
        target=target,
        output_dir=f"./generated-{library_name}/"
    )
    
    return factory


# Example usage for generating library from our test environment
if __name__ == "__main__":
    # Create library from our test dev configs
    factory = create_library_from_dev_environment(
        dev_config_path="/tmp/heaven_data/user_interface_hub_v1_0/configs",
        library_name="my-custom-treeshell",
        version="1.0.0",
        author="TreeShell Developer",
        description="A custom TreeShell library with personalized features",
        target="local"
    )
    
    # Generate, validate, and publish
    package = factory.generate_library()
    if factory.validate():
        factory.publish()
    else:
        print("Validation failed. Check warnings.")
        for warning in factory.get_validation_warnings():
            print(f"  - {warning}")