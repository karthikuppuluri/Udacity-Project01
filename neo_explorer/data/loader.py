"""
Data loader for NEO Explorer.

This module provides data loading capabilities for NASA/JPL NEO data
with error handling, data validation, and performance optimizations.
"""

import csv
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import math

from ..core.models import NearEarthObject, CloseApproach
from ..core.database import NEODatabase
from .parsers import CSVParser, JSONParser


logger = logging.getLogger(__name__)


class DataLoadError(Exception):
    """Exception raised when data loading fails."""
    pass


class DataValidationError(Exception):
    """Exception raised when data validation fails."""
    pass


class DataLoader:
    """
    A robust data loader for NEO and close approach data.
    
    This class provides comprehensive data loading capabilities with:
    - Automatic format detection
    - Data validation and cleaning
    - Error recovery and reporting
    - Performance optimizations
    - Progress tracking
    """
    
    def __init__(self, validate_data: bool = True, strict_mode: bool = False):
        """
        Initialize the data loader.
        
        Args:
            validate_data: Whether to perform data validation
            strict_mode: Whether to fail on validation errors
        """
        self.validate_data = validate_data
        self.strict_mode = strict_mode
        self.csv_parser = CSVParser()
        self.json_parser = JSONParser()
        
        # Statistics
        self.stats = {
            'neos_loaded': 0,
            'approaches_loaded': 0,
            'validation_errors': 0,
            'parsing_errors': 0
        }
    
    def load_database(self, neo_file: Path, cad_file: Path) -> NEODatabase:
        """
        Load a complete NEO database from files.
        
        Args:
            neo_file: Path to the NEO CSV file
            cad_file: Path to the close approach JSON file
            
        Returns:
            A populated NEODatabase instance
            
        Raises:
            DataLoadError: If loading fails
        """
        logger.info(f"Loading NEO database from {neo_file} and {cad_file}")
        
        try:
            # Load NEOs
            neos = self.load_neos(neo_file)
            logger.info(f"Loaded {len(neos)} NEOs")
            
            # Load close approaches
            approaches = self.load_approaches(cad_file)
            logger.info(f"Loaded {len(approaches)} close approaches")
            
            # Create database
            database = NEODatabase(neos, approaches)
            
            logger.info("Database loading completed successfully")
            return database
            
        except Exception as e:
            logger.error(f"Failed to load database: {e}")
            raise DataLoadError(f"Database loading failed: {e}") from e
    
    def load_neos(self, file_path: Path) -> List[NearEarthObject]:
        """
        Load NEOs from a CSV file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of NearEarthObject instances
            
        Raises:
            DataLoadError: If loading fails
        """
        if not file_path.exists():
            raise DataLoadError(f"NEO file not found: {file_path}")
        
        logger.info(f"Loading NEOs from {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                neos = []
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    try:
                        neo = self._parse_neo_row(row)
                        if neo:
                            neos.append(neo)
                            self.stats['neos_loaded'] += 1
                    except Exception as e:
                        self.stats['parsing_errors'] += 1
                        if self.strict_mode:
                            raise DataValidationError(f"Error parsing NEO row {row_num}: {e}") from e
                        else:
                            logger.warning(f"Error parsing NEO row {row_num}: {e}")
                
                logger.info(f"Successfully loaded {len(neos)} NEOs")
                return neos
                
        except Exception as e:
            logger.error(f"Failed to load NEOs from {file_path}: {e}")
            raise DataLoadError(f"Failed to load NEOs: {e}") from e
    
    def load_approaches(self, file_path: Path) -> List[CloseApproach]:
        """
        Load close approaches from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            List of CloseApproach instances
            
        Raises:
            DataLoadError: If loading fails
        """
        if not file_path.exists():
            raise DataLoadError(f"Close approach file not found: {file_path}")
        
        logger.info(f"Loading close approaches from {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                if not isinstance(data, dict) or 'data' not in data:
                    raise DataValidationError("Invalid JSON structure: missing 'data' field")
                
                approaches = []
                approach_data = data['data']
                
                for row_num, row in enumerate(approach_data, start=1):
                    try:
                        approach = self._parse_approach_row(row)
                        if approach:
                            approaches.append(approach)
                            self.stats['approaches_loaded'] += 1
                    except Exception as e:
                        self.stats['parsing_errors'] += 1
                        if self.strict_mode:
                            raise DataValidationError(f"Error parsing approach row {row_num}: {e}") from e
                        else:
                            logger.warning(f"Error parsing approach row {row_num}: {e}")
                
                logger.info(f"Successfully loaded {len(approaches)} close approaches")
                return approaches
                
        except Exception as e:
            logger.error(f"Failed to load close approaches from {file_path}: {e}")
            raise DataLoadError(f"Failed to load close approaches: {e}") from e
    
    def _parse_neo_row(self, row: Dict[str, str]) -> Optional[NearEarthObject]:
        """
        Parse a single NEO row from CSV data.
        
        Args:
            row: Dictionary containing CSV row data
            
        Returns:
            NearEarthObject instance or None if invalid
        """
        try:
            # Extract and validate required fields
            designation = row.get('pdes', '').strip()
            if not designation:
                return None
            
            # Extract optional fields
            name = row.get('name', '').strip()
            if not name:
                name = None
            
            # Parse diameter
            diameter = None
            diameter_str = row.get('diameter', '').strip()
            if diameter_str:
                try:
                    diameter = float(diameter_str)
                    if diameter < 0 or math.isnan(diameter):
                        diameter = None
                except (ValueError, TypeError):
                    diameter = None
            
            # Parse hazardous flag
            hazardous = row.get('pha', 'N').strip().upper() == 'Y'
            
            # Create NEO object
            neo = NearEarthObject(
                designation=designation,
                name=name,
                diameter=diameter,
                hazardous=hazardous
            )
            
            if self.validate_data:
                self._validate_neo(neo)
            
            return neo
            
        except Exception as e:
            logger.debug(f"Error parsing NEO row: {e}")
            return None
    
    def _parse_approach_row(self, row: List[str]) -> Optional[CloseApproach]:
        """
        Parse a single close approach row from JSON data.
        
        Args:
            row: List containing JSON row data
            
        Returns:
            CloseApproach instance or None if invalid
        """
        try:
            if len(row) < 4:
                return None
            
            # Extract fields (assuming standard NASA format)
            designation = str(row[0]).strip()
            if not designation:
                return None
            
            # Parse datetime
            time_str = str(row[3]).strip()
            if not time_str:
                return None
            
            try:
                # Parse NASA format: "1900-Jan-01 00:11"
                time = datetime.strptime(time_str, "%Y-%b-%d %H:%M")
            except ValueError:
                logger.debug(f"Invalid time format: {time_str}")
                return None
            
            # Parse distance
            try:
                distance = float(row[4])
                if distance < 0 or math.isnan(distance):
                    return None
            except (ValueError, TypeError):
                return None
            
            # Parse velocity
            try:
                velocity = float(row[7])
                if velocity < 0 or math.isnan(velocity):
                    return None
            except (ValueError, TypeError):
                return None
            
            # Create close approach object
            approach = CloseApproach(
                designation=designation,
                time=time,
                distance=distance,
                velocity=velocity
            )
            
            if self.validate_data:
                self._validate_approach(approach)
            
            return approach
            
        except Exception as e:
            logger.debug(f"Error parsing approach row: {e}")
            return None
    
    def _validate_neo(self, neo: NearEarthObject) -> None:
        """Validate an NEO object."""
        if not neo.designation:
            raise DataValidationError("NEO must have a designation")
        
        if neo.diameter is not None and neo.diameter < 0:
            raise DataValidationError("NEO diameter cannot be negative")
    
    def _validate_approach(self, approach: CloseApproach) -> None:
        """Validate a close approach object."""
        if not approach.designation:
            raise DataValidationError("Close approach must have a designation")
        
        if approach.distance < 0:
            raise DataValidationError("Close approach distance cannot be negative")
        
        if approach.velocity < 0:
            raise DataValidationError("Close approach velocity cannot be negative")
    
    def get_statistics(self) -> Dict[str, int]:
        """Get loading statistics."""
        return self.stats.copy()
    
    def reset_statistics(self) -> None:
        """Reset loading statistics."""
        self.stats = {
            'neos_loaded': 0,
            'approaches_loaded': 0,
            'validation_errors': 0,
            'parsing_errors': 0
        } 