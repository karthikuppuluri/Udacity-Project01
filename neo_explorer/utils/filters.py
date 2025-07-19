"""
Filter system for querying close approaches.

This module provides a flexible and efficient filtering system for querying
close approaches based on various criteria.
"""

import operator
from typing import Dict, Any, Callable, Optional, Union
from datetime import date, datetime
import logging
from abc import ABC, abstractmethod

from ..core.models import CloseApproach
from ..utils.validators import DataValidator

logger = logging.getLogger(__name__)


class FilterError(Exception):
    """Exception raised when filter operations fail."""
    pass


class AttributeFilter(ABC):
    """
    Abstract base class for filters on comparable attributes.
    
    An AttributeFilter represents search criteria comparing some attribute
    of a close approach (or its attached NEO) to a reference value.
    """
    
    def __init__(self, op: Callable, value: Any):
        """
        Initialize the filter with an operator and reference value.
        
        Args:
            op: A 2-argument predicate comparator (such as operator.le)
            value: The reference value to compare against
        """
        self.op = op
        self.value = value
    
    def __call__(self, approach: CloseApproach) -> bool:
        """
        Apply the filter to a close approach.
        
        Args:
            approach: The close approach to filter
            
        Returns:
            True if the approach matches the filter criteria
        """
        # Accept string or date for self.value
        value = self.value
        if isinstance(value, str):
            try:
                value = DataValidator.validate_date_string(value)
            except Exception as e:
                logger.warning(f"DateFilter: Could not parse date string '{self.value}': {e}")
                return False
        try:
            return self.op(self.get(approach), value)
        except Exception as e:
            logger.warning(f"Filter evaluation failed: {e}")
            return False
    
    @abstractmethod
    def get(self, approach: CloseApproach) -> Any:
        """
        Get the attribute value from a close approach.
        
        Args:
            approach: The close approach to extract the attribute from
            
        Returns:
            The attribute value to compare against
        """
        pass
    
    def __repr__(self) -> str:
        """Return a string representation of the filter."""
        return f"{self.__class__.__name__}(op={self.op.__name__}, value={self.value})"


class DateFilter(AttributeFilter):
    """Filter for close approach dates."""
    
    def get(self, approach: CloseApproach) -> date:
        """Get the date of the close approach."""
        return approach.date


class DistanceFilter(AttributeFilter):
    """Filter for close approach distances."""
    
    def get(self, approach: CloseApproach) -> float:
        """Get the distance of the close approach."""
        return approach.distance


class VelocityFilter(AttributeFilter):
    """Filter for close approach velocities."""
    
    def get(self, approach: CloseApproach) -> float:
        """Get the velocity of the close approach."""
        return approach.velocity


class DiameterFilter(AttributeFilter):
    """Filter for NEO diameters."""
    
    def get(self, approach: CloseApproach) -> Optional[float]:
        """Get the diameter of the NEO."""
        if approach.neo and approach.neo.has_diameter:
            return approach.neo.diameter
        return None


class HazardousFilter(AttributeFilter):
    """Filter for NEO hazardous status."""
    
    def get(self, approach: CloseApproach) -> bool:
        """Get the hazardous status of the NEO."""
        return approach.neo.hazardous if approach.neo else False


class CompositeFilter:
    """A filter that combines multiple filters with AND logic."""
    
    def __init__(self, filters: Dict[str, AttributeFilter]):
        """
        Initialize the composite filter.
        
        Args:
            filters: Dictionary of filters to combine
        """
        self.filters = filters
    
    def __call__(self, approach: CloseApproach) -> bool:
        """
        Apply all filters to a close approach.
        
        Args:
            approach: The close approach to filter
            
        Returns:
            True if the approach matches all filter criteria
        """
        return all(filter_func(approach) for filter_func in self.filters.values())
    
    def __repr__(self) -> str:
        """Return a string representation of the composite filter."""
        return f"CompositeFilter({list(self.filters.keys())})"


