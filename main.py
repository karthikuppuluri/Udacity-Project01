#!/usr/bin/env python3
"""
Main entry point for the NEO Explorer.

This script provides the command-line interface for exploring near-Earth
objects and their close approaches to Earth.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

from extract import load_neos, load_approaches
from database import NEODatabase
from filters import create_filters, limit
from write import write_to_csv, write_to_json


def inspect(database, designation=None, name=None, verbose=False):
    """
    Inspect an NEO by designation or name.

    Args:
        database: The NEODatabase to search
        designation: The primary designation of the NEO
        name: The IAU name of the NEO
        verbose: Whether to show all close approaches
    """
    neo = None

    if designation:
        neo = database.get_neo_by_designation(designation)
    elif name:
        neo = database.get_neo_by_name(name)

    if neo:
        print(neo)
        if verbose:
            for approach in neo.approaches:
                print(f"- {approach}")
    else:
        print("No matching NEOs exist in the database.")


def query(database, filters, limit_count=None, outfile=None):
    """
    Query close approaches with filters.

    Args:
        database: The NEODatabase to query
        filters: The filters to apply
        limit_count: Maximum number of results
        outfile: Output file path
    """
    # Apply filters and limit
    results = database.query(filters)
    if limit_count:
        results = limit(results, limit_count)

    # Convert to list for output
    results_list = list(results)

    if outfile:
        # Write to file
        if outfile.suffix.lower() == ".csv":
            write_to_csv(results_list, outfile)
        elif outfile.suffix.lower() == ".json":
            write_to_json(results_list, outfile)
        else:
            print(f"Unsupported file format: {outfile.suffix}")
            return
    else:
        # Print to stdout
        for approach in results_list:
            print(approach)


def interactive(database, aggressive=False):
    """
    Start an interactive session.

    Args:
        database: The NEODatabase to use
        aggressive: Whether to exit on file changes (unused parameter)
    """
    print("Explore close approaches of near-Earth objects. "
          "Type `help` or `?` to list commands and `exit` to exit.")

    while True:
        try:
            command = input("(neo) ").strip()

            if command in ["exit", "quit"]:
                break
            if command in ["help", "?"]:
                print("Available commands:")
                print("  inspect --pdes <designation>  Inspect NEO by "
                      "designation")
                print("  inspect --name <n>         Inspect NEO by name")
                print("  query [options]               Query close approaches")
                print("  exit                          Exit the session")
            elif command.startswith("inspect"):
                # Parse inspect command
                args = command.split()[1:]
                designation = None
                name = None
                verbose = False

                i = 0
                while i < len(args):
                    if args[i] == "--pdes" and i + 1 < len(args):
                        designation = args[i + 1]
                        i += 2
                    elif args[i] == "--name" and i + 1 < len(args):
                        name = args[i + 1]
                        i += 2
                    elif args[i] == "--verbose":
                        verbose = True
                        i += 1
                    else:
                        i += 1

                inspect(database, designation, name, verbose)
            elif command.startswith("query"):
                # Parse query command (simplified)
                print("Query command parsing not fully implemented "
                      "in this version.")
                print("Use the main script for full query functionality.")
            else:
                print(f"Unknown command: {command}")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            print("\nExiting...")
            break


def main():
    """Run the main entry point for the NEO Explorer program."""
    parser = argparse.ArgumentParser(
        description="Explore past and future close approaches of "
        "near-Earth objects.")

    # Global options
    parser.add_argument(
        "--neofile",
        type=Path,
        default=Path("data/neos.csv"),
        help="Path to CSV file of near-Earth objects",
    )
    parser.add_argument(
        "--cadfile",
        type=Path,
        default=Path("data/cad.json"),
        help="Path to JSON file of close approach data",
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command",
                                       help="Available commands")

    # Inspect command
    inspect_parser = subparsers.add_parser(
        "inspect", help="Inspect an NEO by designation or name")
    inspect_parser.add_argument(
        "--pdes", help="The primary designation of the NEO to inspect")
    inspect_parser.add_argument("--name",
                                help="The IAU name of the NEO to inspect")
    inspect_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Additionally, print all known close approaches of this NEO",
    )

    # Query command
    query_parser = subparsers.add_parser(
        "query",
        help="Query for close approaches that match specified criteria",
    )

    # Query filters
    query_parser.add_argument(
        "--date",
        "-d",
        help="Only return close approaches on the given date (YYYY-MM-DD)",
    )
    query_parser.add_argument(
        "--start-date",
        "-s",
        help="Only return close approaches on or after the given date",
    )
    query_parser.add_argument(
        "--end-date",
        "-e",
        help="Only return close approaches on or before the given date",
    )
    query_parser.add_argument(
        "--min-distance",
        type=float,
        help="Minimum approach distance in astronomical units",
    )
    query_parser.add_argument(
        "--max-distance",
        type=float,
        help="Maximum approach distance in astronomical units",
    )
    query_parser.add_argument(
        "--min-velocity",
        type=float,
        help="Minimum relative approach velocity in km/s",
    )
    query_parser.add_argument(
        "--max-velocity",
        type=float,
        help="Maximum relative approach velocity in km/s",
    )
    query_parser.add_argument("--min-diameter",
                              type=float,
                              help="Minimum NEO diameter in kilometers")
    query_parser.add_argument("--max-diameter",
                              type=float,
                              help="Maximum NEO diameter in kilometers")
    query_parser.add_argument(
        "--hazardous",
        action="store_true",
        help="Only return close approaches of potentially hazardous NEOs",
    )
    query_parser.add_argument(
        "--not-hazardous",
        action="store_true",
        help="Only return close approaches of non-hazardous NEOs",
    )

    # Query output options
    query_parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=10,
        help="Maximum number of results to return",
    )
    query_parser.add_argument("--outfile",
                              "-o",
                              type=Path,
                              help="File to save results")

    # Interactive command
    interactive_parser = subparsers.add_parser(
        "interactive", help="Start an interactive command session")
    interactive_parser.add_argument(
        "--aggressive",
        "-a",
        action="store_true",
        help="Kill the session when project files are modified",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Load database
    try:
        neos = load_neos(args.neofile)
        approaches = load_approaches(args.cadfile)
        database = NEODatabase(neos, approaches)
    except Exception as e:
        print(f"Error loading database: {e}")
        sys.exit(1)

    # Execute command
    if args.command == "inspect":
        if not args.pdes and not args.name:
            print("Error: Must specify either --pdes or --name")
            sys.exit(1)
        inspect(database, args.pdes, args.name, args.verbose)

    elif args.command == "query":
        # Parse dates
        filter_date = None
        start_date = None
        end_date = None

        if args.date:
            filter_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        if args.start_date:
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date()
        if args.end_date:
            end_date = datetime.strptime(args.end_date, "%Y-%m-%d").date()

        # Handle hazardous filter
        hazardous = None
        if args.hazardous:
            hazardous = True
        elif args.not_hazardous:
            hazardous = False

        # Create filters
        filters = create_filters(
            filter_date=filter_date,
            start_date=start_date,
            end_date=end_date,
            distance_min=args.min_distance,
            distance_max=args.max_distance,
            velocity_min=args.min_velocity,
            velocity_max=args.max_velocity,
            diameter_min=args.min_diameter,
            diameter_max=args.max_diameter,
            hazardous=hazardous,
        )

        query(database, filters, args.limit, args.outfile)

    elif args.command == "interactive":
        interactive(database, args.aggressive)


if __name__ == "__main__":
    main()
