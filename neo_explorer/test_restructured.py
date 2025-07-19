#!/usr/bin/env python3
"""
Test script for the NEO Explorer application.

This script tests the basic functionality of the application
to ensure it works correctly with the original data files.
"""

import sys
from pathlib import Path
from datetime import date

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from neo_explorer.data.loader import DataLoader
from neo_explorer.core.database import NEODatabase
from neo_explorer.utils.filters import FilterFactory
from neo_explorer.utils.formatters import DataFormatter


def test_data_loading():
    """Test data loading functionality."""
    print("Testing data loading...")
    
    # Initialize data loader
    loader = DataLoader(validate_data=True, strict_mode=False)
    
    # Load database
    neo_file = Path(__file__).parent / "data" / "neos.csv"
    cad_file = Path(__file__).parent / "data" / "cad.json"
    
    database = loader.load_database(neo_file, cad_file)
    
    # Check statistics
    stats = database.get_statistics()
    print(f"Database loaded successfully:")
    print(f"  NEOs: {stats['total_neos']}")
    print(f"  Close approaches: {stats['total_approaches']}")
    print(f"  Hazardous NEOs: {stats['hazardous_neos']}")
    print(f"  Named NEOs: {stats['named_neos']}")
    print(f"  NEOs with diameter: {stats['neos_with_diameter']}")
    
    return database


def test_neo_lookup(database):
    """Test NEO lookup functionality."""
    print("\nTesting NEO lookup...")
    
    # Test lookup by designation
    neo = database.get_neo_by_designation("433")
    if neo:
        print(f"Found NEO by designation '433': {neo}")
    else:
        print("NEO with designation '433' not found")
    
    # Test lookup by name
    neo = database.get_neo_by_name("Eros")
    if neo:
        print(f"Found NEO by name 'Eros': {neo}")
    else:
        print("NEO with name 'Eros' not found")


def test_query_functionality(database):
    """Test query functionality."""
    print("\nTesting query functionality...")
    
    # Test query with date filter
    filters = FilterFactory.create_filters(date=date(2020, 1, 1))
    approaches = list(database.query(filters.filters))
    print(f"Found {len(approaches)} close approaches on 2020-01-01")
    
    if approaches:
        print(f"First approach: {approaches[0]}")
    
    # Test query with multiple filters
    filters = FilterFactory.create_filters(
        start_date=date(2020, 1, 1),
        end_date=date(2020, 1, 31),
        distance_max=0.025
    )
    approaches = list(database.query(filters.filters))
    print(f"Found {len(approaches)} close approaches in Jan 2020 within 0.025 au")
    
    # Test hazardous query
    filters = FilterFactory.create_filters(hazardous=True)
    approaches = list(database.query(filters.filters))
    print(f"Found {len(approaches)} close approaches of hazardous NEOs")


def test_search_functionality(database):
    """Test search functionality."""
    print("\nTesting search functionality...")
    
    # Search for NEOs
    results = database.search_neos("Eros", limit=5)
    print(f"Found {len(results)} NEOs matching 'Eros'")
    
    for neo in results:
        print(f"  - {neo}")


def test_special_queries(database):
    """Test special query methods."""
    print("\nTesting special queries...")
    
    # Closest approaches
    closest = database.get_closest_approaches(limit=3)
    print(f"Closest {len(closest)} approaches:")
    for approach in closest:
        print(f"  - {approach}")
    
    # Fastest approaches
    fastest = database.get_fastest_approaches(limit=3)
    print(f"Fastest {len(fastest)} approaches:")
    for approach in fastest:
        print(f"  - {approach}")


def test_formatting():
    """Test data formatting functionality."""
    print("\nTesting data formatting...")
    
    # Test NEO formatting
    from neo_explorer.core.models import NearEarthObject
    
    neo = NearEarthObject(
        designation="TEST123",
        name="Test Asteroid",
        diameter=1.5,
        hazardous=True
    )
    
    print("NEO formatted as text:")
    print(DataFormatter.format_neo(neo, "text"))
    
    print("\nNEO formatted as JSON:")
    print(DataFormatter.format_neo(neo, "json"))


def main():
    """Run all tests."""
    print("NEO Explorer - Restructured Application Test")
    print("=" * 50)
    
    try:
        # Test data loading
        database = test_data_loading()
        
        # Test various functionalities
        test_neo_lookup(database)
        test_query_functionality(database)
        test_search_functionality(database)
        test_special_queries(database)
        test_formatting()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        print("The restructured application is working correctly.")
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 