class FilterFactory:
    """Factory for creating filters from user criteria."""
    
    @staticmethod
    def create_filters(
        date: Optional[date] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        distance_min: Optional[float] = None,
        distance_max: Optional[float] = None,
        velocity_min: Optional[float] = None,
        velocity_max: Optional[float] = None,
        diameter_min: Optional[float] = None,
        diameter_max: Optional[float] = None,
        hazardous: Optional[bool] = None
    ) -> CompositeFilter:
        """
        Create a collection of filters from user-specified criteria.
        
        Args:
            date: Exact date for close approaches
            start_date: Start date for date range
            end_date: End date for date range
            distance_min: Minimum approach distance
            distance_max: Maximum approach distance
            velocity_min: Minimum approach velocity
            velocity_max: Maximum approach velocity
            diameter_min: Minimum NEO diameter
            diameter_max: Maximum NEO diameter
            hazardous: NEO hazardous status
            
        Returns:
            A CompositeFilter containing all specified filters
        """
        filters = {}
        
        # Date filters
        if date:
            filters["date"] = DateFilter(operator.eq, date)
        if start_date:
            filters["start_date"] = DateFilter(operator.ge, start_date)
        if end_date:
            filters["end_date"] = DateFilter(operator.le, end_date)
        
        # Distance filters
        if distance_min is not None:
            filters["distance_min"] = DistanceFilter(operator.ge, distance_min)
        if distance_max is not None:
            filters["distance_max"] = DistanceFilter(operator.le, distance_max)
        
        # Velocity filters
        if velocity_min is not None:
            filters["velocity_min"] = VelocityFilter(operator.ge, velocity_min)
        if velocity_max is not None:
            filters["velocity_max"] = VelocityFilter(operator.le, velocity_max)
        
        # Diameter filters
        if diameter_min is not None:
            filters["diameter_min"] = DiameterFilter(operator.ge, diameter_min)
        if diameter_max is not None:
            filters["diameter_max"] = DiameterFilter(operator.le, diameter_max)
        
        # Hazardous filter
        if hazardous is not None:
            filters["hazardous"] = HazardousFilter(operator.eq, hazardous)
        
        return CompositeFilter(filters)
    
    @staticmethod
    def create_custom_filter(
        filter_type: str,
        operator_name: str,
        value: Any
    ) -> AttributeFilter:
        """
        Create a custom filter with specified type and operator.
        
        Args:
            filter_type: Type of filter ('date', 'distance', 'velocity', 'diameter', 'hazardous')
            operator_name: Name of the operator ('eq', 'ne', 'lt', 'le', 'gt', 'ge')
            value: The reference value
            
        Returns:
            An AttributeFilter instance
            
        Raises:
            FilterError: If filter type or operator is not supported
        """
        # Map operator names to operator functions
        operators = {
            'eq': operator.eq,
            'ne': operator.ne,
            'lt': operator.lt,
            'le': operator.le,
            'gt': operator.gt,
            'ge': operator.ge
        }
        
        if operator_name not in operators:
            raise FilterError(f"Unsupported operator: {operator_name}")
        
        op = operators[operator_name]
        
        # Map filter types to filter classes
        filter_classes = {
            'date': DateFilter,
            'distance': DistanceFilter,
            'velocity': VelocityFilter,
            'diameter': DiameterFilter,
            'hazardous': HazardousFilter
        }
        
        if filter_type not in filter_classes:
            raise FilterError(f"Unsupported filter type: {filter_type}")
        
        filter_class = filter_classes[filter_type]
        return filter_class(op, value)


def limit(iterator, n: Optional[int] = None):
    """
    Limit the number of values produced by an iterator.
    
    Args:
        iterator: An iterator of values
        n: The maximum number of values to produce
        
    Yields:
        The first (at most) n values from the iterator
    """
    if n is None or n <= 0:
        yield from iterator
    else:
        count = 0
        for item in iterator:
            if count >= n:
                break
            yield item
            count += 1 