"""
Data formatting utilities for NEO Explorer.

This module provides utilities for formatting and displaying data in various
formats including CSV, JSON, and human-readable text.
"""

import csv
import json
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import logging

from ..core.models import NearEarthObject, CloseApproach

logger = logging.getLogger(__name__)


class FormatError(Exception):
    """Exception raised when formatting operations fail."""
    pass


class DataFormatter:
    """Utility class for formatting data in various output formats."""
    
    @staticmethod
    def format_neo(neo: NearEarthObject, format_type: str = "text") -> str:
        """
        Format an NEO object for display.
        
        Args:
            neo: The NEO object to format
            format_type: The format type ('text', 'json', 'csv')
            
        Returns:
            Formatted string representation
        """
        if format_type == "text":
            return str(neo)
        elif format_type == "json":
            return json.dumps(neo.serialize(), indent=2)
        elif format_type == "csv":
            data = neo.serialize()
            return ",".join(str(v) for v in data.values())
        else:
            raise FormatError(f"Unsupported format type: {format_type}")
    
    @staticmethod
    def format_approach(approach: CloseApproach, format_type: str = "text") -> str:
        """
        Format a close approach object for display.
        
        Args:
            approach: The close approach object to format
            format_type: The format type ('text', 'json', 'csv')
            
        Returns:
            Formatted string representation
        """
        if format_type == "text":
            return str(approach)
        elif format_type == "json":
            return json.dumps(approach.serialize(), indent=2)
        elif format_type == "csv":
            data = approach.serialize()
            return ",".join(str(v) for v in data.values())
        else:
            raise FormatError(f"Unsupported format type: {format_type}")
    
    @staticmethod
    def format_approaches_list(
        approaches: List[CloseApproach],
        format_type: str = "text",
        include_header: bool = True
    ) -> str:
        """
        Format a list of close approaches.
        
        Args:
            approaches: List of close approach objects
            format_type: The format type ('text', 'json', 'csv')
            include_header: Whether to include headers (for CSV)
            
        Returns:
            Formatted string representation
        """
        if not approaches:
            return "No close approaches found."
        
        if format_type == "text":
            return "\n".join(str(approach) for approach in approaches)
        
        elif format_type == "json":
            data = [approach.serialize() for approach in approaches]
            return json.dumps(data, indent=2)
        
        elif format_type == "csv":
            if not approaches:
                return ""
            
            # Get headers from first approach
            headers = list(approaches[0].serialize().keys())
            
            output = []
            if include_header:
                output.append(",".join(headers))
            
            for approach in approaches:
                data = approach.serialize()
                row = [str(data.get(header, "")) for header in headers]
                output.append(",".join(row))
            
            return "\n".join(output)
        
        else:
            raise FormatError(f"Unsupported format type: {format_type}")
    
    @staticmethod
    def format_statistics(stats: Dict[str, Any]) -> str:
        """
        Format database statistics for display.
        
        Args:
            stats: Dictionary of statistics
            
        Returns:
            Formatted statistics string
        """
        lines = ["Database Statistics:"]
        for key, value in stats.items():
            # Convert key to readable format
            readable_key = key.replace('_', ' ').title()
            lines.append(f"  {readable_key}: {value}")
        
        return "\n".join(lines)


class OutputWriter:
    """Utility class for writing formatted data to files."""
    
    @staticmethod
    def write_to_csv(
        approaches: List[CloseApproach],
        file_path: Path,
        include_header: bool = True
    ) -> None:
        """
        Write close approaches to a CSV file.
        
        Args:
            approaches: List of close approach objects
            file_path: Path to the output file
            include_header: Whether to include headers
            
        Raises:
            FormatError: If writing fails
        """
        if not approaches:
            logger.warning("No approaches to write to CSV")
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                # Get headers from first approach
                headers = list(approaches[0].serialize().keys())
                
                writer = csv.DictWriter(file, fieldnames=headers)
                
                if include_header:
                    writer.writeheader()
                
                for approach in approaches:
                    writer.writerow(approach.serialize())
            
            logger.info(f"Successfully wrote {len(approaches)} approaches to {file_path}")
            
        except Exception as e:
            raise FormatError(f"Failed to write CSV file {file_path}: {e}") from e
    
    @staticmethod
    def write_to_json(
        approaches: List[CloseApproach],
        file_path: Path,
        pretty: bool = True
    ) -> None:
        """
        Write close approaches to a JSON file.
        
        Args:
            approaches: List of close approach objects
            file_path: Path to the output file
            pretty: Whether to format JSON with indentation
            
        Raises:
            FormatError: If writing fails
        """
        try:
            data = [approach.serialize() for approach in approaches]
            
            with open(file_path, 'w', encoding='utf-8') as file:
                if pretty:
                    json.dump(data, file, indent=2, ensure_ascii=False)
                else:
                    json.dump(data, file, ensure_ascii=False)
            
            logger.info(f"Successfully wrote {len(approaches)} approaches to {file_path}")
            
        except Exception as e:
            raise FormatError(f"Failed to write JSON file {file_path}: {e}") from e
    
    @staticmethod
    def write_to_text(
        approaches: List[CloseApproach],
        file_path: Path
    ) -> None:
        """
        Write close approaches to a text file.
        
        Args:
            approaches: List of close approach objects
            file_path: Path to the output file
            
        Raises:
            FormatError: If writing fails
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                for approach in approaches:
                    file.write(str(approach) + "\n")
            
            logger.info(f"Successfully wrote {len(approaches)} approaches to {file_path}")
            
        except Exception as e:
            raise FormatError(f"Failed to write text file {file_path}: {e}") from e


def write_to_csv(approaches: List[CloseApproach], file_path: Path) -> None:
    """Legacy function for backward compatibility."""
    OutputWriter.write_to_csv(approaches, file_path)


def write_to_json(approaches: List[CloseApproach], file_path: Path) -> None:
    """Legacy function for backward compatibility."""
    OutputWriter.write_to_json(approaches, file_path) 