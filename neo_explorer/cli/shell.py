"""
Interactive shell for NEO Explorer.

This module provides an interactive command shell for exploring NEO data
with enhanced command parsing and user experience.
"""

import cmd
import shlex
import sys
import logging
from typing import Optional, List
from pathlib import Path

from ..core.database import NEODatabase
from ..utils.filters import FilterFactory, limit
from ..utils.formatters import OutputWriter
from ..utils.validators import InputValidator, ValidationError

logger = logging.getLogger(__name__)


class NEOShell(cmd.Cmd):
    """
    Interactive shell for exploring NEO data.
    
    This shell provides commands for inspecting NEOs and querying close approaches
    with a user-friendly interface and comprehensive error handling.
    """
    
    intro = (
        "Welcome to NEO Explorer Interactive Shell!\n"
        "Type 'help' or '?' to list commands and 'exit' to quit.\n"
        "Use 'help <command>' for detailed information about each command.\n"
    )
    prompt = '(neo) '
    
    def __init__(self, database: NEODatabase, aggressive: bool = False):
        """
        Initialize the NEO shell.
        
        Args:
            database: The NEO database to use
            aggressive: Whether to kill the session when files are modified
        """
        super().__init__()
        self.database = database
        self.aggressive = aggressive
        
        # Display database statistics
        stats = database.get_statistics()
        print(f"Database loaded: {stats['total_neos']} NEOs, {stats['total_approaches']} close approaches")
    
    def do_inspect(self, arg: str) -> Optional[bool]:
        """
        Inspect an NEO by designation or name.
        
        Usage:
            inspect --pdes <designation>
            inspect --name <name>
            inspect --pdes <designation> --verbose
            inspect --name <name> --verbose
        
        Examples:
            inspect --pdes 433
            inspect --name Eros --verbose
        """
        try:
            args = self._parse_inspect_args(arg)
            self._execute_inspect(args)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
    
    def do_i(self, arg: str) -> Optional[bool]:
        """Shorthand for inspect command."""
        return self.do_inspect(arg)
    
    def do_query(self, arg: str) -> Optional[bool]:
        """
        Query for close approaches matching specified criteria.
        
        Usage:
            query [options]
        
        Filter Options:
            --date YYYY-MM-DD              Exact date
            --start-date YYYY-MM-DD        Start date (inclusive)
            --end-date YYYY-MM-DD          End date (inclusive)
            --min-distance <value>         Minimum distance (au)
            --max-distance <value>         Maximum distance (au)
            --min-velocity <value>         Minimum velocity (km/s)
            --max-velocity <value>         Maximum velocity (km/s)
            --min-diameter <value>         Minimum diameter (km)
            --max-diameter <value>         Maximum diameter (km)
            --hazardous                    Only hazardous NEOs
            --not-hazardous                Only non-hazardous NEOs
        
        Output Options:
            --limit <number>               Maximum results (default: 10)
            --outfile <file>               Save to file (CSV/JSON)
            --format <text|csv|json>       Output format
        
        Examples:
            query --date 2020-01-01
            query --start-date 2020-01-01 --end-date 2020-01-31 --max-distance 0.025
            query --hazardous --max-distance 0.05 --min-velocity 30
            query --limit 5 --outfile results.csv
        """
        try:
            args = self._parse_query_args(arg)
            self._execute_query(args)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
    
    def do_q(self, arg: str) -> Optional[bool]:
        """Shorthand for query command."""
        return self.do_query(arg)
    
    def do_stats(self, arg: str) -> Optional[bool]:
        """
        Display database statistics.
        
        Usage:
            stats
        """
        stats = self.database.get_statistics()
        print("Database Statistics:")
        for key, value in stats.items():
            readable_key = key.replace('_', ' ').title()
            print(f"  {readable_key}: {value}")
    
    def do_search(self, arg: str) -> Optional[bool]:
        """
        Search for NEOs by designation or name.
        
        Usage:
            search <query> [--limit <number>]
        
        Examples:
            search Eros
            search 433
            search 2020 --limit 5
        """
        try:
            args = self._parse_search_args(arg)
            self._execute_search(args)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
    
    def do_closest(self, arg: str) -> Optional[bool]:
        """
        Show the closest approaches to Earth.
        
        Usage:
            closest [--limit <number>]
        
        Examples:
            closest
            closest --limit 5
        """
        try:
            args = self._parse_limit_args(arg)
            limit_count = args.get('limit', 10)
            approaches = self.database.get_closest_approaches(limit_count)
            
            print(f"Closest {len(approaches)} approach(es) to Earth:")
            for approach in approaches:
                print(f"  - {approach}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
    
    def do_fastest(self, arg: str) -> Optional[bool]:
        """
        Show the fastest approaches to Earth.
        
        Usage:
            fastest [--limit <number>]
        
        Examples:
            fastest
            fastest --limit 5
        """
        try:
            args = self._parse_limit_args(arg)
            limit_count = args.get('limit', 10)
            approaches = self.database.get_fastest_approaches(limit_count)
            
            print(f"Fastest {len(approaches)} approach(es) to Earth:")
            for approach in approaches:
                print(f"  - {approach}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
    
    def do_recent(self, arg: str) -> Optional[bool]:
        """
        Show the most recent close approaches.
        
        Usage:
            recent [--limit <number>]
        
        Examples:
            recent
            recent --limit 5
        """
        try:
            args = self._parse_limit_args(arg)
            limit_count = args.get('limit', 10)
            approaches = self.database.get_recent_approaches(limit_count)
            
            print(f"Most recent {len(approaches)} approach(es):")
            for approach in approaches:
                print(f"  - {approach}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
    
    def do_exit(self, arg: str) -> bool:
        """Exit the interactive shell."""
        print("Goodbye!")
        return True
    
    def do_quit(self, arg: str) -> bool:
        """Exit the interactive shell."""
        return self.do_exit(arg)
    
    def do_EOF(self, arg: str) -> bool:
        """Exit the interactive shell on EOF."""
        print()
        return self.do_exit(arg)
    
    def _parse_inspect_args(self, arg: str) -> dict:
        """Parse inspect command arguments."""
        if not arg.strip():
            raise ValidationError("Either --pdes or --name must be specified")
        
        try:
            args = shlex.split(arg)
        except ValueError as e:
            raise ValidationError(f"Invalid argument format: {e}")
        
        result = {}
        i = 0
        while i < len(args):
            if args[i] in ['--pdes', '-p']:
                if i + 1 >= len(args):
                    raise ValidationError("--pdes requires a designation")
                result['pdes'] = args[i + 1]
                i += 2
            elif args[i] in ['--name', '-n']:
                if i + 1 >= len(args):
                    raise ValidationError("--name requires a name")
                result['name'] = args[i + 1]
                i += 2
            elif args[i] in ['--verbose', '-v']:
                result['verbose'] = True
                i += 1
            else:
                raise ValidationError(f"Unknown argument: {args[i]}")
        
        if not result.get('pdes') and not result.get('name'):
            raise ValidationError("Either --pdes or --name must be specified")
        
        return result
    
    def _parse_query_args(self, arg: str) -> dict:
        """Parse query command arguments."""
        try:
            args = shlex.split(arg)
        except ValueError as e:
            raise ValidationError(f"Invalid argument format: {e}")
        
        result = {}
        i = 0
        while i < len(args):
            if args[i] in ['--date', '-d']:
                if i + 1 >= len(args):
                    raise ValidationError("--date requires a date")
                result['date'] = args[i + 1]
                i += 2
            elif args[i] in ['--start-date', '-s']:
                if i + 1 >= len(args):
                    raise ValidationError("--start-date requires a date")
                result['start_date'] = args[i + 1]
                i += 2
            elif args[i] in ['--end-date', '-e']:
                if i + 1 >= len(args):
                    raise ValidationError("--end-date requires a date")
                result['end_date'] = args[i + 1]
                i += 2
            elif args[i] == '--min-distance':
                if i + 1 >= len(args):
                    raise ValidationError("--min-distance requires a value")
                result['distance_min'] = float(args[i + 1])
                i += 2
            elif args[i] == '--max-distance':
                if i + 1 >= len(args):
                    raise ValidationError("--max-distance requires a value")
                result['distance_max'] = float(args[i + 1])
                i += 2
            elif args[i] == '--min-velocity':
                if i + 1 >= len(args):
                    raise ValidationError("--min-velocity requires a value")
                result['velocity_min'] = float(args[i + 1])
                i += 2
            elif args[i] == '--max-velocity':
                if i + 1 >= len(args):
                    raise ValidationError("--max-velocity requires a value")
                result['velocity_max'] = float(args[i + 1])
                i += 2
            elif args[i] == '--min-diameter':
                if i + 1 >= len(args):
                    raise ValidationError("--min-diameter requires a value")
                result['diameter_min'] = float(args[i + 1])
                i += 2
            elif args[i] == '--max-diameter':
                if i + 1 >= len(args):
                    raise ValidationError("--max-diameter requires a value")
                result['diameter_max'] = float(args[i + 1])
                i += 2
            elif args[i] == '--hazardous':
                result['hazardous'] = True
                i += 1
            elif args[i] == '--not-hazardous':
                result['hazardous'] = False
                i += 1
            elif args[i] in ['--limit', '-l']:
                if i + 1 >= len(args):
                    raise ValidationError("--limit requires a number")
                result['limit'] = int(args[i + 1])
                i += 2
            elif args[i] in ['--outfile', '-o']:
                if i + 1 >= len(args):
                    raise ValidationError("--outfile requires a filename")
                result['outfile'] = Path(args[i + 1])
                i += 2
            elif args[i] == '--format':
                if i + 1 >= len(args):
                    raise ValidationError("--format requires a format type")
                result['format'] = args[i + 1]
                i += 2
            else:
                raise ValidationError(f"Unknown argument: {args[i]}")
        
        return result
    
    def _parse_search_args(self, arg: str) -> dict:
        """Parse search command arguments."""
        try:
            args = shlex.split(arg)
        except ValueError as e:
            raise ValidationError(f"Invalid argument format: {e}")
        
        if not args:
            raise ValidationError("Search query is required")
        
        result = {'query': args[0]}
        
        i = 1
        while i < len(args):
            if args[i] == '--limit':
                if i + 1 >= len(args):
                    raise ValidationError("--limit requires a number")
                result['limit'] = int(args[i + 1])
                i += 2
            else:
                raise ValidationError(f"Unknown argument: {args[i]}")
        
        return result
    
    def _parse_limit_args(self, arg: str) -> dict:
        """Parse limit-only arguments."""
        try:
            args = shlex.split(arg)
        except ValueError as e:
            raise ValidationError(f"Invalid argument format: {e}")
        
        result = {}
        i = 0
        while i < len(args):
            if args[i] == '--limit':
                if i + 1 >= len(args):
                    raise ValidationError("--limit requires a number")
                result['limit'] = int(args[i + 1])
                i += 2
            else:
                raise ValidationError(f"Unknown argument: {args[i]}")
        
        return result
    
    def _execute_inspect(self, args: dict) -> None:
        """Execute the inspect command."""
        neo = None
        if args.get('pdes'):
            neo = self.database.get_neo_by_designation(args['pdes'])
        elif args.get('name'):
            neo = self.database.get_neo_by_name(args['name'])
        
        if not neo:
            print("No matching NEOs found in the database.")
            return
        
        print(neo)
        
        if args.get('verbose'):
            if neo.approaches:
                print(f"\nClose approaches ({len(neo.approaches)} total):")
                for approach in neo.approaches:
                    print(f"  - {approach}")
            else:
                print("\nNo close approaches found for this NEO.")
    
    def _execute_query(self, args: dict) -> None:
        """Execute the query command."""
        # Create filters
        filters = FilterFactory.create_filters(
            date=args.get('date'),
            start_date=args.get('start_date'),
            end_date=args.get('end_date'),
            distance_min=args.get('distance_min'),
            distance_max=args.get('distance_max'),
            velocity_min=args.get('velocity_min'),
            velocity_max=args.get('velocity_max'),
            diameter_min=args.get('diameter_min'),
            diameter_max=args.get('diameter_max'),
            hazardous=args.get('hazardous')
        )
        
        # Query the database
        limit_count = args.get('limit', 10)
        approaches = list(limit(self.database.query(filters.filters), limit_count))
        
        if not approaches:
            print("No close approaches match the specified criteria.")
            return
        
        # Handle output
        if args.get('outfile'):
            outfile = args['outfile']
            suffix = outfile.suffix.lower()
            if suffix == '.csv':
                OutputWriter.write_to_csv(approaches, outfile)
            elif suffix == '.json':
                OutputWriter.write_to_json(approaches, outfile)
            else:
                raise ValidationError(f"Unsupported output format: {suffix}")
            
            print(f"Results saved to {outfile}")
        else:
            print(f"Found {len(approaches)} close approach(es):")
            for approach in approaches:
                print(f"  - {approach}")
    
    def _execute_search(self, args: dict) -> None:
        """Execute the search command."""
        query = args['query']
        limit_count = args.get('limit', 10)
        
        results = self.database.search_neos(query, limit_count)
        
        if not results:
            print(f"No NEOs found matching '{query}'.")
            return
        
        print(f"Found {len(results)} NEO(s) matching '{query}':")
        for neo in results:
            print(f"  - {neo}")
    
    def emptyline(self) -> bool:
        """Do nothing on empty line."""
        return False
    
    def default(self, line: str) -> bool:
        """Handle unknown commands."""
        print(f"Unknown command: {line}")
        print("Type 'help' for a list of available commands.")
        return False 