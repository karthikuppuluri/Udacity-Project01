#!/usr/bin/env python3
"""
Main entry point for NEO Explorer.

This script provides the command-line interface for the NEO Explorer application.
It can be run directly or imported as a module.

Usage:
    python -m neo_explorer.main [command] [options]
    python neo_explorer/main.py [command] [options]
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from neo_explorer.cli.main import main

if __name__ == '__main__':
    sys.exit(main()) 