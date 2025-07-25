"""
Database for managing Near-Earth Objects and their close approaches.

This module provides a database implementation for NEO data with querying capabilities.
"""

from typing import List, Optional, Iterator
from models import NearEarthObject, CloseApproach


class NEODatabase:
    """
    A database of near-Earth objects and their close approaches.
    
    This database provides indexing and querying capabilities for NEO data.
    """
    
    def __init__(self, neos, approaches):
        """
        Create a new NEODatabase.
        
        Args:
            neos: Collection of NearEarthObject instances
            approaches: Collection of CloseApproach instances
        """
        self._neos = neos
        self._approaches = approaches
        
        # Build indexes for fast lookups
        self._designation_to_neo = {}
        self._name_to_neo = {}
        
        # Link NEOs and close approaches
        self._link_data()
        self._build_indexes()
    
    def _link_data(self):
        """Link NEOs and close approaches together."""
        for approach in self._approaches:
            # Find the corresponding NEO
            neo = self._find_neo_by_designation(approach._designation)
            if neo:
                approach.neo = neo
                neo.approaches.append(approach)
    
    def _find_neo_by_designation(self, designation):
        """Find a NEO by its designation."""
        for neo in self._neos:
            if neo.designation == designation:
                return neo
        return None
    
    def _build_indexes(self):
        """Build indexes for fast lookups."""
        for neo in self._neos:
            # Index by designation
            self._designation_to_neo[neo.designation] = neo
            
            # Index by name (if present)
            if neo.name:
                self._name_to_neo[neo.name] = neo
    
    def get_neo_by_designation(self, designation):
        """
        Find and return an NEO by its primary designation.
        
        Args:
            designation: The primary designation of the NEO to search for.
            
        Returns:
            The corresponding NearEarthObject, or None if not found.
        """
        return self._designation_to_neo.get(designation)
    
    def get_neo_by_name(self, name):
        """
        Find and return an NEO by its IAU name.
        
        Args:
            name: The IAU name of the NEO to search for.
            
        Returns:
            The corresponding NearEarthObject, or None if not found.
        """
        return self._name_to_neo.get(name)
    
    def query(self, filters=None):
        """
        Query close approaches with the given filters.
        
        Args:
            filters: A collection of filters to apply to the close approaches.
            
        Yields:
            CloseApproach objects that match the filters.
        """
        for approach in self._approaches:
            if filters is None or filters(approach):
                yield approach 