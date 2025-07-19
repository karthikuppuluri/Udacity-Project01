"""
Data validation utilities for NEO Explorer.

This module provides utilities for validating data integrity and user input
throughout the application.
"""

from typing import Any, Optional, Union
from datetime import datetime, date
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Exception raised when validation fails."""
    pass


class DataValidator:
    """Utility class for validating data and user input."""
    
    @staticmethod
    def validate_date_string(date_string: str) -> date:
        """
        Validate and parse a date string in YYYY-MM-DD format.
        
        Args:
            date_string: Date string to validate
            
        Returns:
            Parsed date object
            
        Raises:
            ValidationError: If the date string is invalid
        """
        try:
            return datetime.strptime(date_string, '%Y-%m-%d').date()
        except ValueError:
            raise ValidationError(f"'{date_string}' is not a valid date. Use YYYY-MM-DD format.")
    
    @staticmethod
    def validate_float(value: Any, min_value: Optional[float] = None, 
                      max_value: Optional[float] = None, name: str = "value") -> float:
        """
        Validate a float value with optional range constraints.
        
        Args:
            value: Value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            name: Name of the value for error messages
            
        Returns:
            Validated float value
            
        Raises:
            ValidationError: If the value is invalid
        """
        try:
            float_value = float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"'{value}' is not a valid number for {name}")
        
        if min_value is not None and float_value < min_value:
            raise ValidationError(f"{name} must be at least {min_value}")
        
        if max_value is not None and float_value > max_value:
            raise ValidationError(f"{name} must be at most {max_value}")
        
        return float_value
    
    @staticmethod
    def validate_integer(value: Any, min_value: Optional[int] = None,
                        max_value: Optional[int] = None, name: str = "value") -> int:
        """
        Validate an integer value with optional range constraints.
        
        Args:
            value: Value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            name: Name of the value for error messages
            
        Returns:
            Validated integer value
            
        Raises:
            ValidationError: If the value is invalid
        """
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"'{value}' is not a valid integer for {name}")
        
        if min_value is not None and int_value < min_value:
            raise ValidationError(f"{name} must be at least {min_value}")
        
        if max_value is not None and int_value > max_value:
            raise ValidationError(f"{name} must be at most {max_value}")
        
        return int_value
    
    @staticmethod
    def validate_file_path(file_path: Union[str, Path], must_exist: bool = True) -> Path:
        """
        Validate a file path.
        
        Args:
            file_path: Path to validate
            must_exist: Whether the file must exist
            
        Returns:
            Validated Path object
            
        Raises:
            ValidationError: If the path is invalid
        """
        try:
            path = Path(file_path)
        except Exception as e:
            raise ValidationError(f"Invalid file path '{file_path}': {e}")
        
        if must_exist and not path.exists():
            raise ValidationError(f"File does not exist: {path}")
        
        return path
    
    @staticmethod
    def validate_string(value: Any, min_length: int = 0, max_length: Optional[int] = None,
                       name: str = "string") -> str:
        """
        Validate a string value.
        
        Args:
            value: Value to validate
            min_length: Minimum allowed length
            max_length: Maximum allowed length
            name: Name of the value for error messages
            
        Returns:
            Validated string value
            
        Raises:
            ValidationError: If the value is invalid
        """
        if not isinstance(value, str):
            raise ValidationError(f"'{value}' is not a valid string for {name}")
        
        if len(value) < min_length:
            raise ValidationError(f"{name} must be at least {min_length} characters long")
        
        if max_length is not None and len(value) > max_length:
            raise ValidationError(f"{name} must be at most {max_length} characters long")
        
        return value.strip()
    
    @staticmethod
    def validate_choice(value: Any, choices: list, name: str = "choice") -> Any:
        """
        Validate that a value is one of the allowed choices.
        
        Args:
            value: Value to validate
            choices: List of allowed choices
            name: Name of the value for error messages
            
        Returns:
            Validated value
            
        Raises:
            ValidationError: If the value is not in the allowed choices
        """
        if value not in choices:
            choices_str = ", ".join(str(c) for c in choices)
            raise ValidationError(f"{name} must be one of: {choices_str}")
        
        return value


class InputValidator:
    """Utility class for validating user input from command line arguments."""
    
    @staticmethod
    def validate_query_args(args: dict) -> dict:
        """
        Validate query command arguments.
        
        Args:
            args: Dictionary of arguments to validate
            
        Returns:
            Validated arguments dictionary
            
        Raises:
            ValidationError: If any arguments are invalid
        """
        validated = {}
        
        # Validate dates
        for date_field in ['date', 'start_date', 'end_date']:
            if args.get(date_field):
                validated[date_field] = DataValidator.validate_date_string(args[date_field])
        
        # Validate numeric fields
        numeric_fields = [
            ('distance_min', 0.0, None),
            ('distance_max', 0.0, None),
            ('velocity_min', 0.0, None),
            ('velocity_max', 0.0, None),
            ('diameter_min', 0.0, None),
            ('diameter_max', 0.0, None),
            ('limit', 1, 10000)
        ]
        
        for field, min_val, max_val in numeric_fields:
            if args.get(field) is not None:
                if field == 'limit':
                    validated[field] = DataValidator.validate_integer(
                        args[field], min_val, max_val, field
                    )
                else:
                    validated[field] = DataValidator.validate_float(
                        args[field], min_val, max_val, field
                    )
        
        # Validate boolean fields
        if 'hazardous' in args:
            validated['hazardous'] = bool(args['hazardous'])
        
        # Validate file paths
        if args.get('outfile'):
            validated['outfile'] = DataValidator.validate_file_path(
                args['outfile'], must_exist=False
            )
        
        return validated
    
    @staticmethod
    def validate_inspect_args(args: dict) -> dict:
        """
        Validate inspect command arguments.
        
        Args:
            args: Dictionary of arguments to validate
            
        Returns:
            Validated arguments dictionary
            
        Raises:
            ValidationError: If any arguments are invalid
        """
        validated = {}
        
        # Validate designation or name
        if args.get('pdes'):
            validated['pdes'] = DataValidator.validate_string(
                args['pdes'], min_length=1, name="designation"
            )
        elif args.get('name'):
            validated['name'] = DataValidator.validate_string(
                args['name'], min_length=1, name="name"
            )
        else:
            raise ValidationError("Either designation or name must be provided")
        
        # Validate verbose flag
        if 'verbose' in args:
            validated['verbose'] = bool(args['verbose'])
        
        return validated 