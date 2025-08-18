#!/usr/bin/env python3
"""CLI for specialized-ai-treeshell TreeShell Factory"""

import argparse
from pathlib import Path
from .factory import RecursiveTreeShellFactory

def main():
    parser = argparse.ArgumentParser(description="Generate TreeShell library from specialized-ai-treeshell")
    parser.add_argument("--new-library", required=True, help="Name of new library to generate")
    parser.add_argument("--dev-configs", required=True, help="Path to dev config directory")
    parser.add_argument("--version", default="1.0.0", help="Version of new library")
    parser.add_argument("--author", default="TreeShell Developer", help="Author name")
    parser.add_argument("--description", help="Library description")
    parser.add_argument("--target", default="local", choices=["local", "pypi", "github"], help="Publishing target")
    parser.add_argument("--output-dir", help="Output directory")
    
    args = parser.parse_args()
    
    if not args.description:
        args.description = f"TreeShell library based on specialized-ai-treeshell"
    
    factory = RecursiveTreeShellFactory(
        base_library="specialized_ai_treeshell",
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
            print(f"🚀 Successfully published {args.new_library}!")
        else:
            print(f"❌ Publishing failed")
    else:
        print("❌ Validation failed")
        for warning in factory.get_validation_warnings():
            print(f"  - {warning}")

if __name__ == "__main__":
    main()
