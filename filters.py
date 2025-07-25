"""
Filters for querying close approaches.

This module provides filtering capabilities for querying close approaches
based on various criteria.
"""

import operator
from typing import Optional, List
from datetime import date
import itertools


class UnsupportedCriterionError(NotImplementedError):
    """A filter criterion is unsupported."""
    pass


class AttributeFilter:
    """
    A general-purpose filter for comparable attributes.
    
    An AttributeFilter represents search criteria comparing some attribute
    of a close approach (or its attached NEO) to a reference value.
    """
    
    def __init__(self, op, value):
        """
        Initialize the filter with an operator and reference value.
        
        Args:
            op: A 2-argument predicate comparator (such as operator.le)
            value: The reference value to compare against
        """
        self.op = op
        self.value = value
    
    def __call__(self, approach):
        """
        Apply the filter to a close approach.
        
        Args:
            approach: The close approach to filter
            
        Returns:
            True if the approach matches the filter criteria
        """
        return self.op(self.get(approach), self.value)
    
    @classmethod
    def get(cls, approach):
        """
        Get the attribute value from a close approach.
        
        Args:
            approach: The close approach to extract the attribute from
            
        Returns:
            The attribute value to compare against
        """
        raise UnsupportedCriterionError


class DateFilter(AttributeFilter):
    """Filter for close approach dates."""
    
    @classmethod
    def get(cls, approach):
        """Get the date of the close approach."""
        return approach.date


class DistanceFilter(AttributeFilter):
    """Filter for close approach distances."""
    
    @classmethod
    def get(cls, approach):
        """Get the distance of the close approach."""
        return approach.distance


class VelocityFilter(AttributeFilter):
    """Filter for close approach velocities."""
    
    @classmethod
    def get(cls, approach):
        """Get the velocity of the close approach."""
        return approach.velocity


class DiameterFilter(AttributeFilter):
    """Filter for NEO diameters."""
    
    @classmethod
    def get(cls, approach):
        """Get the diameter of the NEO."""
        return approach.neo.diameter if approach.neo else None


class HazardousFilter(AttributeFilter):
    """Filter for NEO hazardous status."""
    
    @classmethod
    def get(cls, approach):
        """Get the hazardous status of the NEO."""
        return approach.neo.hazardous if approach.neo else False


class CompositeFilter:
    """
    A filter that combines multiple filters.
    
    A CompositeFilter applies multiple filters to a close approach,
    returning True only if all filters pass.
    """
    
    def __init__(self, filters):
        """
        Initialize the composite filter.
        
        Args:
            filters: A list of filters to apply
        """
        self.filters = filters
    
    def __call__(self, approach):
        """
        Apply all filters to a close approach.
        
        Args:
            approach: The close approach to filter
            
        Returns:
            True if the approach passes all filters
        """
        return all(f(approach) for f in self.filters)


def create_filters(date=None, start_date=None, end_date=None,
                   distance_min=None, distance_max=None,
                   velocity_min=None, velocity_max=None,
                   diameter_min=None, diameter_max=None,
                   hazardous=None):
    """
    Create a collection of filters from user-specified criteria.
    
    Args:
        date: A specific date to filter by
        start_date: The start date for a date range
        end_date: The end date for a date range
        distance_min: Minimum distance in astronomical units
        distance_max: Maximum distance in astronomical units
        velocity_min: Minimum velocity in km/s
        velocity_max: Maximum velocity in km/s
        diameter_min: Minimum diameter in kilometers
        diameter_max: Maximum diameter in kilometers
        hazardous: Whether to filter by hazardous status
        
    Returns:
        A CompositeFilter containing all the specified filters
    """
    filters = []
    
    # Date filters
    if date is not None:
        filters.append(DateFilter(operator.eq, date))
    if start_date is not None:
        filters.append(DateFilter(operator.ge, start_date))
    if end_date is not None:
        filters.append(DateFilter(operator.le, end_date))
    
    # Distance filters
    if distance_min is not None:
        filters.append(DistanceFilter(operator.ge, distance_min))
    if distance_max is not None:
        filters.append(DistanceFilter(operator.le, distance_max))
    
    # Velocity filters
    if velocity_min is not None:
        filters.append(VelocityFilter(operator.ge, velocity_min))
    if velocity_max is not None:
        filters.append(VelocityFilter(operator.le, velocity_max))
    
    # Diameter filters
    if diameter_min is not None:
        filters.append(DiameterFilter(operator.ge, diameter_min))
    if diameter_max is not None:
        filters.append(DiameterFilter(operator.le, diameter_max))
    
    # Hazardous filter
    if hazardous is not None:
        filters.append(HazardousFilter(operator.eq, hazardous))
    
    return CompositeFilter(filters)


def limit(iterator, n=None):
    """
    Limit the number of items produced by an iterator.
    
    Args:
        iterator: An iterable to limit
        n: The maximum number of items to produce (None for no limit)
        
    Yields:
        At most n items from the iterator
    """
    if n is None or n <= 0:
        yield from iterator
    else:
        yield from itertools.islice(iterator, n) 