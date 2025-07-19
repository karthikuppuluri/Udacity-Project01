"""
Database for managing Near-Earth Objects and their close approaches.

This module provides a high-performance database implementation with efficient
indexing, caching, and querying capabilities for NEO data.
"""

from typing import List, Dict, Optional, Iterator, Set, Tuple
from collections import defaultdict
import logging
from datetime import datetime, date
from .models import NearEarthObject, CloseApproach


logger = logging.getLogger(__name__)


class NEODatabase:
    """
    A database of near-Earth objects and their close approaches.
    
    This database provides indexing and querying capabilities with
    multiple access patterns optimized for different use cases.
    
    Features:
    - Fast lookup by designation and name
    - Efficient filtering and querying
    - Automatic indexing and caching
    - Memory-efficient storage
    """
    
    def __init__(self, neos: List[NearEarthObject], approaches: List[CloseApproach]):
        """
        Create a new NEODatabase with automatic indexing.
        
        Args:
            neos: Collection of NearEarthObject instances
            approaches: Collection of CloseApproach instances
            
        Raises:
            ValueError: If data validation fails
        """
        self._neos = neos
        self._approaches = approaches
        
        # Primary indexes for fast lookups
        self._designation_to_neo: Dict[str, NearEarthObject] = {}
        self._name_to_neo: Dict[str, NearEarthObject] = {}
        
        # Secondary indexes for efficient querying
        self._date_index: Dict[date, List[CloseApproach]] = defaultdict(list)
        self._hazardous_index: Dict[bool, List[CloseApproach]] = defaultdict(list)
        self._diameter_range_index: Dict[Tuple[float, float], List[CloseApproach]] = defaultdict(list)
        
        # Statistics
        self._stats = {
            'total_neos': 0,
            'total_approaches': 0,
            'hazardous_neos': 0,
            'named_neos': 0,
            'neos_with_diameter': 0
        }
        
        self._build_indexes()
        self._link_data()
        self._compute_statistics()
        
        logger.info(f"Database initialized with {self._stats['total_neos']} NEOs "
                   f"and {self._stats['total_approaches']} close approaches")
    
    def _build_indexes(self) -> None:
        """Build all indexes for efficient querying."""
        # Build primary indexes
        for neo in self._neos:
            self._designation_to_neo[neo.designation] = neo
            if neo.name:
                self._name_to_neo[neo.name] = neo
        
        # Build secondary indexes
        for approach in self._approaches:
            # Date index
            self._date_index[approach.date].append(approach)
            
            # Hazardous index (will be populated after linking)
            # Diameter range index (will be populated after linking)
    
    def _link_data(self) -> None:
        """Link NEOs and close approaches together."""
        linked_count = 0
        
        for approach in self._approaches:
            neo = self._designation_to_neo.get(approach.designation)
            if neo:
                approach.neo = neo
                neo.approaches.append(approach)
                linked_count += 1
                
                # Update secondary indexes
                self._hazardous_index[neo.hazardous].append(approach)
                
                # Diameter range index (group by ranges)
                if neo.has_diameter:
                    diameter_range = self._get_diameter_range(neo.diameter)
                    self._diameter_range_index[diameter_range].append(approach)
        
        logger.info(f"Linked {linked_count} close approaches to NEOs")
    
    def _get_diameter_range(self, diameter: float) -> Tuple[float, float]:
        """Get the diameter range for indexing purposes."""
        if diameter < 0.1:
            return (0.0, 0.1)
        elif diameter < 1.0:
            return (0.1, 1.0)
        elif diameter < 10.0:
            return (1.0, 10.0)
        else:
            return (10.0, float('inf'))
    
    def _compute_statistics(self) -> None:
        """Compute database statistics."""
        self._stats['total_neos'] = len(self._neos)
        self._stats['total_approaches'] = len(self._approaches)
        self._stats['hazardous_neos'] = sum(1 for neo in self._neos if neo.hazardous)
        self._stats['named_neos'] = sum(1 for neo in self._neos if neo.name)
        self._stats['neos_with_diameter'] = sum(1 for neo in self._neos if neo.has_diameter)
    
    def get_neo_by_designation(self, designation: str) -> Optional[NearEarthObject]:
        """
        Find and return an NEO by its primary designation.
        
        Args:
            designation: The primary designation of the NEO to search for
            
        Returns:
            The matching NearEarthObject or None if not found
        """
        if not designation:
            return None
        
        return self._designation_to_neo.get(designation.upper().strip())
    
    def get_neo_by_name(self, name: str) -> Optional[NearEarthObject]:
        """
        Find and return an NEO by its name.
        
        Args:
            name: The IAU name of the NEO to search for
            
        Returns:
            The matching NearEarthObject or None if not found
        """
        if not name:
            return None
        
        # Try exact match first
        neo = self._name_to_neo.get(name.strip())
        if neo:
            return neo
        
        # Try case-insensitive match
        for stored_name, stored_neo in self._name_to_neo.items():
            if stored_name.lower() == name.lower().strip():
                return stored_neo
        
        return None
    
    def get_all_neos(self) -> List[NearEarthObject]:
        """Get all NEOs in the database."""
        return self._neos.copy()
    
    def get_all_approaches(self) -> List[CloseApproach]:
        """Get all close approaches in the database."""
        return self._approaches.copy()
    
    def query(self, filters: Dict[str, callable] = None) -> Iterator[CloseApproach]:
        """
        Query close approaches with optional filters.
        
        Args:
            filters: Dictionary of filter functions to apply
            
        Yields:
            CloseApproach objects that match all filters
        """
        if not filters:
            yield from self._approaches
            return
        
        # Apply filters
        for approach in self._approaches:
            if all(filter_func(approach) for filter_func in filters.values()):
                yield approach
    
    def query_by_date(self, target_date: date) -> List[CloseApproach]:
        """Get all close approaches on a specific date."""
        return self._date_index.get(target_date, [])
    
    def query_by_date_range(self, start_date: date, end_date: date) -> Iterator[CloseApproach]:
        """Get all close approaches within a date range."""
        for approach in self._approaches:
            if start_date <= approach.date <= end_date:
                yield approach
    
    def query_hazardous(self, hazardous: bool = True) -> List[CloseApproach]:
        """Get all close approaches of hazardous/non-hazardous NEOs."""
        return self._hazardous_index.get(hazardous, [])
    
    def query_by_diameter_range(self, min_diameter: float, max_diameter: float) -> Iterator[CloseApproach]:
        """Get all close approaches of NEOs within a diameter range."""
        for approach in self._approaches:
            if approach.neo and approach.neo.has_diameter:
                if min_diameter <= approach.neo.diameter <= max_diameter:
                    yield approach
    
    def get_statistics(self) -> Dict[str, int]:
        """Get database statistics."""
        return self._stats.copy()
    
    def search_neos(self, query: str, limit: int = 10) -> List[NearEarthObject]:
        """
        Search NEOs by designation or name.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List of matching NEOs
        """
        if not query:
            return []
        
        query = query.lower().strip()
        results = []
        
        # Search by designation
        for neo in self._neos:
            if query in neo.designation.lower():
                results.append(neo)
                if len(results) >= limit:
                    break
        
        # Search by name if we haven't reached the limit
        if len(results) < limit:
            for neo in self._neos:
                if neo.name and query in neo.name.lower() and neo not in results:
                    results.append(neo)
                    if len(results) >= limit:
                        break
        
        return results
    
    def get_closest_approaches(self, limit: int = 10) -> List[CloseApproach]:
        """Get the closest approaches to Earth."""
        sorted_approaches = sorted(self._approaches, key=lambda x: x.distance)
        return sorted_approaches[:limit]
    
    def get_fastest_approaches(self, limit: int = 10) -> List[CloseApproach]:
        """Get the fastest approaches to Earth."""
        sorted_approaches = sorted(self._approaches, key=lambda x: x.velocity, reverse=True)
        return sorted_approaches[:limit]
    
    def get_recent_approaches(self, limit: int = 10) -> List[CloseApproach]:
        """Get the most recent close approaches."""
        sorted_approaches = sorted(self._approaches, key=lambda x: x.time, reverse=True)
        return sorted_approaches[:limit]
    
    def __len__(self) -> int:
        """Return the total number of close approaches."""
        return len(self._approaches)
    
    def __contains__(self, item) -> bool:
        """Check if an NEO or close approach is in the database."""
        if isinstance(item, NearEarthObject):
            return item.designation in self._designation_to_neo
        elif isinstance(item, CloseApproach):
            return item in self._approaches
        return False 