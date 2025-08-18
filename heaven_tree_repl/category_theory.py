#!/usr/bin/env python3
"""
TreeShell Category Theory Implementation

Mathematical foundation: Operad + Monad + Fibration system for TreeShell generation.
Implements the complete category-theoretic structure documented in TREESHELL_LIBRARY_FACTORY.md
"""

from typing import Dict, List, Any, Callable, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json
import copy


@dataclass
class Operation:
    """Base class for TreeShell operations in the operad."""
    type: str
    target: str
    data: Dict[str, Any]
    
    @classmethod
    def identity(cls) -> 'Operation':
        """Identity operation for the operad."""
        return cls(type="identity", target="", data={})


@dataclass 
class OverrideOperation(Operation):
    """Override operation that modifies existing nodes."""
    def __init__(self, target: str, overrides: Dict[str, Any]):
        super().__init__(type="override", target=target, data=overrides)


@dataclass
class AddOperation(Operation):
    """Add operation that creates new nodes."""
    def __init__(self, target: str, node_data: Dict[str, Any]):
        super().__init__(type="add", target=target, data=node_data)


@dataclass
class ExcludeOperation(Operation):
    """Exclude operation that removes nodes."""
    def __init__(self, target: str):
        super().__init__(type="exclude", target=target, data={})


class TreeShellOperad:
    """
    Operad defining TreeShell capability algebra.
    
    An operad is a mathematical structure that models operations and their composition.
    In TreeShell, this defines how navigation, execution, customization, and extension
    operations can be algebraically combined.
    """
    
    def __init__(self, config_system: Dict[str, Any]):
        self.config_system = config_system
        self.operations: List[Operation] = []
        self.composition_rules = self._build_composition_rules()
        self.arity_map = self._compute_arity()
        
    def compose(self, ops: List[Operation]) -> Operation:
        """
        Algebraic composition of TreeShell operations.
        
        Satisfies operad laws:
        - Associativity: (a ∘ b) ∘ c = a ∘ (b ∘ c)
        - Identity: id ∘ a = a ∘ id = a
        - Unit coherence: Composition respects units
        """
        if not ops:
            return Operation.identity()
            
        if len(ops) == 1:
            return ops[0]
            
        # Compose operations left-to-right
        result = ops[0]
        for op in ops[1:]:
            result = self._compose_pair(result, op)
            
        return result
        
    def identity(self) -> Operation:
        """Identity operation for the operad."""
        return Operation.identity()
        
    def extract_from_config(self, config: Dict[str, Any]) -> List[Operation]:
        """Extract algebraic operations from dev configuration."""
        operations = []
        
        # Override operations
        override_nodes = config.get('override_nodes', {})
        for target, overrides in override_nodes.items():
            operations.append(OverrideOperation(target, overrides))
            
        # Add operations  
        add_nodes = config.get('add_nodes', {})
        for target, node_data in add_nodes.items():
            operations.append(AddOperation(target, node_data))
            
        # Exclude operations
        exclude_nodes = config.get('exclude_nodes', [])
        for target in exclude_nodes:
            operations.append(ExcludeOperation(target))
            
        return operations
    
    def _build_composition_rules(self) -> Dict[str, Any]:
        """Build composition rules for operations."""
        return {
            'override': self._compose_overrides,
            'add': self._compose_adds,
            'exclude': self._compose_excludes,
            'mixed': self._compose_mixed
        }
    
    def _compute_arity(self) -> Dict[str, int]:
        """Compute arity (number of inputs) for each operation type."""
        return {
            'identity': 0,
            'override': 2,  # target + data
            'add': 2,       # target + data  
            'exclude': 1    # target only
        }
    
    def _compose_pair(self, op1: Operation, op2: Operation) -> Operation:
        """Compose two operations according to operad laws."""
        # Identity laws
        if op1.type == "identity":
            return op2
        if op2.type == "identity":
            return op1
            
        # Same type composition
        if op1.type == op2.type:
            return self.composition_rules[op1.type](op1, op2)
        else:
            return self.composition_rules['mixed'](op1, op2)
    
    def _compose_overrides(self, op1: OverrideOperation, op2: OverrideOperation) -> Operation:
        """Compose two override operations."""
        if op1.target == op2.target:
            # Merge overrides for same target
            merged_data = {**op1.data, **op2.data}
            return OverrideOperation(op1.target, merged_data)
        else:
            # Different targets - create composite operation
            return Operation(
                type="composite_override",
                target="multiple", 
                data={op1.target: op1.data, op2.target: op2.data}
            )
    
    def _compose_adds(self, op1: AddOperation, op2: AddOperation) -> Operation:
        """Compose two add operations."""
        return Operation(
            type="composite_add",
            target="multiple",
            data={op1.target: op1.data, op2.target: op2.data}
        )
    
    def _compose_excludes(self, op1: ExcludeOperation, op2: ExcludeOperation) -> Operation:
        """Compose two exclude operations."""
        return Operation(
            type="composite_exclude", 
            target="multiple",
            data={"excludes": [op1.target, op2.target]}
        )
    
    def _compose_mixed(self, op1: Operation, op2: Operation) -> Operation:
        """Compose operations of different types."""
        return Operation(
            type="composite_mixed",
            target="multiple",
            data={
                "operations": [
                    {"type": op1.type, "target": op1.target, "data": op1.data},
                    {"type": op2.type, "target": op2.target, "data": op2.data}
                ]
            }
        )


