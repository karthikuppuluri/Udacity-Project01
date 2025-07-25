#!/usr/bin/env python3
"""
Verification script for Project01.

This script verifies that all components are working correctly.
"""

import sys
from pathlib import Path

print("Project01 Verification Script")
print("=" * 50)

# Check file structure
print("\n Checking file structure...")
required_files = [
    'main.py',
    'models.py', 
    'extract.py',
    'database.py',
    'filters.py',
    'write.py',
    'helpers.py'
]

for file in required_files:
    if Path(file).exists():
        print(f"Passed: {file}")
    else:
        print(f"{file} - MISSING")

# Check directories
print("\nChecking directories...")
required_dirs = ['data', 'tests', 'res']
for dir_name in required_dirs:
    if Path(dir_name).exists():
        print(f"Passed: {dir_name}/")
    else:
        print(f"{dir_name}/ - MISSING")

# Check data files
print("\nChecking data files...")
data_files = ['data/neos.csv', 'data/cad.json']
for file in data_files:
    path = Path(file)
    if path.exists():
        size = path.stat().st_size
        print(f"Passed: {file} ({size:,} bytes)")
    else:
        print(f"{file} - MISSING")

# Test imports
print("\n🔧 Testing imports...")
try:
    from models import NearEarthObject, CloseApproach
    print("Passed: models.py")
except Exception as e:
    print(f"models.py: {e}")

try:
    from helpers import cd_to_datetime, datetime_to_str
    print("Passed: helpers.py")
except Exception as e:
    print(f"helpers.py: {e}")

try:
    from extract import load_neos, load_approaches
    print("Passed: extract.py")
except Exception as e:
    print(f"extract.py: {e}")

try:
    from database import NEODatabase
    print("Passed: database.py")
except Exception as e:
    print(f"database.py: {e}")

try:
    from filters import create_filters, limit
    print("Passed: filters.py")
except Exception as e:
    print(f"filters.py: {e}")

try:
    from write import write_to_csv, write_to_json
    print("Passed: write.py")
except Exception as e:
    print(f"write.py: {e}")

# Test basic functionality
print("\nTesting basic functionality...")
try:
    from models import NearEarthObject, CloseApproach
    from datetime import datetime
    
    neo = NearEarthObject("433", "Eros", 16.84, False)
    print(f"Passed: Created NEO: {neo}")
    
    approach = CloseApproach(
        datetime(2020, 1, 1, 12, 0),
        0.025,
        15.5,
        "433"
    )
    print(f"Passed: Created CloseApproach: {approach}")
    
    from helpers import cd_to_datetime
    dt = cd_to_datetime("2020-Jan-01 12:00")
    print(f"Passed: Date conversion: {dt}")
    
except Exception as e:
    print(f"Basic functionality failed: {e}")

# Test CLI
print("\nTesting CLI...")
try:
    import subprocess
    result = subprocess.run([sys.executable, 'main.py', '--help'], 
                          capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        print("Passed: CLI help works")
    else:
        print(f"CLI help failed: {result.stderr}")
except Exception as e:
    print(f"CLI test failed: {e}")

print("\n" + "=" * 50)
print("Verification complete!") 