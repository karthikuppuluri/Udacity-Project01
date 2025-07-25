PROJECT: EXPLORING NEAR-EARTH OBJECTS
=====================================

This project implements a command-line tool for exploring and analyzing Near-Earth Objects (NEOs) 
and their close approaches to Earth. The tool can load data from CSV and JSON files, filter 
results based on various criteria, and output results in CSV or JSON format.

FEATURES
========

1. DATA MODELS
   - NearEarthObject: Represents NEOs with designation, name, diameter, hazardous status
   - CloseApproach: Represents close approaches with time, distance, velocity
   - Serialize methods for consistent data output

2. DATA EXTRACTION
   - Load NEO data from CSV files
   - Load close approach data from JSON files
   - Handle missing or invalid data gracefully

3. DATABASE FUNCTIONALITY
   - NEODatabase class for data management
   - Indexing for efficient lookups
   - Link NEOs with their close approaches

4. FILTERING AND QUERYING
   - Date-based filtering (single date, date ranges)
   - Distance filtering (min/max distance)
   - Velocity filtering (min/max velocity)
   - Diameter filtering (min/max diameter)
   - Hazardous status filtering
   - Composite filters for complex queries

5. OUTPUT CAPABILITIES
   - CSV output with exact format specification
   - JSON output with nested structure
   - Consistent handling of edge cases

6. COMMAND-LINE INTERFACE
   - Three subcommands: inspect, query, interactive
   - Comprehensive argument parsing
   - Help documentation

USAGE
=====

1. INSPECT DATA
   python main.py inspect
   - Shows basic information about loaded data
   - Displays NEO count and close approach count

2. QUERY DATA
   Basic query:
   python main.py query --date 2020-01-01 --limit 5

   Advanced query with filters:
   python main.py query --start-date 2020-01-01 --end-date 2020-12-31 
                        --hazardous --min-diameter 0.25 --max-distance 0.1 
                        --limit 10 --outfile results.json

   Available query options:
   --date DATE              Single date filter (YYYY-MM-DD)
   --start-date DATE        Start date for range filter
   --end-date DATE          End date for range filter
   --min-distance DISTANCE  Minimum distance filter (AU)
   --max-distance DISTANCE  Maximum distance filter (AU)
   --min-velocity VELOCITY  Minimum velocity filter (km/s)
   --max-velocity VELOCITY  Maximum velocity filter (km/s)
   --min-diameter DIAMETER  Minimum diameter filter (km)
   --max-diameter DIAMETER  Maximum diameter filter (km)
   --hazardous              Filter for hazardous NEOs only
   --not-hazardous          Filter for non-hazardous NEOs only
   --limit N                Limit results to first N entries
   --outfile FILENAME       Save results to file (CSV or JSON)

3. INTERACTIVE MODE
   python main.py interactive
   - Interactive query builder
   - Step-by-step filter selection
   - Real-time result preview

4. OUTPUT FILES
   CSV Format:
   - Header: datetime_utc,distance_au,velocity_km_s,designation,name,diameter_km,potentially_hazardous
   - Data rows with proper formatting

   JSON Format:
   - Array of objects with datetime_utc, distance_au, velocity_km_s
   - Nested neo object with designation, name, diameter_km, potentially_hazardous

EXAMPLES
========

1. Find all close approaches on January 1, 2020:
   python main.py query --date 2020-01-01

2. Find hazardous NEOs larger than 1km that came within 0.1 AU:
   python main.py query --hazardous --min-diameter 1.0 --max-distance 0.1

3. Save first 10 results to CSV:
   python main.py query --limit 10 --outfile results.csv

4. Complex query with date range and multiple filters:
   python main.py query --start-date 2020-01-01 --end-date 2020-12-31 
                        --hazardous --min-diameter 0.25 --max-distance 0.1 
                        --limit 5 --outfile hazardous_approaches.json

TESTING
=======

Run all unit tests:
python -m unittest discover tests

Run specific test modules:
python -m unittest tests.test_write
python -m unittest tests.test_database
python -m unittest tests.test_filters

Run basic functionality test:
python test_basic.py

Run serialize method test:
python test_serialize.py

Run verification script:
python verify.py

REQUIREMENTS
===========

- Python 3.6 or higher
- No external dependencies (uses only Python standard library)
- Data files: neos.csv and cad.json in data/ directory

DATA FORMATS
============

NEO Data (neos.csv):
- designation: Primary designation (string)
- name: IAU name (string, can be empty)
- diameter: Diameter in kilometers (float, can be NaN)
- hazardous: Potentially hazardous flag (boolean)

Close Approach Data (cad.json):
- cd: Calendar date (string, format: "YYYY-MMM-DD HH:MM")
- dist: Distance in AU (float)
- v_rel: Relative velocity in km/s (float)
- des: Primary designation (string)

IMPLEMENTATION DETAILS
=====================

1. MODELS (models.py)
   - NearEarthObject: Handles missing names and diameters
   - CloseApproach: Links to NEO objects
   - Serialize methods for consistent output

2. EXTRACTION (extract.py)
   - CSV parsing with csv module
   - JSON parsing with json module
   - Error handling for malformed data

3. DATABASE (database.py)
   - In-memory database with indexing
   - Efficient lookup by designation or name
   - Links NEOs and close approaches

4. FILTERS (filters.py)
   - Abstract base class for filters
   - Concrete filter implementations
   - Composite filter support
   - Limit function for result truncation

5. OUTPUT (write.py)
   - CSV writing with exact format
   - JSON writing with nested structure
   - Edge case handling via serialize methods

6. CLI (main.py)
   - ArgumentParser for command-line interface
   - Three subcommands with comprehensive options
   - Error handling and user feedback


EXTENSIBILITY
=============

- Modular design allows easy addition of new filters
- Abstract base classes for extensible filter system
- Serialize methods enable custom output formats
- Database class can be extended for additional query types

AUTHOR
======

Karthik Uppuluri