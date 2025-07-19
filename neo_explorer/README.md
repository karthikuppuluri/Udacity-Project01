# NEO Explorer

A robust and efficient tool for exploring Near-Earth Objects (NEOs) and their close approaches to Earth using NASA/JPL data.

## Features

- **High Performance**: Optimized database with efficient indexing and caching
- **Comprehensive Filtering**: Query close approaches by date, distance, velocity, diameter, and hazard status
- **Multiple Output Formats**: Support for CSV, JSON, and human-readable text output
- **Interactive Shell**: Command-line interface with REPL for exploratory data analysis
- **Data Validation**: Robust error handling and data validation
- **Extensible Architecture**: Modular design for easy extension and customization
- **Type Safety**: Full type hints and validation throughout the codebase

## Installation

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd neo-explorer

# Install the package
pip install -e .
```

### Direct Usage

```bash
# Run directly from the source directory
python neo_explorer/main.py --help
```

## Quick Start

### Basic Usage

```bash
# Inspect an NEO by designation
neo-explorer inspect --pdes 433

# Inspect an NEO by name with verbose output
neo-explorer inspect --name Eros --verbose

# Query close approaches on a specific date
neo-explorer query --date 2020-01-01

# Query with multiple filters
neo-explorer query --start-date 2020-01-01 --end-date 2020-01-31 --max-distance 0.025

# Query hazardous NEOs
neo-explorer query --hazardous --max-distance 0.05 --min-velocity 30

# Save results to file
neo-explorer query --limit 5 --outfile results.csv
neo-explorer query --limit 5 --outfile results.json

# Start interactive shell
neo-explorer interactive
```

### Interactive Shell Commands

```bash
# Start the interactive shell
neo-explorer interactive

# Available commands:
(neo) help                    # Show available commands
(neo) inspect --pdes 433      # Inspect NEO by designation
(neo) inspect --name Eros     # Inspect NEO by name
(neo) query --date 2020-01-01 # Query close approaches
(neo) search Eros             # Search for NEOs
(neo) closest --limit 5       # Show closest approaches
(neo) fastest --limit 5       # Show fastest approaches
(neo) recent --limit 5        # Show recent approaches
(neo) stats                   # Show database statistics
(neo) exit                    # Exit the shell
```

## Command Reference

### Global Options

- `--neofile PATH`: Path to NEO CSV file (default: data/neos.csv)
- `--cadfile PATH`: Path to close approach JSON file (default: data/cad.json)
- `--verbose, -v`: Enable verbose output
- `--strict`: Enable strict mode (fail on data validation errors)

### Inspect Command

Inspect an NEO by primary designation or name.

```bash
neo-explorer inspect [OPTIONS]

Options:
  --pdes, -p TEXT     Primary designation of the NEO
  --name, -n TEXT     IAU name of the NEO
  --verbose, -v       Show all close approaches
```

### Query Command

Query for close approaches matching specified criteria.

```bash
neo-explorer query [OPTIONS]

Filter Options:
  --date, -d TEXT           Exact date (YYYY-MM-DD)
  --start-date, -s TEXT     Start date (YYYY-MM-DD)
  --end-date, -e TEXT       End date (YYYY-MM-DD)
  --min-distance FLOAT      Minimum distance (au)
  --max-distance FLOAT      Maximum distance (au)
  --min-velocity FLOAT      Minimum velocity (km/s)
  --max-velocity FLOAT      Maximum velocity (km/s)
  --min-diameter FLOAT      Minimum diameter (km)
  --max-diameter FLOAT      Maximum diameter (km)
  --hazardous               Only hazardous NEOs
  --not-hazardous           Only non-hazardous NEOs

Output Options:
  --limit, -l INTEGER       Maximum results (default: 10)
  --outfile, -o PATH        Save to file (CSV/JSON)
  --format TEXT             Output format (text/csv/json)
```

### Interactive Command

Start an interactive command session.

```bash
neo-explorer interactive [OPTIONS]

Options:
  --aggressive, -a    Kill session when files are modified
```

## Configuration

The application can be configured using environment variables:

```bash
# Data file paths
export NEO_FILE=/path/to/neos.csv
export CAD_FILE=/path/to/cad.json

# Data loading settings
export VALIDATE_DATA=true
export STRICT_MODE=false
export ENCODING=utf-8

# Query settings
export DEFAULT_LIMIT=10
export MAX_LIMIT=10000

# Output settings
export DEFAULT_FORMAT=text
export PRETTY_JSON=true

# Logging settings
export LOG_LEVEL=INFO

# Performance settings
export CACHE_ENABLED=true
export CACHE_SIZE=1000
```

## Architecture

The application is organized into several modules:

- **core**: Core data models and database functionality
- **data**: Data loading and parsing utilities
- **utils**: Filtering, formatting, and validation utilities
- **cli**: Command-line interface and interactive shell
- **config**: Configuration management

### Key Components

- **NearEarthObject**: Represents an NEO with properties like designation, name, diameter, and hazard status
- **CloseApproach**: Represents a close approach with time, distance, velocity, and NEO reference
- **NEODatabase**: High-performance database with indexing and querying capabilities
- **DataLoader**: Robust data loading with validation and error handling
- **FilterFactory**: Flexible filtering system for querying close approaches

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy neo_explorer/

# Run linting
flake8 neo_explorer/
black neo_explorer/
```

### Project Structure

```
neo_explorer/
├── __init__.py
├── main.py
├── setup.py
├── requirements.txt
├── README.md
├── core/
│   ├── __init__.py
│   ├── models.py
│   └── database.py
├── data/
│   ├── __init__.py
│   ├── loader.py
│   └── parsers.py
├── utils/
│   ├── __init__.py
│   ├── filters.py
│   ├── formatters.py
│   └── validators.py
├── cli/
│   ├── __init__.py
│   ├── main.py
│   └── shell.py
└── config/
    ├── __init__.py
    └── settings.py
```

## Performance

The restructured application includes several performance optimizations:

- **Efficient Indexing**: Multiple indexes for fast lookups by designation, name, date, and other criteria
- **Memory Optimization**: Lazy loading and efficient data structures
- **Caching**: Configurable caching for frequently accessed data
- **Streaming**: Iterator-based processing for large datasets
- **Optimized Queries**: Smart filtering and query optimization

## Error Handling

The application provides comprehensive error handling:

- **Data Validation**: Robust validation of input data and user arguments
- **Graceful Degradation**: Continues operation even with some data errors
- **Detailed Error Messages**: Clear and helpful error messages
- **Logging**: Comprehensive logging for debugging and monitoring
- **Exception Hierarchy**: Well-defined exception types for different error conditions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NASA/JPL for providing the NEO data
- The original Udacity project for the initial concept
- The Python community for excellent tools and libraries 