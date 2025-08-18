#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="my-domain-treeshell",
    version="1.0.0",
    author="Domain Expert",
    description="Domain-specific TreeShell with specialized features",
    packages=find_packages(),
    install_requires=[
        "heaven_tree_repl",
    ],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'my_domain_treeshell-factory=my_domain_treeshell.cli:main',
        ],
    },
)
