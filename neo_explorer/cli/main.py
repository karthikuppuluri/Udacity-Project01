"""
Main command-line interface for NEO Explorer.

This module provides the main entry point for the NEO Explorer application
with comprehensive argument parsing, error handling, and command execution.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Optional

from ..data.loader import DataLoader, DataLoadError
from ..core.database import NEODatabase
from ..utils.filters import FilterFactory, limit
from ..utils.formatters import OutputWriter
from ..utils.validators import InputValidator, ValidationError
from .shell import NEOShell


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """
    Create the main argument parser for the CLI.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="Explore past and future close approaches of near-Earth objects.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s inspect --pdes 433
  %(prog)s inspect --name Eros --verbose
  %(prog)s query --date 2020-01-01
  %(prog)s query --start-date 2020-01-01 --end-date 2020-01-31 --max-distance 0.025
  %(prog)s query --hazardous --max-distance 0.05 --min-velocity 30
  %(prog)s interactive
        """
    )
    
    # Global options
    parser.add_argument(
        '--neofile',
        type=Path,
        default=Path('data/neos.csv'),
        help="Path to CSV file of near-Earth objects (default: data/neos.csv)"
    )
    parser.add_argument(
        '--cadfile',
        type=Path,
        default=Path('data/cad.json'),
        help="Path to JSON file of close approach data (default: data/cad.json)"
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Enable verbose output"
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help="Enable strict mode (fail on data validation errors)"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Inspect command
    inspect_parser = subparsers.add_parser(
        'inspect',
        help="Inspect an NEO by primary designation or name"
    )
    inspect_parser.add_argument(
        '--pdes', '-p',
        help="The primary designation of the NEO to inspect (e.g., '433')"
    )
    inspect_parser.add_argument(
        '--name', '-n',
        help="The IAU name of the NEO to inspect (e.g., 'Eros')"
    )
    inspect_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Additionally, print all known close approaches of this NEO"
    )
    
    # Query command
    query_parser = subparsers.add_parser(
        'query',
        help="Query for close approaches that match specified criteria"
    )
    
    # Query filters
    filters_group = query_parser.add_argument_group('Filters')
    filters_group.add_argument(
        '--date', '-d',
        help="Only return close approaches on the given date (YYYY-MM-DD)"
    )
    filters_group.add_argument(
        '--start-date', '-s',
        help="Only return close approaches on or after the given date (YYYY-MM-DD)"
    )
    filters_group.add_argument(
        '--end-date', '-e',
        help="Only return close approaches on or before the given date (YYYY-MM-DD)"
    )
    filters_group.add_argument(
        '--min-distance',
        type=float,
        help="Minimum approach distance in astronomical units"
    )
    filters_group.add_argument(
        '--max-distance',
        type=float,
        help="Maximum approach distance in astronomical units"
    )
    filters_group.add_argument(
        '--min-velocity',
        type=float,
        help="Minimum relative approach velocity in km/s"
    )
    filters_group.add_argument(
        '--max-velocity',
        type=float,
        help="Maximum relative approach velocity in km/s"
    )
    filters_group.add_argument(
        '--min-diameter',
        type=float,
        help="Minimum NEO diameter in kilometers"
    )
    filters_group.add_argument(
        '--max-diameter',
        type=float,
        help="Maximum NEO diameter in kilometers"
    )
    filters_group.add_argument(
        '--hazardous',
        action='store_true',
        help="Only return close approaches of potentially hazardous NEOs"
    )
    filters_group.add_argument(
        '--not-hazardous',
        action='store_true',
        help="Only return close approaches of non-hazardous NEOs"
    )
    
    # Query output options
    output_group = query_parser.add_argument_group('Output Options')
    output_group.add_argument(
        '--limit', '-l',
        type=int,
        default=10,
        help="Maximum number of results to return (default: 10)"
    )
    output_group.add_argument(
        '--outfile', '-o',
        type=Path,
        help="File to save results (CSV or JSON format based on extension)"
    )
    output_group.add_argument(
        '--format',
        choices=['text', 'csv', 'json'],
        default='text',
        help="Output format when not saving to file (default: text)"
    )
    
    # Interactive command
    interactive_parser = subparsers.add_parser(
        'interactive',
        help="Start an interactive command session"
    )
    interactive_parser.add_argument(
        '--aggressive', '-a',
        action='store_true',
        help="Kill the session when project files are modified"
    )
    
    return parser


def validate_args(args: argparse.Namespace) -> None:
    """
    Validate command-line arguments.
    
    Args:
        args: Parsed arguments
        
    Raises:
        ValidationError: If arguments are invalid
    """
    # Check that required files exist
    if not args.neofile.exists():
        raise ValidationError(f"NEO file not found: {args.neofile}")
    
    if not args.cadfile.exists():
        raise ValidationError(f"Close approach file not found: {args.cadfile}")
    
    # Validate command-specific arguments
    if args.command == 'inspect':
        if not args.pdes and not args.name:
            raise ValidationError("Either --pdes or --name must be specified for inspect command")
    
    elif args.command == 'query':
        # Validate that at least one filter is specified
        filter_args = [
            args.date, args.start_date, args.end_date,
            args.min_distance, args.max_distance,
            args.min_velocity, args.max_velocity,
            args.min_diameter, args.max_diameter,
            args.hazardous, args.not_hazardous
        ]
        
        if not any(filter_args):
            logger.warning("No filters specified - will return all close approaches")
        
        # Validate conflicting options
        if args.hazardous and args.not_hazardous:
            raise ValidationError("Cannot specify both --hazardous and --not-hazardous")
        
        # Validate date range
        if args.start_date and args.end_date:
            try:
                start = InputValidator.validate_query_args({'start_date': args.start_date})['start_date']
                end = InputValidator.validate_query_args({'end_date': args.end_date})['end_date']
                if start > end:
                    raise ValidationError("Start date must be before or equal to end date")
            except ValidationError:
                pass  # Let the individual validation handle the error


def load_database(neo_file: Path, cad_file: Path, strict_mode: bool = False) -> NEODatabase:
    """
    Load the NEO database from files.
    
    Args:
        neo_file: Path to NEO CSV file
        cad_file: Path to close approach JSON file
        strict_mode: Whether to enable strict mode
        
    Returns:
        Loaded NEODatabase instance
        
    Raises:
        DataLoadError: If loading fails
    """
    logger.info("Loading NEO database...")
    
    loader = DataLoader(validate_data=True, strict_mode=strict_mode)
    database = loader.load_database(neo_file, cad_file)
    
    # Log loading statistics
    stats = loader.get_statistics()
    logger.info(f"Database loaded successfully:")
    logger.info(f"  NEOs loaded: {stats['neos_loaded']}")
    logger.info(f"  Close approaches loaded: {stats['approaches_loaded']}")
    logger.info(f"  Parsing errors: {stats['parsing_errors']}")
    
    return database


def execute_inspect(database: NEODatabase, args: argparse.Namespace) -> None:
    """
    Execute the inspect command.
    
    Args:
        database: The NEO database
        args: Parsed arguments
    """
    # Find the NEO
    neo = None
    if args.pdes:
        neo = database.get_neo_by_designation(args.pdes)
    elif args.name:
        neo = database.get_neo_by_name(args.name)
    
    if not neo:
        print("No matching NEOs found in the database.", file=sys.stderr)
        return
    
    # Display NEO information
    print(neo)
    
    # Display close approaches if verbose
    if args.verbose:
        if neo.approaches:
            print(f"\nClose approaches ({len(neo.approaches)} total):")
            for approach in neo.approaches:
                print(f"  - {approach}")
        else:
            print("\nNo close approaches found for this NEO.")


def execute_query(database: NEODatabase, args: argparse.Namespace) -> None:
    """
    Execute the query command.
    
    Args:
        database: The NEO database
        args: Parsed arguments
    """
    # Create filters
    filters = FilterFactory.create_filters(
        date=args.date,
        start_date=args.start_date,
        end_date=args.end_date,
        distance_min=args.min_distance,
        distance_max=args.max_distance,
        velocity_min=args.min_velocity,
        velocity_max=args.max_velocity,
        diameter_min=args.min_diameter,
        diameter_max=args.max_diameter,
        hazardous=args.hazardous if args.hazardous or args.not_hazardous else None
    )
    
    # Query the database
    approaches = list(limit(database.query(filters.filters), args.limit))
    
    if not approaches:
        print("No close approaches match the specified criteria.")
        return
    
    # Handle output
    if args.outfile:
        # Save to file
        suffix = args.outfile.suffix.lower()
        if suffix == '.csv':
            OutputWriter.write_to_csv(approaches, args.outfile)
        elif suffix == '.json':
            OutputWriter.write_to_json(approaches, args.outfile)
        else:
            raise ValidationError(f"Unsupported output format: {suffix}")
        
        print(f"Results saved to {args.outfile}")
    else:
        # Display to console
        print(f"Found {len(approaches)} close approach(es):")
        for approach in approaches:
            print(f"  - {approach}")


def execute_interactive(database: NEODatabase, args: argparse.Namespace) -> None:
    """
    Execute the interactive command.
    
    Args:
        database: The NEO database
        args: Parsed arguments
    """
    shell = NEOShell(database, aggressive=args.aggressive)
    try:
        shell.cmdloop()
    except KeyboardInterrupt:
        print("\nExiting interactive mode.")


def main() -> int:
    """
    Main entry point for the CLI.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Validate arguments
        validate_args(args)
        
        # Load database
        database = load_database(args.neofile, args.cadfile, args.strict)
        
        # Execute command
        if args.command == 'inspect':
            execute_inspect(database, args)
        elif args.command == 'query':
            execute_query(database, args)
        elif args.command == 'interactive':
            execute_interactive(database, args)
        else:
            parser.print_help()
            return 1
        
        return 0
        
    except ValidationError as e:
        print(f"Validation error: {e}", file=sys.stderr)
        return 1
    except DataLoadError as e:
        print(f"Data loading error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        return 1
    except Exception as e:
        logger.exception("Unexpected error occurred")
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main()) 