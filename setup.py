#!/usr/bin/env python3
"""Setup script for heaven-tree-repl package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="heaven-tree-repl",
    version="0.1.29",
    author="HEAVEN Development Team",
    author_email="heaven@example.com",
    description="Hierarchical Embodied Autonomously Validating Evolution Network Tree REPL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/heaven-tree-repl",
    packages=find_packages(),
    package_data={
        "heaven-tree-repl": [
            "configs/*.json",
            "shortcuts/*.json",
        ],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "jinja2>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
            "mypy",
        ],
    },
    entry_points={
        "console_scripts": [
            "heaven-tree-repl=heaven_tree_repl.cli:main",
        ],
    },
)