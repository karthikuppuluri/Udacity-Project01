"""
Data parsers for different file formats.

This module provides extensible parser classes for handling various data formats
used in the NEO Explorer application.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import csv
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ParserError(Exception):
    """Exception raised when parsing fails."""
    pass


class BaseParser(ABC):
    """Abstract base class for data parsers."""
    
    @abstractmethod
    def parse(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Parse a file and return structured data.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            List of dictionaries containing parsed data
            
        Raises:
            ParserError: If parsing fails
        """
        pass
    
    @abstractmethod
    def validate(self, data: Any) -> bool:
        """
        Validate parsed data.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass


class CSVParser(BaseParser):
    """Parser for CSV files."""
    
    def __init__(self, delimiter: str = ',', encoding: str = 'utf-8'):
        """
        Initialize CSV parser.
        
        Args:
            delimiter: CSV delimiter character
            encoding: File encoding
        """
        self.delimiter = delimiter
        self.encoding = encoding
    
    def parse(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Parse a CSV file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of dictionaries containing parsed data
            
        Raises:
            ParserError: If parsing fails
        """
        if not file_path.exists():
            raise ParserError(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding=self.encoding) as file:
                reader = csv.DictReader(file, delimiter=self.delimiter)
                data = []
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Clean the data
                        cleaned_row = self._clean_row(row)
                        if cleaned_row:
                            data.append(cleaned_row)
                    except Exception as e:
                        logger.warning(f"Error parsing CSV row {row_num}: {e}")
                
                return data
                
        except Exception as e:
            raise ParserError(f"Failed to parse CSV file {file_path}: {e}") from e
    
    def _clean_row(self, row: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Clean and validate a CSV row.
        
        Args:
            row: Raw CSV row data
            
        Returns:
            Cleaned row data or None if invalid
        """
        cleaned = {}
        
        for key, value in row.items():
            if value is not None:
                cleaned[key] = value.strip()
            else:
                cleaned[key] = ""
        
        return cleaned
    
    def validate(self, data: List[Dict[str, Any]]) -> bool:
        """
        Validate parsed CSV data.
        
        Args:
            data: Parsed CSV data
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(data, list):
            return False
        
        if not data:
            return True
        
        # Check that all rows have the same keys
        first_keys = set(data[0].keys())
        for row in data[1:]:
            if set(row.keys()) != first_keys:
                return False
        
        return True


class JSONParser(BaseParser):
    """Parser for JSON files."""
    
    def __init__(self, encoding: str = 'utf-8'):
        """
        Initialize JSON parser.
        
        Args:
            encoding: File encoding
        """
        self.encoding = encoding
    
    def parse(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Parse a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            List of dictionaries containing parsed data
            
        Raises:
            ParserError: If parsing fails
        """
        if not file_path.exists():
            raise ParserError(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding=self.encoding) as file:
                data = json.load(file)
                
                if not self.validate(data):
                    raise ParserError("Invalid JSON structure")
                
                # Extract the data array
                if isinstance(data, dict) and 'data' in data:
                    return data['data']
                elif isinstance(data, list):
                    return data
                else:
                    raise ParserError("Unexpected JSON structure")
                
        except json.JSONDecodeError as e:
            raise ParserError(f"Invalid JSON in file {file_path}: {e}") from e
        except Exception as e:
            raise ParserError(f"Failed to parse JSON file {file_path}: {e}") from e
    
    def validate(self, data: Any) -> bool:
        """
        Validate parsed JSON data.
        
        Args:
            data: Parsed JSON data
            
        Returns:
            True if valid, False otherwise
        """
        # Check for expected NASA/JPL format
        if isinstance(data, dict):
            # Should have signature, count, fields, and data
            required_keys = {'signature', 'count', 'fields', 'data'}
            if not required_keys.issubset(data.keys()):
                return False
            
            # Data should be a list
            if not isinstance(data['data'], list):
                return False
            
            return True
        
        elif isinstance(data, list):
            # Direct array format
            return True
        
        return False


class ParserFactory:
    """Factory for creating parsers based on file type."""
    
    _parsers = {
        '.csv': CSVParser,
        '.json': JSONParser,
    }
    
    @classmethod
    def create_parser(cls, file_path: Path) -> BaseParser:
        """
        Create a parser for the given file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Appropriate parser instance
            
        Raises:
            ParserError: If no parser is available for the file type
        """
        suffix = file_path.suffix.lower()
        
        if suffix not in cls._parsers:
            raise ParserError(f"No parser available for file type: {suffix}")
        
        parser_class = cls._parsers[suffix]
        return parser_class()
    
    @classmethod
    def register_parser(cls, extension: str, parser_class: type) -> None:
        """
        Register a new parser for a file extension.
        
        Args:
            extension: File extension (e.g., '.txt')
            parser_class: Parser class to register
        """
        if not issubclass(parser_class, BaseParser):
            raise ValueError("Parser class must inherit from BaseParser")
        
        cls._parsers[extension.lower()] = parser_class
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """Get list of supported file extensions."""
        return list(cls._parsers.keys()) 