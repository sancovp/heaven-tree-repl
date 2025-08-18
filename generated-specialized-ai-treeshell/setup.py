#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="specialized-ai-treeshell",
    version="1.0.0",
    author="AI Specialist",
    description="Specialized AI TreeShell built on domain library",
    packages=find_packages(),
    install_requires=[
        "my_domain_treeshell",
    ],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'specialized_ai_treeshell-factory=specialized_ai_treeshell.cli:main',
        ],
    },
)
