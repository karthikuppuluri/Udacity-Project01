"""
Command-line interface for NEO Explorer.

This module provides the command-line interface and interactive shell
for the NEO Explorer application.
"""

from .main import main
from .shell import NEOShell

__all__ = ['main', 'NEOShell'] 