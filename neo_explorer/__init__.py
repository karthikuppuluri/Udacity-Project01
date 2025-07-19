"""
NEO Explorer - A robust and efficient tool for exploring Near-Earth Objects.

This package provides functionality to analyze and query data about near-Earth objects
and their close approaches to Earth using NASA/JPL data.

Main components:
- Core models for NEOs and close approaches
- Data loading and processing utilities
- Query and filtering capabilities
- Command-line interface
- Interactive shell
"""

__version__ = "1.0.0"
__author__ = "Karthik Uppuluri"
__description__ = "A tool for exploring Near-Earth Objects and their close approaches"

from .core.models import NearEarthObject, CloseApproach
from .core.database import NEODatabase
from .data.loader import DataLoader
from .utils.filters import FilterFactory
from .cli.main import main

__all__ = [
    'NearEarthObject',
    'CloseApproach', 
    'NEODatabase',
    'DataLoader',
    'FilterFactory',
    'main'
] 