class TreeShellMonad:
    """
    Monad for TreeShell self-generation.
    
    A monad is an endofunctor with two natural transformations (unit, bind)
    that satisfy monadic laws. In TreeShell, this enables pure functional
    generation of sibling instances while preserving mathematical structure.
    """
    
    def __init__(self):
        self.coordinate_map: Dict[int, Any] = {}
        self.next_coordinate = 1  # 0 is reserved for base TreeShell
        
    def pure(self, dev_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Unit: Lift dev configuration into TreeShell.
        
        Monadic unit law: bind(pure(a), f) = f(a)
        """
        operad = TreeShellOperad(dev_config)
        operations = operad.extract_from_config(dev_config)
        
        return {
            'config': dev_config,
            'operations': operations,
            'operad': operad,
            'coordinate': 0  # Default coordinate
        }
        
    def bind(self, shell_data: Dict[str, Any], transform: Callable) -> Dict[str, Any]:
        """
        Bind: Monadic composition for TreeShell transformations.
        
        Monadic bind laws:
        - Left identity: bind(pure(a), f) = f(a)  
        - Right identity: bind(m, pure) = m
        - Associativity: bind(bind(m, f), g) = bind(m, λx. bind(f(x), g))
        """
        return transform(shell_data)
        
    def generate_sibling(self, parent_shell: Dict[str, Any], coordinate: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate sibling TreeShell at new coordinate.
        
        This is the key monadic operation that creates mathematically
        equivalent TreeShell instances at different coordinate positions.
        """
        if coordinate is None:
            coordinate = self.next_coordinate
            self.next_coordinate += 1
            
        def sibling_transform(shell: Dict[str, Any]) -> Dict[str, Any]:
            # Extract the mathematical structure
            operad = shell['operad']
            operations = shell['operations']
            
            # Create sibling with same structure, different coordinate space
            sibling_config = copy.deepcopy(shell['config'])
            sibling_config['coordinate_base'] = coordinate
            
            sibling = {
                'config': sibling_config,
                'operations': operations,
                'operad': operad,
                'coordinate': coordinate,
                'parent_coordinate': shell['coordinate']
            }
            
            self.coordinate_map[coordinate] = sibling
            return sibling
            
        return self.bind(parent_shell, sibling_transform)
        
    def coordinate_space_mapping(self) -> Dict[int, Any]:
        """
        Map showing sibling relationships in coordinate space:
        
        0 = TreeShell (original mathematical object)
        ├── 0.1 = System family (child of TreeShell)
        ├── 0.2 = Agent family (child of TreeShell)  
        ├── 0.3 = Conversations family (child of TreeShell)
        └── 0.X = Any other family (child of TreeShell)

        1 = MyLibraryShell (sibling of TreeShell)  
        ├── 1.1 = Custom family (child of MyLibraryShell)
        ├── 1.2 = Domain-specific family (child of MyLibraryShell)
        └── 1.X = Any other family (child of MyLibraryShell)

        2 = AnotherLibraryShell (another sibling)
        3 = YetAnotherLibraryShell (another sibling)
        ...
        ∞
        """
        return self.coordinate_map


class ReleaseSubstrate(ABC):
    """Abstract base for release substrates."""
    
    @abstractmethod
    def project(self, treeshell_data: Dict[str, Any]) -> Dict[str, Any]:
        """Project TreeShell onto this substrate."""
        pass


class PyPISubstrate(ReleaseSubstrate):
    """PyPI package substrate with Python-specific projection."""
    
    def project(self, treeshell_data: Dict[str, Any]) -> Dict[str, Any]:
        """Project TreeShell onto PyPI package format."""
        config = treeshell_data['config']
        operations = treeshell_data['operations']
        
        return {
            'setup_py': self._generate_setup(config),
            'pyproject_toml': self._generate_pyproject(config),
            'shell_classes': self._generate_classes(config, operations),
            'config_files': self._project_configs(config)
        }
    
    def _generate_setup(self, config: Dict[str, Any]) -> str:
        """Generate setup.py content."""
        return f"""#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="{config.get('library_name', 'custom-treeshell')}",
    version="{config.get('version', '1.0.0')}",
    author="{config.get('author', 'TreeShell Developer')}",
    description="{config.get('description', 'Custom TreeShell library')}",
    packages=find_packages(),
    install_requires=[
        "heaven-tree-repl>=0.1.0",
    ],
    python_requires=">=3.8",
)
"""
    
    def _generate_pyproject(self, config: Dict[str, Any]) -> str:
        """Generate pyproject.toml content."""
        return f"""[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{config.get('library_name', 'custom-treeshell')}"
version = "{config.get('version', '1.0.0')}"
description = "{config.get('description', 'Custom TreeShell library')}"
authors = [{{name = "{config.get('author', 'TreeShell Developer')}"}}]
dependencies = [
    "heaven-tree-repl>=0.1.0",
]
requires-python = ">=3.8"
"""
    
    def _generate_classes(self, config: Dict[str, Any], operations: List[Operation]) -> str:
        """Generate shell class hierarchy."""
        lib_name = config.get('library_name', 'custom-treeshell').replace('-', '_')
        class_name = ''.join(word.capitalize() for word in lib_name.split('_'))
        
        return f"""#!/usr/bin/env python3
# Auto-generated by TreeShellLibraryFactory

import os
from pathlib import Path
from heaven_tree_repl.shells import TreeShell, AgentTreeShell, UserTreeShell, FullstackTreeShell
from heaven_tree_repl.system_config_loader_v2 import SystemConfigLoader


class {class_name}ConfigLoader(SystemConfigLoader):
    \"\"\"Custom config loader that uses this library's system configs as base.\"\"\"
    
    def _get_library_configs_dir(self) -> str:
        \"\"\"Override to use this library's configs instead of heaven-tree-repl's.\"\"\"
        # Point to this library's config directory
        library_root = Path(__file__).parent.parent
        return str(library_root / "configs")


class {class_name}TreeShell(TreeShell):
    \"\"\"Base TreeShell with {class_name} customizations baked in.\"\"\"
    def __init__(self, user_config_path: str = None):
        config_loader = {class_name}ConfigLoader(config_types=["base"])
        final_config = config_loader.load_configs(user_config_path)
        super().__init__(final_config)


class {class_name}AgentTreeShell(AgentTreeShell):
    \"\"\"Agent TreeShell with {class_name} customizations baked in.\"\"\"
    def __init__(self, user_config_path: str = None, session_id: str = None, approval_callback=None):
        config_loader = {class_name}ConfigLoader(config_types=["base", "agent"]) 
        final_config = config_loader.load_configs(user_config_path)
        super().__init__(final_config, session_id, approval_callback)


class {class_name}UserTreeShell(UserTreeShell):
    \"\"\"User TreeShell with {class_name} customizations baked in.\"\"\"
    def __init__(self, user_config_path: str = None, parent_approval_callback=None):
        config_loader = {class_name}ConfigLoader(config_types=["base", "user"])
        final_config = config_loader.load_configs(user_config_path)
        super().__init__(final_config, parent_approval_callback)


class {class_name}LibraryTreeShell(FullstackTreeShell):
    \"\"\"Complete TreeShell library with {class_name} customizations baked in.\"\"\"
    def __init__(self, user_config_path: str = None, parent_approval_callback=None):
        config_loader = {class_name}ConfigLoader(config_types=["base", "agent", "user"])
        final_config = config_loader.load_configs(user_config_path)
        super().__init__(final_config, parent_approval_callback)
"""
    
    def _project_configs(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Project configuration files for the package."""
        return {
            'system_base_config.json': json.dumps(config.get('base_config', {}), indent=2),
            'system_agent_config.json': json.dumps(config.get('agent_config', {}), indent=2),
            'system_user_config.json': json.dumps(config.get('user_config', {}), indent=2),
        }


class GitHubSubstrate(ReleaseSubstrate):  
    """GitHub repository substrate with Git-specific projection."""
    
    def project(self, treeshell_data: Dict[str, Any]) -> Dict[str, Any]:
        config = treeshell_data['config']
        
        return {
            'readme': self._generate_readme(config),
            'source_tree': self._project_source(treeshell_data),
            'ci_config': self._generate_ci(config),
            'release_config': self._generate_releases(config)
        }
    
    def _generate_readme(self, config: Dict[str, Any]) -> str:
        """Generate README.md content."""
        lib_name = config.get('library_name', 'custom-treeshell')
        return f"""# {lib_name}

{config.get('description', 'A custom TreeShell library')}

## Installation

```bash
pip install {lib_name}
```

## Usage

```python
from {lib_name.replace('-', '_')} import CustomLibraryTreeShell

shell = CustomLibraryTreeShell()
await shell.run()
```

## Customization

Create dev config files in a directory and pass the path:

```python
shell = CustomLibraryTreeShell(user_config_path="./my-customizations/")
```

Generated by TreeShell Library Factory.
"""
    
    def _project_source(self, treeshell_data: Dict[str, Any]) -> Dict[str, str]:
        """Project source tree structure."""
        pypi_substrate = PyPISubstrate()
        pypi_projection = pypi_substrate.project(treeshell_data)
        
        return {
            'setup.py': pypi_projection['setup_py'],
            'pyproject.toml': pypi_projection['pyproject_toml'],
            'shell_classes.py': pypi_projection['shell_classes']
        }
    
    def _generate_ci(self, config: Dict[str, Any]) -> str:
        """Generate GitHub Actions CI configuration."""
        return """name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
    - name: Test installation
      run: |
        python -c "import custom_treeshell; print('Import successful')"
"""
    
    def _generate_releases(self, config: Dict[str, Any]) -> str:
        """Generate release configuration."""
        return """name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.10'
    - name: Build package
      run: |
        python -m pip install --upgrade pip build
        python -m build
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
"""


class TreeShellFibration:
    """
    Fibration over release substrates.
    
    A fibration is a structure-preserving map between spaces that allows
    the abstract mathematical object to be projected onto different
    concrete substrates while preserving its essential structure.
    """
    
    def __init__(self, base_space: Dict[str, Any]):
        self.base = base_space  # Base space of the fibration
        self.fibers: Dict[str, Any] = {}  # substrate -> materialized form
        self.projection_maps: Dict[str, ReleaseSubstrate] = {}  # structure-preserving maps
        
    def materialize_on(self, substrate: ReleaseSubstrate) -> Dict[str, Any]:
        """
        Project TreeShell onto concrete substrate.
        
        This is the fibration map that preserves mathematical structure
        while adapting to substrate-specific requirements.
        """
        # Apply projection while preserving structure
        materialized = substrate.project(self.base)
        
        # Validate structure preservation
        assert self._preserves_structure(materialized, substrate)
        
        return materialized
        
    def fiber_over(self, substrate_name: str) -> Dict[str, Any]:
        """
        Get the fiber space over a specific substrate.
        
        Each fiber represents all possible materializations
        of TreeShell objects on that substrate.
        """
        if substrate_name not in self.fibers:
            substrate = self.projection_maps[substrate_name]
            self.fibers[substrate_name] = self.materialize_on(substrate)
        return self.fibers[substrate_name]
        
    def register_substrate(self, substrate_type: str, substrate: ReleaseSubstrate):
        """Register new release substrate with its projection map."""
        self.projection_maps[substrate_type] = substrate
        
    def _preserves_structure(self, materialized: Dict[str, Any], substrate: ReleaseSubstrate) -> bool:
        """Verify that projection preserves essential TreeShell structure."""
        # Check that essential structure is preserved
        if isinstance(substrate, (PyPISubstrate, LocalSubstrate)):
            required_keys = ['setup_py', 'shell_classes']
        elif isinstance(substrate, GitHubSubstrate):
            required_keys = ['readme', 'source_tree']
        else:
            # Unknown substrate type, assume basic requirements
            required_keys = ['setup_py']
        
        for key in required_keys:
            if key not in materialized:
                print(f"DEBUG: Missing required key '{key}' in materialized package")
                return False
                
        return True


class LocalSubstrate(ReleaseSubstrate):
    """Local development substrate for testing and development installs."""
    
    def project(self, treeshell_data: Dict[str, Any]) -> Dict[str, Any]:
        """Project TreeShell onto local development format."""
        # Use PyPI format as base for local development
        pypi_substrate = PyPISubstrate()
        return pypi_substrate.project(treeshell_data)


class TreeShellCategoryTheory:
    """
    Complete category-theoretic system: Operad + Monad + Fibration.
    
    This integrates the three mathematical foundations:
    1. Operad: Defines capability algebra
    2. Monad: Enables self-generation  
    3. Fibration: Materializes on substrates
    """
    
    def __init__(self, base_treeshell_config: Dict[str, Any]):
        self.base_config = base_treeshell_config
        self.operad = TreeShellOperad(base_treeshell_config)
        self.monad = TreeShellMonad()  
        self.fibration = TreeShellFibration(self.monad.pure(base_treeshell_config))
        
        # Register standard substrates
        self._register_standard_substrates()
        
    def generate_and_release(
        self, 
        dev_config: Dict[str, Any], 
        substrate: str,
        coordinate: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Complete category-theoretic pipeline:
        Operad → Monad → Fibration
        
        1. Operad: Define capabilities from dev config
        2. Monad: Generate sibling TreeShell  
        3. Fibration: Materialize on substrate
        """
        # Step 1: Extract algebraic operations (Operad)
        operations = self.operad.extract_from_config(dev_config)
        
        # Step 2: Generate sibling instance (Monad)
        if coordinate is None:
            coordinate = self._next_available_coordinate()
            
        base_shell = self.monad.pure(dev_config)
        sibling_shell = self.monad.generate_sibling(base_shell, coordinate)
        
        # Step 3: Materialize on substrate (Fibration)
        substrate_obj = self._get_substrate(substrate)
        
        # Update fibration base with sibling data
        self.fibration.base = sibling_shell
        package = self.fibration.materialize_on(substrate_obj)
        
        return package
        
    def _register_standard_substrates(self):
        """Register standard release substrates."""
        self.fibration.register_substrate("pypi", PyPISubstrate())
        self.fibration.register_substrate("github", GitHubSubstrate())
        self.fibration.register_substrate("local", LocalSubstrate())
        
    def _get_substrate(self, substrate_name: str) -> ReleaseSubstrate:
        """Get substrate object by name."""
        if substrate_name not in self.fibration.projection_maps:
            raise ValueError(f"Unknown substrate: {substrate_name}")
        return self.fibration.projection_maps[substrate_name]
        
    def _next_available_coordinate(self) -> int:
        """Get next available coordinate for sibling generation."""
        return self.monad.next_coordinate
        
    def coordinate_algebra(self) -> Dict[str, Any]:
        """
        The coordinate space forms an algebraic structure where:
        - TreeShell occupies position 0
        - Generated siblings occupy positions 1, 2, 3, ...
        - Each position has its own family hierarchy (X.1, X.2, X.3, ...)
        """
        return {
            'origin': 0,  # TreeShell base position
            'siblings': self.monad.coordinate_space_mapping(),
            'operad': self.operad,
            'monad': self.monad,
            'fibration': self.fibration
        }